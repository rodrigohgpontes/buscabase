"""Ingere releases etiquetadas do bncc-dados e atualiza vetores desatualizados."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tarfile
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy import select, text

from app.config import settings
from app.db import SessionLocal, engine
from app.ml import embed_texts_sync
from app.models import (
    AlinhamentoEI,
    Area,
    Componente,
    Contexto,
    Documento,
    Etapa,
    Item,
    Recorte,
    Snapshot,
)
from app.cache import cache_delete_prefix

SCHEMA_MAJOR = re.compile(r"^schema-v([0-9]+)")


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = (
        value.replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "item"


def sha_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def download_snapshot(tag: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / f"{tag}.tar.gz"
    url = f"https://github.com/{settings.bncc_dados_owner}/{settings.bncc_dados_repo}/archive/refs/tags/{tag}.tar.gz"
    if not archive.exists():
        with urlopen(url) as response, open(archive, "wb") as handle:
            shutil.copyfileobj(response, handle)
    extract_dir = dest / tag
    if extract_dir.exists():
        return _find_root(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(extract_dir, filter="data")
    return _find_root(extract_dir)


def _find_root(extract_dir: Path) -> Path:
    for child in extract_dir.iterdir():
        if child.is_dir() and (child / "dados").exists():
            return child
    raise FileNotFoundError(f"snapshot sem pasta dados em {extract_dir}")


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_major_from_tag_tree(root: Path) -> str:
    schema_dir = root / "schema"
    if not schema_dir.exists():
        return "unknown"
    versions = []
    for path in schema_dir.glob("*.json"):
        versions.append(path.name)
    return ",".join(sorted(versions)[:8]) or "present"


def halt_on_schema_major(root: Path) -> None:
    version_file = root / "schema" / "VERSION"
    if version_file.exists():
        text_value = version_file.read_text(encoding="utf-8").strip()
        if re.match(r"^2\.", text_value):
            raise SystemExit(f"schema major incompatível: {text_value}")


def resolve_nome(maps: dict[str, str], ref: str | None) -> str | None:
    if not ref:
        return None
    return maps.get(ref, ref)


def build_maps(estrutura: dict, contextos: list[dict], computacao: dict | None) -> dict[str, str]:
    names: dict[str, str] = {}
    for key in (
        "etapas",
        "areas_conhecimento",
        "componentes_curriculares",
        "recortes_temporais",
        "campos_experiencias",
        "competencias_gerais",
        "competencias_especificas",
        "documento_curricular",
    ):
        for row in estrutura.get(key, []) or []:
            ident = row.get("id")
            nome = row.get("nome") or row.get("texto")
            if ident and nome:
                names[ident] = nome if isinstance(nome, str) else str(nome)[:80]
    for row in contextos:
        ident = row.get("id")
        nome = row.get("nome")
        if ident and nome:
            names[ident] = nome
    if computacao:
        for group in ("eixos", "objetos_conhecimento", "competencias"):
            for row in computacao.get(group, []) or []:
                ident = row.get("id")
                nome = row.get("nome") or row.get("texto")
                if ident and nome:
                    names[ident] = nome if isinstance(nome, str) else str(nome)[:80]
    return names


def pagina_from_fonte(fonte: dict | None) -> str | None:
    if not fonte:
        return None
    locator = fonte.get("localizador_pdf") or fonte.get("localizador")
    return locator


def url_path_for(tipo: str, codigo: str) -> str:
    if tipo == "habilidade":
        return f"/habilidade/{codigo}"
    if tipo in {"objetivo", "objetivo_aprendizagem"}:
        return f"/aprendizagem/{codigo}"
    if tipo.startswith("competencia"):
        return f"/competencia/{codigo}"
    return f"/aprendizagem/{codigo}"


def etapa_from_codigo_or_row(row: dict, fallback: str | None) -> str | None:
    if fallback:
        return fallback
    codigo = row.get("codigo") or ""
    if codigo.startswith("EI"):
        return "EI"
    if codigo.startswith("EF"):
        return "EF"
    if codigo.startswith("EM"):
        return "EM"
    return None


def unidade_from_row(row: dict, names: dict[str, str]) -> str | None:
    if row.get("campo_experiencias"):
        return names.get(row["campo_experiencias"], row["campo_experiencias"])
    org = row.get("organizacao") or {}
    if isinstance(org, dict):
        nomes = org.get("nomes") or {}
        if nomes.get("unidadeTematica"):
            return nomes["unidadeTematica"]
        if org.get("unidade_tematica"):
            return names.get(org["unidade_tematica"], org["unidade_tematica"])
        campos = org.get("campos_atuacao") or []
        if campos:
            return names.get(campos[0], campos[0])
        if org.get("eixo"):
            return names.get(org["eixo"], org["eixo"])
    if row.get("eixo"):
        return names.get(row["eixo"], row["eixo"])
    return None


def objetos_from_row(row: dict, names: dict[str, str]) -> list[dict]:
    refs = row.get("objetos_conhecimento") or row.get("objetosConhecimento") or []
    out = []
    for ref in refs:
        if isinstance(ref, dict):
            out.append({"id": ref.get("id") or ref.get("nome"), "nome": ref.get("nome")})
        else:
            out.append({"id": ref, "nome": names.get(ref, ref)})
    return out


def resolve_componente_id(row: dict) -> str | None:
    raw = row.get("componente")
    if isinstance(raw, dict):
        raw = raw.get("id") or raw.get("sigla") or raw.get("sigla_codigo")
    if isinstance(raw, str):
        key = raw.strip()
        folded = key.lower().replace("ç", "c")
        if key.upper() in {"CO"} or key in {"co-comp", "computacao"} or folded == "computacao":
            return "co-comp"
        if key:
            return key
    codigo = str(row.get("codigo") or row.get("id") or "")
    if re.match(r"^(EI03CO|EF\d{2}CO|EM13CO)", codigo.upper()):
        return "co-comp"
    return None


def upsert_item(db, row: dict, *, tipo: str, etapa: str | None, names: dict[str, str], tag: str) -> tuple[Item, bool]:
    codigo = row["codigo"] if "codigo" in row else row["id"]
    texto = row["texto"]
    texto_hash = sha_text(texto)
    existing = db.get(Item, codigo)
    fonte = row.get("fonte") or {"documento": row.get("documento")}
    vigencia = row.get("vigencia") or {"status": "vigente", "desde": tag, "ate": None}
    componente_id = resolve_componente_id(row)
    area_id = row.get("area") if isinstance(row.get("area"), str) else None
    recorte_id = row.get("grupo_etario") if isinstance(row.get("grupo_etario"), str) else None
    etapa_id = etapa_from_codigo_or_row(row, etapa)
    anos = row.get("anos")
    if area_id is None and componente_id:
        comp = db.get(Componente, componente_id)
        if comp is not None and comp.area_id:
            area_id = comp.area_id
    if recorte_id is None and isinstance(anos, list) and len(anos) == 1 and etapa_id:
        rec = db.execute(
            select(Recorte).where(
                Recorte.etapa_id == etapa_id,
                Recorte.tipo == "ano",
                Recorte.anos.overlap(anos),
            )
        ).scalars().first()
        if rec is not None:
            recorte_id = rec.id
    if recorte_id is None and not anos and etapa_id == "EM":
        rec = db.execute(
            select(Recorte).where(Recorte.etapa_id == "EM", Recorte.tipo == "sem_seriacao")
        ).scalars().first()
        if rec is not None:
            recorte_id = rec.id
    changed = existing is None or existing.texto_hash != texto_hash or existing.payload != row
    item = existing or Item(codigo=codigo)
    item.tipo = tipo
    item.documento_id = row.get("documento") or (fonte.get("documento") if isinstance(fonte, dict) else None) or "bncc-2018"
    item.etapa = etapa_id
    item.texto = texto
    item.texto_hash = texto_hash
    item.anos = row.get("anos")
    item.componente_id = componente_id
    item.area_id = area_id
    item.recorte_id = recorte_id
    item.unidade_ou_campo = unidade_from_row(row, names)
    item.objetos = objetos_from_row(row, names)
    item.vigencia_status = vigencia.get("status") or "vigente"
    item.vigencia_desde = vigencia.get("desde")
    item.vigencia_ate = vigencia.get("ate")
    item.fonte = fonte
    item.pagina_pdf = pagina_from_fonte(fonte if isinstance(fonte, dict) else None)
    item.url_path = url_path_for(tipo, codigo)
    item.data_version = tag
    item.payload = row
    db.merge(item)
    return item, changed


def recorte_nome(row: dict) -> str:
    if row.get("nome"):
        return row["nome"]
    numero = row.get("numero")
    if row.get("tipo") == "ano" and numero is not None:
        return f"{numero}º ano"
    if row.get("tipo") == "sem_seriacao":
        return "Sem seriação"
    return row["id"]


def load_taxonomies(db, estrutura: dict, tag: str) -> None:
    for row in estrutura.get("documento_curricular") or []:
        db.merge(
            Documento(
                id=row["id"],
                nome=row["nome"],
                tipo=row.get("tipo") or "documento",
                esfera=row.get("esfera"),
                derivado_de=row.get("derivado_de"),
                slug=slugify(row["id"]),
                data_version=tag,
                payload=row,
            )
        )
    for row in estrutura.get("etapas") or []:
        db.merge(
            Etapa(
                id=row["id"],
                nome=row["nome"],
                slug=slugify(row.get("id") or row["nome"]),
                payload=row,
            )
        )
    for row in estrutura.get("areas_conhecimento") or []:
        db.merge(
            Area(
                id=row["id"],
                etapa_id=row.get("etapa"),
                nome=row["nome"],
                slug=slugify(row["id"]),
                documento_id=row.get("documento"),
                payload=row,
            )
        )
    for row in estrutura.get("componentes_curriculares") or []:
        db.merge(
            Componente(
                id=row["id"],
                etapa_id=row.get("etapa"),
                area_id=row.get("area"),
                nome=row["nome"],
                sigla=row.get("sigla_codigo"),
                slug=slugify(row["id"]),
                documento_id=row.get("documento"),
                payload=row,
            )
        )
    for row in estrutura.get("recortes_temporais") or []:
        db.merge(
            Recorte(
                id=row["id"],
                etapa_id=row.get("etapa"),
                tipo=row.get("tipo") or "recorte",
                nome=recorte_nome(row),
                faixa=row.get("faixa"),
                slug=slugify(row["id"]),
                anos=row.get("anos") or _anos_from_faixa(row),
                payload=row,
            )
        )


def _anos_from_faixa(row: dict) -> list[int] | None:
    if row.get("tipo") == "ano" and row.get("numero") is not None:
        return [int(row["numero"])]
    nome = row.get("nome") or ""
    m = re.search(r"(\d+)", nome)
    if m and row.get("tipo") == "ano":
        return [int(m.group(1))]
    return None


def load_competencias(db, estrutura: dict, tag: str, names: dict[str, str]) -> list[str]:
    changed_ids: list[str] = []
    for row in estrutura.get("competencias_gerais") or []:
        row = {**row, "codigo": row["id"]}
        _, changed = upsert_item(db, row, tipo="competencia_geral", etapa=None, names=names, tag=tag)
        if changed:
            changed_ids.append(row["id"])
    for row in estrutura.get("competencias_especificas") or []:
        row = {**row, "codigo": row["id"]}
        _, changed = upsert_item(db, row, tipo="competencia_especifica", etapa=row.get("etapa"), names=names, tag=tag)
        if changed:
            changed_ids.append(row["id"])
    return changed_ids


def write_catalog(db, tag: str) -> None:
    dest = Path(settings.bncc_catalog_dir)
    dest.mkdir(parents=True, exist_ok=True)
    items = list(db.execute(select(Item)).scalars())
    documentos = list(db.execute(select(Documento)).scalars())
    etapas = list(db.execute(select(Etapa)).scalars())
    areas = list(db.execute(select(Area)).scalars())
    componentes = list(db.execute(select(Componente)).scalars())
    recortes = list(db.execute(select(Recorte)).scalars())
    catalog = {
        "recorte": tag,
        "origin": settings.public_origin,
        "items": [
            {
                "codigo": item.codigo,
                "tipo": item.tipo,
                "url_path": item.url_path,
                "etapa": item.etapa,
                "componente_id": item.componente_id,
                "area_id": item.area_id,
                "recorte_id": item.recorte_id,
                "documento_id": item.documento_id,
                "vigencia_status": item.vigencia_status,
            }
            for item in items
        ],
        "documentos": [{"id": d.id, "slug": d.slug, "nome": d.nome} for d in documentos],
        "etapas": [{"id": e.id, "slug": e.slug, "nome": e.nome} for e in etapas],
        "areas": [{"id": a.id, "slug": a.slug, "nome": a.nome, "etapa_id": a.etapa_id} for a in areas],
        "componentes": [
            {"id": c.id, "slug": c.slug, "nome": c.nome, "etapa_id": c.etapa_id} for c in componentes
        ],
        "recortes": [
            {"id": r.id, "slug": r.slug, "nome": r.nome, "etapa_id": r.etapa_id, "tipo": r.tipo}
            for r in recortes
        ],
    }
    (dest / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")


def embed_changed(db, codigos: list[str]) -> int:
    if not codigos:
        return 0
    if not settings.cloud_key(settings.embedding_api_key):
        print("OPENROUTER_API_KEY/EMBEDDING_API_KEY ausente: itens salvos sem vetor. Buscar lexical continua disponível.")
        return 0
    batch_size = max(1, settings.embedding_batch_size)
    embedded = 0
    for start in range(0, len(codigos), batch_size):
        chunk = codigos[start : start + batch_size]
        items = [db.get(Item, codigo) for codigo in chunk]
        items = [item for item in items if item is not None]
        texts = [f"{item.codigo}. {item.texto}" for item in items]
        try:
            vectors = embed_texts_sync(texts)
        except Exception as exc:
            print(f"embeddings falharam neste lote: {exc}")
            continue
        for item, vector in zip(items, vectors, strict=True):
            item.embedding = vector
            item.embedding_model = settings.embedding_model
            embedded += 1
        db.commit()
    return embedded


def embedding_candidates(db, changed: list[str]) -> list[str]:
    candidates = set(changed)
    for item in db.execute(select(Item)).scalars():
        if item.embedding is None or item.embedding_model != settings.embedding_model:
            candidates.add(item.codigo)
    return sorted(candidates)


def apply_snapshot(tag: str | None = None) -> None:
    tag = tag or settings.bncc_dados_tag
    root = download_snapshot(tag, Path(settings.bncc_snapshot_dir))
    halt_on_schema_major(root)
    dados = root / "dados"
    estrutura = None
    contextos: list[dict] = []
    computacao = None
    ei = None
    ef = None
    em = None
    for doc_dir in sorted(p for p in dados.iterdir() if p.is_dir()):
        for json_file in sorted(doc_dir.glob("*.json")):
            payload = read_json(json_file)
            name = json_file.name
            if name == "estrutura.json":
                estrutura = payload
            elif name == "ensino-fundamental.json":
                ef = payload
                contextos.extend(payload.get("contextos_organizacao") or [])
            elif name == "ensino-medio.json":
                em = payload
                contextos.extend(payload.get("contextos_organizacao") or [])
            elif name == "educacao-infantil.json":
                ei = payload
            elif name == "computacao.json":
                computacao = payload
    if estrutura is None:
        raise SystemExit("estrutura.json ausente no snapshot")

    names = build_maps(estrutura, contextos, computacao)
    db = SessionLocal()
    changed: list[str] = []
    try:
        load_taxonomies(db, estrutura, tag)
        if computacao:
            db.merge(
                Componente(
                    id="co-comp",
                    etapa_id=None,
                    area_id=None,
                    nome="Computação",
                    sigla="CO",
                    slug="computacao",
                    documento_id="computacao-2022",
                    payload={"id": "co-comp", "nome": "Computação", "sigla_codigo": "CO"},
                )
            )
        for ctx in contextos:
            db.merge(
                Contexto(
                    id=ctx["id"],
                    tipo=ctx.get("tipo") or "contexto",
                    nome=ctx.get("nome") or ctx["id"],
                    componente_id=ctx.get("componente"),
                    payload=ctx,
                )
            )
        changed.extend(load_competencias(db, estrutura, tag, names))
        if ei:
            for row in ei.get("objetivos") or []:
                _, did = upsert_item(db, row, tipo="objetivo", etapa="EI", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
            for row in ei.get("alinhamentos") or []:
                db.merge(
                    AlinhamentoEI(
                        id=row.get("id") or sha_text(json.dumps(row, sort_keys=True)),
                        payload=row,
                        codigos=row.get("objetivos") or row.get("codigos") or [],
                    )
                )
        if ef:
            for row in ef.get("habilidades") or []:
                _, did = upsert_item(db, row, tipo="habilidade", etapa="EF", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
        if em:
            for row in em.get("habilidades") or []:
                _, did = upsert_item(db, row, tipo="habilidade", etapa="EM", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
        if computacao:
            for row in computacao.get("objetivos_ei") or []:
                _, did = upsert_item(db, row, tipo="objetivo", etapa="EI", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
            for row in computacao.get("habilidades_ef") or []:
                _, did = upsert_item(db, row, tipo="habilidade", etapa="EF", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
            for row in computacao.get("habilidades_em") or []:
                _, did = upsert_item(db, row, tipo="habilidade", etapa="EM", names=names, tag=tag)
                if did:
                    changed.append(row["codigo"])
            for row in computacao.get("competencias") or []:
                row = {**row, "codigo": row["id"]}
                _, did = upsert_item(
                    db,
                    row,
                    tipo="competencia_geral" if "cg" in row["id"] else "competencia_especifica",
                    etapa=None,
                    names=names,
                    tag=tag,
                )
                if did:
                    changed.append(row["id"])
        db.commit()
        embedding_ids = embedding_candidates(db, changed)
        embedded_count = embed_changed(db, embedding_ids)
        try:
            db.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_items_embedding ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)"
                )
            )
            db.commit()
        except Exception:
            db.rollback()
        count = db.execute(select(Item)).scalars().all()
        for snap in db.execute(select(Snapshot)).scalars():
            snap.active = False
        db.merge(
            Snapshot(
                tag=tag,
                schema_version=schema_major_from_tag_tree(root),
                embedding_model=settings.embedding_model,
                embedding_dimension=settings.embedding_dimension,
                item_count=len(count),
                changelog_category="correcao",
                active=True,
            )
        )
        db.commit()
        write_catalog(db, tag)
        cache_delete_prefix("buscar")
        cache_delete_prefix("buscar.v2")
        cache_delete_prefix("perguntar")
        print(f"Ingestão {tag}: {len(count)} itens, {embedded_count} vetores atualizados")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--tag", default=None)
    args = parser.parse_args()
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    if args.apply:
        apply_snapshot(args.tag)


if __name__ == "__main__":
    main()
