"""Load extracted prose JSON into Postgres and publish Arte in documentos."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select, text

from app.config import settings
from app.db import SessionLocal
from app.ingest import sha_text, write_catalog
from app.ml import embed_texts_sync
from app.models import Documento, ProseBlock, ProseDocument, ProsePage, Snapshot
from app.prose import is_embeddable_block, prose_embed_text, restored_embedding

ARTE_ID = "arte-2026"
ARTE_DOCUMENTO = {
    "id": ARTE_ID,
    "slug": ARTE_ID,
    "nome": "Normas complementares à BNCC — Arte (Parecer CNE/CEB nº 2/2026)",
    "tipo": "complemento",
    "esfera": "nacional",
    "derivado_de": "bncc-2018",
    "data_version": "local-pceb002-26",
}


def default_prose_dir() -> Path:
    return Path(settings.bncc_prose_dir)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_embeddings(db, documento_id: str) -> dict[str, tuple[str | None, object, str | None]]:
    rows = db.execute(
        select(
            ProseBlock.id,
            ProseBlock.texto_hash,
            ProseBlock.embedding,
            ProseBlock.embedding_model,
        ).where(ProseBlock.documento_id == documento_id)
    ).all()
    return {row.id: (row.texto_hash, row.embedding, row.embedding_model) for row in rows}


def replace_document(db, payload: dict) -> tuple[int, int]:
    documento_id = payload["documento_id"]
    extracted = payload.get("extracted_at")
    if isinstance(extracted, str):
        try:
            extracted_at = datetime.fromisoformat(extracted.replace("Z", "+00:00"))
        except ValueError:
            extracted_at = datetime.now(timezone.utc)
    else:
        extracted_at = datetime.now(timezone.utc)

    previous = snapshot_embeddings(db, documento_id)
    db.execute(delete(ProseBlock).where(ProseBlock.documento_id == documento_id))
    db.execute(delete(ProsePage).where(ProsePage.documento_id == documento_id))
    db.execute(delete(ProseDocument).where(ProseDocument.id == documento_id))
    db.flush()
    db.add(
        ProseDocument(
            id=documento_id,
            arquivo=payload["arquivo"],
            sha256=payload["sha256"],
            page_count=payload["page_count"],
            data_version=payload.get("data_version") or "",
            extracted_at=extracted_at,
        )
    )
    db.flush()
    pages = payload.get("pages") or []
    block_count = 0
    for page in pages:
        db.add(
            ProsePage(
                documento_id=documento_id,
                page=page["page"],
                width=page["width"],
                height=page["height"],
            )
        )
        for seq, block in enumerate(page.get("blocks") or [], start=1):
            text_value = block.get("text") or ""
            texto_hash = sha_text(text_value)
            embedding, embedding_model = restored_embedding(previous, block["id"], texto_hash)
            db.add(
                ProseBlock(
                    id=block["id"],
                    documento_id=documento_id,
                    page=page["page"],
                    seq=seq,
                    type=block["type"],
                    text=text_value,
                    raw_lines=block.get("raw_lines") or [],
                    bbox=block.get("bbox") or [0, 0, 0, 0],
                    font_size=block.get("font_size"),
                    font_name=block.get("font_name"),
                    item_codigo=block.get("item_codigo"),
                    texto_hash=texto_hash,
                    embedding=embedding,
                    embedding_model=embedding_model,
                )
            )
            block_count += 1
    return len(pages), block_count


def prose_embedding_candidates(db) -> list[ProseBlock]:
    out: list[ProseBlock] = []
    for block in db.execute(select(ProseBlock)).scalars():
        if not is_embeddable_block(block.type, block.text):
            continue
        if block.embedding is None or block.embedding_model != settings.embedding_model:
            out.append(block)
    return out


def embed_changed_prose(db) -> int:
    candidates = prose_embedding_candidates(db)
    if not candidates:
        return 0
    if not settings.cloud_key(settings.embedding_api_key):
        print(
            "OPENROUTER_API_KEY/EMBEDDING_API_KEY ausente: blocos de prosa salvos sem vetor. "
            "Busca lexical continua disponível."
        )
        return 0
    batch_size = max(1, settings.embedding_batch_size)
    embedded = 0
    for start in range(0, len(candidates), batch_size):
        chunk = candidates[start : start + batch_size]
        texts = [prose_embed_text(block.documento_id, block.page, block.text) for block in chunk]
        try:
            vectors = embed_texts_sync(texts)
        except Exception as exc:
            print(f"embeddings de prosa falharam neste lote: {exc}")
            continue
        for block, vector in zip(chunk, vectors, strict=True):
            block.embedding = vector
            block.embedding_model = settings.embedding_model
            embedded += 1
        db.commit()
    try:
        db.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prose_blocks_embedding ON prose_blocks "
                "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)"
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    return embedded


def upsert_arte_documento(db, payload: dict) -> None:
    meta = payload.get("validation") or {}
    page_count = payload.get("page_count")
    document_payload = {
        "parecer": "CNE/CEB nº 2/2026",
        "processo": "23001.000221/2022-97",
        "aprovado_em": "2026-03-19",
        "homologacao": "DOU 18/8/2026, Seção 1, pág. 73",
        "arquivo": payload.get("arquivo"),
        "sha256": payload.get("sha256"),
        "page_count": page_count,
        "proveniencia": "research/pceb002_26.pdf",
        "worst_coverage": meta.get("worst_coverage"),
    }
    db.merge(
        Documento(
            id=ARTE_DOCUMENTO["id"],
            nome=ARTE_DOCUMENTO["nome"],
            tipo=ARTE_DOCUMENTO["tipo"],
            esfera=ARTE_DOCUMENTO["esfera"],
            derivado_de=ARTE_DOCUMENTO["derivado_de"],
            slug=ARTE_DOCUMENTO["slug"],
            data_version=ARTE_DOCUMENTO["data_version"],
            payload=document_payload,
        )
    )


def load_dir(prose_dir: Path | None = None) -> dict[str, tuple[int, int]]:
    prose_dir = prose_dir or default_prose_dir()
    db = SessionLocal()
    loaded: dict[str, tuple[int, int]] = {}
    try:
        for path in sorted(prose_dir.glob("*.json")):
            if path.name.startswith("."):
                continue
            payload = load_json(path)
            if "documento_id" not in payload or "pages" not in payload:
                continue
            pages, blocks = replace_document(db, payload)
            if payload["documento_id"] == ARTE_ID:
                upsert_arte_documento(db, payload)
            loaded[payload["documento_id"]] = (pages, blocks)
            expected_pages = payload["page_count"]
            if pages != expected_pages:
                raise SystemExit(f"{payload['documento_id']}: {pages} páginas no DB, JSON tem {expected_pages}")
        db.commit()
        embedded = embed_changed_prose(db)
        if embedded:
            print(f"prosa embeddings: {embedded} blocos")
        snap = db.execute(select(Snapshot).where(Snapshot.active.is_(True))).scalar_one_or_none()
        write_catalog(db, snap.tag if snap else settings.bncc_dados_tag)
    finally:
        db.close()
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=None)
    args = parser.parse_args()
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    loaded = load_dir(args.dir)
    if not loaded:
        raise SystemExit("nenhum JSON de prosa encontrado")
    for documento_id, (pages, blocks) in loaded.items():
        print(f"prosa {documento_id}: {pages} páginas, {blocks} blocos")


if __name__ == "__main__":
    main()
