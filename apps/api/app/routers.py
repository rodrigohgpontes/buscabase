from __future__ import annotations

import csv
import io
import time
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, load_only

from app.cache import cache_get, cache_set
from app.codes import CodeError, alphanumeric_prefix_len, normalize_code
from app.config import settings
from app.db import SessionLocal, get_db
from app.models import Area, Componente, Documento, Etapa, Item, ProseBlock, ProseDocument, ProsePage, Recorte, Snapshot
from app.perguntar import perguntar_disponivel, rate_limit, stream_answer
from app.privacy import client_ip, record_event
from app.recados import (
    criar_recado,
    email_ok,
    listar_recados,
    public_recado,
    recado_rate_ok,
    sanitize_pagina,
)
from app.usage import event_rate_ok, ingest_from_request, require_uso, uso_resumo
from app.prose import STRIP_TYPES
from app.retrieval import (
    SearchFilters,
    has_scope,
    hybrid_search,
    hybrid_search_prose,
    inferred_labels,
    lookup_item,
    recorte_item_clauses,
    related_items,
    suggest_codes,
    wants_prose_strip,
)
from app.serialize import public_item, public_prose_block, public_prose_fonte, suggestion_card

router = APIRouter()


def snapshot_or_503(db: Session) -> Snapshot:
    snap = db.execute(select(Snapshot).where(Snapshot.active.is_(True))).scalar_one_or_none()
    if snap is None:
        raise HTTPException(
            status_code=503,
            detail={
                "titulo": "O recorte ainda não foi carregado.",
                "texto": "A Base ainda está em ingestão. Tente de novo em instantes.",
            },
        )
    return snap


def _tem_aprendizagens(payload: dict | None) -> bool:
    if not isinstance(payload, dict):
        return True
    return payload.get("tem_aprendizagens_proprias") is not False


def _campos_from_items(db: Session) -> list[dict]:
    seen: dict[str, str] = {}
    rows = db.execute(
        select(Item.payload, Item.unidade_ou_campo).where(Item.etapa == "EI", Item.tipo == "objetivo")
    ).all()
    for payload, unidade in rows:
        if not isinstance(payload, dict):
            continue
        campo_id = payload.get("campo_experiencias")
        if not campo_id or campo_id in seen:
            continue
        seen[campo_id] = unidade or campo_id
    return [{"id": campo_id, "nome": nome} for campo_id, nome in seen.items()]


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    snap = db.execute(select(Snapshot).where(Snapshot.active.is_(True))).scalar_one_or_none()
    return {
        "ok": True,
        "recorte": snap.tag if snap else None,
        "item_count": snap.item_count if snap else 0,
        "embedding_model": snap.embedding_model if snap else settings.embedding_model,
        "embedding_dimension": snap.embedding_dimension if snap else settings.embedding_dimension,
        "perguntar": perguntar_disponivel(),
        "generation": bool(settings.cloud_key(settings.generation_api_key)),
        "rerank": bool(settings.cloud_key(settings.rerank_api_key)),
    }


@router.get("/taxonomias")
def taxonomias(db: Session = Depends(get_db)) -> dict:
    snapshot_or_503(db)
    etapas = [{"id": e.id, "nome": e.nome, "slug": e.slug} for e in db.execute(select(Etapa)).scalars()]
    anos = [
        {
            "id": r.id,
            "nome": r.nome,
            "slug": r.slug,
            "etapa": r.etapa_id,
            "tipo": r.tipo,
            "faixa": r.faixa,
            "anos": r.anos,
        }
        for r in db.execute(select(Recorte)).scalars()
    ]
    componentes = [
        {
            "id": c.id,
            "nome": c.nome,
            "slug": c.slug,
            "etapa": c.etapa_id,
            "sigla": c.sigla,
            "area": c.area_id,
            "presenca": (c.payload or {}).get("presenca") if isinstance(c.payload, dict) else None,
            "tem_aprendizagens": _tem_aprendizagens(c.payload),
        }
        for c in db.execute(select(Componente)).scalars()
    ]
    areas = [
        {"id": a.id, "nome": a.nome, "slug": a.slug, "etapa": a.etapa_id}
        for a in db.execute(select(Area)).scalars()
    ]
    documentos = [
        {"id": d.id, "nome": d.nome, "slug": d.slug, "tipo": d.tipo}
        for d in db.execute(select(Documento)).scalars()
    ]
    campos = _campos_from_items(db)
    tipos = [
        {"id": "habilidade", "nome": "Habilidade"},
        {"id": "objetivo", "nome": "Objetivo de aprendizagem e desenvolvimento"},
        {"id": "competencia_geral", "nome": "Competência geral"},
        {"id": "competencia_especifica", "nome": "Competência específica"},
    ]
    competencias = [
        {"id": item.codigo, "nome": item.texto, "tipo": item.tipo}
        for item in db.execute(
            select(Item)
            .where(Item.tipo.in_(["competencia_geral", "competencia_especifica"]))
            .order_by(Item.tipo, Item.codigo)
        ).scalars()
    ]
    return {
        "etapas": etapas,
        "anos": anos,
        "componentes": componentes,
        "areas": areas,
        "campos": campos,
        "documentos": documentos,
        "tipos": tipos,
        "competencias": competencias,
    }


@router.get("/recorte")
def recorte(db: Session = Depends(get_db)) -> dict:
    snap = snapshot_or_503(db)
    return {
        "tag": snap.tag,
        "embedding_model": snap.embedding_model,
        "embedding_dimension": snap.embedding_dimension,
        "item_count": snap.item_count,
        "ingested_at": snap.ingested_at.isoformat() if snap.ingested_at else None,
    }


@router.get("/sugestoes")
def sugestoes(
    q: str = Query(min_length=1),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict:
    if alphanumeric_prefix_len(q) < 2:
        return {"q": q, "items": [], "ver_mais": False, "anuncio": "Nenhuma sugestão para este início de código."}
    items = suggest_codes(db, q, limit=limit + 1)
    ver_mais = len(items) > limit
    cards = [suggestion_card(db, item) for item in items[:limit]]
    n = len(cards)
    anuncio = f"{n} sugestões de código." if n else "Nenhuma sugestão para este início de código."
    return {"q": normalize_code(q), "items": cards, "ver_mais": ver_mais, "anuncio": anuncio}


@router.get("/codigos/{codigo}")
def codigo_lookup(codigo: str, request: Request, db: Session = Depends(get_db)) -> dict:
    started = time.perf_counter()
    status, item = lookup_item(db, codigo)
    latency = int((time.perf_counter() - started) * 1000)
    if status == "invalid":
        record_event(
            kind="lookup",
            mode="codigo",
            status_code=400,
            latency_ms=latency,
            query=codigo,
            result_count=0,
            request=request,
        )
        raise HTTPException(
            status_code=400,
            detail={
                "titulo": "Esse código não está no formato esperado.",
                "texto": "Confira letras e números. Exemplo: EF05MA03. Você também pode buscar pelo tema.",
                "acoes": ["Tentar outro código", "Buscar pelo tema"],
            },
        )
    if status == "missing":
        prefix = normalize_code(codigo)[:6]
        proximos = [suggestion_card(db, row) for row in suggest_codes(db, prefix, limit=5)]
        record_event(
            kind="lookup",
            mode="codigo",
            status_code=404,
            latency_ms=latency,
            query=codigo,
            result_count=0,
            request=request,
        )
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Esse código tem um formato válido, mas não existe no recorte atual da Base.",
                "texto": "A numeração oficial pode ter lacunas. Confira o código ou veja opções próximas.",
                "proximos": proximos,
            },
        )
    record_event(
        kind="lookup",
        mode="codigo",
        status_code=200,
        latency_ms=latency,
        query=codigo,
        result_count=1,
        request=request,
    )
    data = public_item(db, item)  # type: ignore[arg-type]
    data["relacionados"] = [public_item(db, rel) for rel in related_items(db, item)]  # type: ignore[arg-type]
    return data


def _filters_from_query(
    etapa: list[str] | None,
    ano: list[str] | None,
    componente: list[str] | None,
    documento: list[str] | None,
    area: list[str] | None,
    campo: list[str] | None,
    tipo: list[str] | None,
    incluir_revogados: bool,
) -> SearchFilters:
    return SearchFilters(
        etapas=etapa or None,
        anos=ano or None,
        componentes=componente or None,
        documentos=documento or None,
        areas=area or None,
        campos=campo or None,
        tipos=tipo or None,
        incluir_revogados=incluir_revogados,
    )


def _record_search(
    *,
    request: Request,
    q: str,
    filters: SearchFilters,
    payload: dict,
    latency_ms: int,
    cache_hit: bool,
) -> None:
    total = int(payload.get("total") or 0)
    record_event(
        kind="search",
        mode="filtros" if not q else "buscar",
        status_code=200,
        latency_ms=latency_ms,
        query=q or None,
        filters=filters.__dict__,
        inferred=payload.get("inferred") or None,
        result_count=total,
        cache_hit=cache_hit,
        atalho_codigo=bool(payload.get("atalho_codigo")),
        request=request,
    )


@router.get("/buscar")
async def buscar(
    request: Request,
    q: str = Query(default=""),
    etapa: list[str] | None = Query(default=None),
    ano: list[str] | None = Query(default=None),
    componente: list[str] | None = Query(default=None),
    documento: list[str] | None = Query(default=None),
    area: list[str] | None = Query(default=None),
    campo: list[str] | None = Query(default=None),
    tipo: list[str] | None = Query(default=None),
    incluir_revogados: bool = False,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    started = time.perf_counter()
    snapshot_or_503(db)
    q = (q or "").strip()
    filters = _filters_from_query(etapa, ano, componente, documento, area, campo, tipo, incluir_revogados)
    if not q and not has_scope(filters):
        raise HTTPException(
            status_code=400,
            detail={
                "titulo": "Falta um recorte ou um termo de busca.",
                "texto": "Digite o que você procura ou escolha ao menos um recorte: etapa, ano, campo, componente, documento ou tipo.",
            },
        )
    cached = cache_get("buscar.v4", q, filters.__dict__, limit, offset)
    if isinstance(cached, dict):
        _record_search(
            request=request,
            q=q,
            filters=filters,
            payload=cached,
            latency_ms=int((time.perf_counter() - started) * 1000),
            cache_hit=True,
        )
        return cached
    items, total, short = await hybrid_search(db, q, filters, limit=limit, offset=offset)
    trechos = []
    if wants_prose_strip(q, filters, atalho_codigo=short == "codigo", offset=offset):
        blocks = await hybrid_search_prose(db, q, limit=8, types=STRIP_TYPES)
        for block in blocks:
            if block.type not in STRIP_TYPES:
                continue
            trechos.append(public_prose_fonte(db, block))
            if len(trechos) >= 3:
                break
    payload = {
        "q": q,
        "total": total,
        "offset": offset,
        "limit": limit,
        "atalho_codigo": short == "codigo",
        "items": [public_item(db, item) for item in items],
        "trechos": trechos,
        "recorte": snapshot_or_503(db).tag,
        "inferred": inferred_labels(q) if q else [],
    }
    cache_set("buscar.v4", payload, q, filters.__dict__, limit, offset)
    _record_search(
        request=request,
        q=q,
        filters=filters,
        payload=payload,
        latency_ms=int((time.perf_counter() - started) * 1000),
        cache_hit=False,
    )
    return payload


class ExportBody(BaseModel):
    codigos: list[str] = Field(min_length=1, max_length=50)
    formato: str = Field(pattern="^(txt|csv)$")


@router.post("/exportar")
def exportar(body: ExportBody, request: Request, db: Session = Depends(get_db)) -> Response:
    if len(body.codigos) > 50:
        raise HTTPException(status_code=400, detail="O limite é de 50 itens.")
    items = []
    for codigo in body.codigos:
        item = db.get(Item, codigo)
        if item is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "titulo": "Não encontramos este código.",
                    "texto": f"O código {codigo} não está no recorte atual.",
                },
            )
        items.append(public_item(db, item))
    recorte = snapshot_or_503(db).tag
    record_event(
        kind="export",
        status_code=200,
        result_count=len(items),
        codigos=list(body.codigos),
        export_format=body.formato,
        request=request,
    )
    if body.formato == "txt":
        chunks = []
        for row in items:
            chunks.append(
                f"{row['codigo']} — {row['texto']}\n"
                f"{row['metadados_linha']}\n"
                f"Fonte: {row['documento']}"
                + (f", {row['pagina_pdf']}" if row.get("pagina_pdf") else "")
                + f". Recorte {recorte}.\n"
                f"{row['permalink']}\n"
            )
        content = "\n".join(chunks)
        return Response(
            content=content,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="buscabase.txt"'},
        )
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "codigo",
            "tipo",
            "texto",
            "etapa",
            "anos",
            "componente",
            "unidade_ou_campo",
            "documento",
            "fonte",
            "url",
            "recorte",
        ],
    )
    writer.writeheader()
    for row in items:
        writer.writerow(
            {
                "codigo": row["codigo"],
                "tipo": row["tipo"],
                "texto": row["texto"],
                "etapa": row["etapa"],
                "anos": ",".join(str(a) for a in (row["anos"] or [])),
                "componente": row["componente"],
                "unidade_ou_campo": row["unidade_ou_campo"],
                "documento": row["documento"],
                "fonte": (row.get("pagina_pdf") or ""),
                "url": row["permalink"],
                "recorte": recorte,
            }
        )
    return Response(
        content=buffer.getvalue().encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="buscabase.csv"'},
    )


class HistoricoTurn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: Literal["user", "assistant"]
    content: str = Field(default="", max_length=4000)
    codigos: list[str] = Field(default_factory=list, max_length=12)

    @model_validator(mode="before")
    @classmethod
    def content_from_text(cls, data):
        if isinstance(data, dict) and not str(data.get("content") or "").strip() and data.get("text"):
            data = {**data, "content": data["text"]}
        return data


class PerguntarBody(BaseModel):
    pergunta: str = Field(min_length=3, max_length=2000)
    historico: list[HistoricoTurn] = Field(default_factory=list, max_length=8)
    sessao: str | None = None


@router.post("/perguntar")
async def perguntar(request: Request, body: PerguntarBody, db: Session = Depends(get_db)):
    started = time.perf_counter()
    turn = len(body.historico) + 1
    if not perguntar_disponivel():
        record_event(
            kind="perguntar",
            mode="perguntar",
            status_code=503,
            query=body.pergunta,
            turn=turn,
            request=request,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "titulo": "Pesquisa conversacional está temporariamente indisponível.",
                "texto": "Você ainda pode encontrar e copiar itens usando Pesquisa por código, Pesquisa por filtros ou Pesquisa simples.",
            },
        )
    ip = client_ip(request)
    sessao = body.sessao or request.headers.get("x-session-id") or "anon"
    ok, reason = rate_limit(ip, sessao)
    if not ok:
        record_event(
            kind="perguntar",
            mode="perguntar",
            status_code=429,
            query=body.pergunta,
            turn=turn,
            error_id=reason,
            request=request,
        )
        raise HTTPException(
            status_code=429,
            detail={
                "titulo": "Você atingiu o limite de perguntas deste período.",
                "texto": "Pesquisa por código, Pesquisa por filtros e Pesquisa simples continuam disponíveis.",
                "motivo": reason,
            },
        )
    cancel = __import__("asyncio").Event()

    async def event_stream():
        last_name = None
        last_data: dict = {}
        error_id = None
        try:
            async for event in stream_answer(
                db, body.pergunta, [turn.model_dump() for turn in body.historico], cancel
            ):
                last_name = event["event"]
                last_data = event.get("data") or {}
                if await request.is_disconnected():
                    cancel.set()
                    break
                yield f"event: {event['event']}\ndata: {__import__('json').dumps(event['data'], ensure_ascii=False)}\n\n"
        except Exception:
            error_id = uuid.uuid4().hex[:8].upper()
            last_name = "error"
            last_data = {"codigo_atendimento": error_id}
            yield f"event: error\ndata: {{\"mensagem\": \"Não foi possível concluir a busca agora.\", \"codigo_atendimento\": \"{error_id}\"}}\n\n"
        finally:
            status = 200
            if last_name == "error":
                status = 500
            elif last_name == "cancelled":
                status = 499
            elif last_name == "unavailable":
                status = 503
            sources = last_data.get("sources")
            result_count = len(sources) if isinstance(sources, list) else None
            record_event(
                kind="perguntar",
                mode="perguntar",
                status_code=status,
                latency_ms=int((time.perf_counter() - started) * 1000),
                query=body.pergunta,
                turn=turn,
                result_count=result_count,
                cache_hit=bool(last_data.get("cache_hit")),
                tokens_in=last_data.get("tokens_in"),
                tokens_out=last_data.get("tokens_out"),
                error_id=last_data.get("codigo_atendimento") or error_id,
                request=request,
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class EventoBody(BaseModel):
    kind: Literal["page", "copy", "share"]
    copy_kind: Literal["texto", "texto_e_referencia", "link"] | None = None
    mode: Literal["codigo", "filtros", "buscar", "perguntar"] | None = None
    codigo: str | None = Field(default=None, max_length=32)
    page_class: Literal[
        "home",
        "home_consulta",
        "habilidade",
        "indices",
        "documento",
        "dimensao",
        "institucional",
        "outro",
    ] | None = None
    referrer_host: str | None = Field(default=None, max_length=200)
    device: Literal["mobile", "desktop", "bot"] | None = None


@router.post("/eventos")
def criar_evento(body: EventoBody, request: Request) -> dict:
    ip = client_ip(request)
    if not event_rate_ok(ip):
        raise HTTPException(
            status_code=429,
            detail={
                "titulo": "Você atingiu o limite deste período.",
                "texto": "Tente de novo em instantes.",
            },
        )
    ingest_from_request(request, body.model_dump())
    return {"ok": True}


@router.get("/uso")
def uso(
    dias: int = Query(default=7, ge=1, le=30),
    _: str = Depends(require_uso),
    db: Session = Depends(get_db),
) -> dict:
    return uso_resumo(db, dias)


class RecadoBody(BaseModel):
    nome: str = Field(max_length=120)
    email: str = Field(max_length=254)
    mensagem: str = Field(max_length=4000)
    pagina: str | None = Field(default=None, max_length=200)

    @field_validator("nome", "email", "mensagem", "pagina", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


@router.post("/recados")
def criar_recado_publico(body: RecadoBody, request: Request) -> dict:
    ip = client_ip(request)
    if not recado_rate_ok(ip):
        raise HTTPException(
            status_code=429,
            detail={
                "titulo": "Você atingiu o limite deste período.",
                "texto": "Tente de novo em instantes.",
            },
        )
    nome = body.nome
    email = body.email.lower()
    mensagem = body.mensagem
    if not nome or not email or not mensagem:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Preencha nome, e-mail e mensagem.",
                "texto": "Os três campos são obrigatórios.",
            },
        )
    if not email_ok(email):
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Informe um e-mail válido.",
                "texto": "Confira o endereço e tente novamente.",
            },
        )
    db = SessionLocal()
    try:
        criar_recado(
            db,
            nome=nome,
            email=email,
            mensagem=mensagem,
            pagina=sanitize_pagina(body.pagina),
        )
    finally:
        db.close()
    return {"ok": True}


@router.get("/recados")
def listar_recados_uso(
    _: str = Depends(require_uso),
    db: Session = Depends(get_db),
) -> dict:
    return {"recados": [public_recado(row) for row in listar_recados(db)]}


@router.get("/catalogo")
def catalogo(db: Session = Depends(get_db)) -> dict:
    snap = snapshot_or_503(db)
    items = db.execute(select(Item)).scalars()
    return {
        "recorte": snap.tag,
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
            }
            for item in items
        ],
        "documentos": [
            {"id": d.id, "slug": d.slug, "nome": d.nome} for d in db.execute(select(Documento)).scalars()
        ],
        "etapas": [{"id": e.id, "slug": e.slug, "nome": e.nome} for e in db.execute(select(Etapa)).scalars()],
        "areas": [
            {"id": a.id, "slug": a.slug, "nome": a.nome, "etapa_id": a.etapa_id}
            for a in db.execute(select(Area)).scalars()
        ],
        "componentes": [
            {"id": c.id, "slug": c.slug, "nome": c.nome, "etapa_id": c.etapa_id}
            for c in db.execute(select(Componente)).scalars()
        ],
        "recortes": [
            {"id": r.id, "slug": r.slug, "nome": r.nome, "etapa_id": r.etapa_id, "tipo": r.tipo}
            for r in db.execute(select(Recorte)).scalars()
        ],
    }


@router.get("/items/{codigo}")
def item_by_codigo(codigo: str, db: Session = Depends(get_db)) -> dict:
    item = db.get(Item, codigo)
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos este registro.",
                "texto": "Esse código não está no recorte atual da Base.",
            },
        )
    data = public_item(db, item)
    data["relacionados"] = [public_item(db, rel) for rel in related_items(db, item)]
    return data


@router.get("/prose/{documento_id}")
def prose_document(documento_id: str, db: Session = Depends(get_db)) -> dict:
    snapshot_or_503(db)
    cached = cache_get("prose.v1", documento_id)
    if cached:
        return cached
    doc = db.get(ProseDocument, documento_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos este documento.",
                "texto": "Essa reconstrução não está no recorte atual.",
            },
        )
    catalog = db.get(Documento, documento_id)
    payload = {
        "id": doc.id,
        "nome": catalog.nome if catalog else doc.id,
        "page_count": doc.page_count,
        "extracted_at": doc.extracted_at.isoformat() if doc.extracted_at else None,
    }
    cache_set("prose.v1", payload, documento_id)
    return payload


@router.get("/prose/{documento_id}/paginas/{n}")
def prose_page(documento_id: str, n: int, db: Session = Depends(get_db)) -> dict:
    snapshot_or_503(db)
    cached = cache_get("prose.v1.page", documento_id, n)
    if cached:
        return cached
    page = db.get(ProsePage, (documento_id, n))
    if page is None:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos esta página.",
                "texto": "Essa página não está na reconstrução do documento.",
            },
        )
    blocks = list(
        db.execute(
            select(ProseBlock)
            .options(
                load_only(
                    ProseBlock.id,
                    ProseBlock.documento_id,
                    ProseBlock.page,
                    ProseBlock.seq,
                    ProseBlock.type,
                    ProseBlock.text,
                    ProseBlock.item_codigo,
                )
            )
            .where(ProseBlock.documento_id == documento_id, ProseBlock.page == n)
            .order_by(ProseBlock.seq)
        ).scalars()
    )
    payload = {
        "documento_id": documento_id,
        "page": n,
        "width": page.width,
        "height": page.height,
        "blocks": [public_prose_block(block) for block in blocks],
    }
    cache_set("prose.v1.page", payload, documento_id, n)
    return payload


@router.get("/dimensao/{kind}/{slug}")
def dimensao(kind: str, slug: str, db: Session = Depends(get_db)) -> dict:
    mapping = {
        "etapa": (Etapa, "etapa"),
        "ano": (Recorte, "recorte_id"),
        "area": (Area, "area_id"),
        "componente": (Componente, "componente_id"),
        "documento": (Documento, "documento_id"),
    }
    if kind not in mapping:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos este índice.",
                "texto": "Esse tipo de página não faz parte dos índices da Base.",
            },
        )
    model, _field = mapping[kind]
    row = db.execute(select(model).where(model.slug == slug)).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos este índice.",
                "texto": "Esse endereço não está no recorte atual da Base.",
            },
        )
    stmt = _dimensao_stmt(db, kind, row)
    stmt = stmt.where(Item.tipo.in_(["habilidade", "objetivo"])).order_by(Item.codigo)
    rows = db.execute(stmt).scalars().all()
    items = [public_item(db, item) for item in rows]
    payload = getattr(row, "payload", None) if kind == "documento" else None
    return {
        "kind": kind,
        "id": row.id,
        "slug": row.slug,
        "nome": row.nome,
        "tipo": getattr(row, "tipo", None),
        "derivado_de": getattr(row, "derivado_de", None),
        "payload": payload if isinstance(payload, dict) else None,
        "items": items,
        "recorte": snapshot_or_503(db).tag,
    }


def _dimensao_stmt(db: Session, kind: str, row):
    stmt = select(Item)
    if kind == "etapa":
        return stmt.where(Item.etapa == row.id)
    if kind == "ano":
        return stmt.where(or_(*recorte_item_clauses(row)))
    if kind == "area":
        comp_ids = list(db.execute(select(Componente.id).where(Componente.area_id == row.id)).scalars())
        clauses = [Item.area_id == row.id]
        if comp_ids:
            clauses.append(Item.componente_id.in_(comp_ids))
        return stmt.where(or_(*clauses))
    if kind == "componente":
        return stmt.where(Item.componente_id == row.id)
    return stmt.where(Item.documento_id == row.id)
