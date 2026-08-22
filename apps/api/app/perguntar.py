"""Perguntar: reutiliza a recuperação do Buscar, mostra fontes antes de gerar, SSE, cancelamento e desligamento."""

from __future__ import annotations

import asyncio
import json
import re
import unicodedata
import uuid
from collections.abc import AsyncIterator

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cache import cache_get, cache_set, redis_client
from app.codes import normalize_code
from app.config import settings
from app.ml import api_endpoint, api_headers, generation_payload
from app.models import Item, ProseBlock
from app.retrieval import (
    SearchFilters,
    hybrid_search,
    hybrid_search_prose,
    is_catalog_query,
    is_item_lookup_query,
    parse_search_query,
)
from app.serialize import public_item_fonte, public_prose_fonte

SYSTEM_PROMPT = """Você é o Busca Base. Responda em português brasileiro, registro preciso de documento curricular.

Formato da resposta (obrigatório):
1. Resposta direta em 1–3 frases curtas.
2. Se precisar comparar ou listar, use no máximo uma lista curta com hífens (sem subtítulos).
3. Se a Base não tratar o pedido, diga isso com clareza e mostre só o que ela define.
4. Cite fontes no texto com [n], onde n é o número da fonte fornecida.

Proibições:
- Não use títulos markdown (##), tabelas, listas aninhadas nem blocos de código.
- Não invente códigos, progressões ou metodologia.
- Insira códigos exatamente como aparecem nas fontes.
- Não use cadeia de raciocínio. Não se apresente como pessoa. Não diga que está pensando.
- Distinga texto oficial de explicação.
- Você pode citar o documento e a página das fontes de prosa (reconstrução do PDF oficial).
- Não invente códigos, páginas ou documentos.
- Se um trecho de prosa tiver um código, só o mencione se esse código também estiver nas fontes de item.
- Se a pessoa pedir um percurso, avise que a ordem não é oficial da BNCC.
- Se houver conversa anterior, continue o assunto e os códigos já citados, salvo quando a pergunta atual mudar de tema.
- Se as fontes forem o recorte pedido (mesmo ano e componente, ou o tipo pedido), apresente o conjunto. Não dê a entender que a Base só contém os itens listados.
"""

PINNED_CODE_LIMIT = 4
HISTORY_TURN_LIMIT = 8
CATALOG_ITEM_LIMIT = 12

_CODE_RE = re.compile(r"\b(?:EI|EF|EM|CO)[A-Z0-9]{4,}\b")
_CANON_CODE_RE = re.compile(r"(?:EI|EF|EM|CO)[A-Z0-9]{4,}")
_CONTINUATION_RE = re.compile(
    r"(?i)^\s*("
    r"e\b|também|tambem|ainda|isso|isto|dessa|desse|desta|deste|"
    r"essa|esse|este|esta|o mesmo|a mesma|"
    r"o que muda|mais simples|mais detalhe|explique melhor|"
    r"em outras palavras|e no|e na|e nos|e nas|"
    r"agora no|agora na|agora nos|agora nas|"
    r"e quanto|e sobre"
    r")"
)
_THIN_TOKENS = {
    "muda",
    "mudam",
    "mudanca",
    "melhor",
    "simples",
    "isso",
    "isto",
    "mesmo",
    "mesma",
    "compare",
    "comparar",
    "explique",
    "explicar",
    "diferenca",
    "diferencas",
    "quero",
    "saber",
    "sobre",
}


def perguntar_disponivel() -> bool:
    return bool(settings.perguntar_enabled and settings.cloud_key(settings.generation_api_key))


def rate_limit(ip: str, session_id: str) -> tuple[bool, str | None]:
    client = redis_client()
    ip_key = f"rl:ip:{ip}"
    sess_key = f"rl:sess:{session_id}"
    ip_count = client.incr(ip_key)
    if ip_count == 1:
        client.expire(ip_key, settings.perguntar_rate_window_seconds)
    sess_count = client.incr(sess_key)
    if sess_count == 1:
        client.expire(sess_key, settings.perguntar_rate_window_seconds)
    if ip_count > settings.perguntar_rate_limit_ip or sess_count > settings.perguntar_session_limit:
        return False, "rate"
    queue = int(client.get("perguntar:queue") or 0)
    if queue >= settings.perguntar_queue_limit:
        return False, "queue"
    return True, None


def enqueue() -> int:
    client = redis_client()
    return int(client.incr("perguntar:queue"))


def dequeue() -> None:
    client = redis_client()
    client.decr("perguntar:queue")


def extract_codes(text: str) -> list[str]:
    return _CODE_RE.findall((text or "").upper())


def canon_code(raw: str) -> str | None:
    code = normalize_code(raw)
    if _CANON_CODE_RE.fullmatch(code):
        return code
    return None


def validate_codes(db: Session, text: str, allowed: set[str]) -> str:
    for code in extract_codes(text):
        if code not in allowed:
            item = db.get(Item, code)
            if item is None or code not in allowed:
                text = text.replace(code, "[código não confirmado]")
    return text


def _truncate_source_text(text: str) -> str:
    limit = settings.perguntar_source_text_chars
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _clean_turn(turn: dict) -> dict | None:
    role = turn.get("role")
    if role not in ("user", "assistant"):
        return None
    content = turn.get("content") or turn.get("text") or ""
    if not isinstance(content, str):
        return None
    content = content.strip()[:4000]
    if not content:
        return None
    entry: dict = {"role": role, "content": content}
    raw_codes = turn.get("codigos") or []
    if isinstance(raw_codes, list):
        codes: list[str] = []
        seen: set[str] = set()
        for raw in raw_codes:
            if not isinstance(raw, str):
                continue
            code = canon_code(raw)
            if code and code not in seen:
                seen.add(code)
                codes.append(code)
            if len(codes) >= 8:
                break
        if codes:
            entry["codigos"] = codes
    return entry


def previous_history(history: list[dict], question: str) -> list[dict]:
    """Keep the last turns, dropping the current question if the client already appended it."""
    cleaned = [turn for turn in (_clean_turn(t) for t in history or []) if turn]
    turns = cleaned[-HISTORY_TURN_LIMIT:]
    if (
        turns
        and turns[-1]["role"] == "user"
        and turns[-1]["content"] == question.strip()
    ):
        return turns[:-1]
    return turns


def cited_codes(history: list[dict], question: str) -> list[str]:
    """Unique codes from historico, most recently mentioned last."""
    ordered: list[str] = []
    for turn in previous_history(history, question):
        chunk: list[str] = []
        chunk.extend(turn.get("codigos") or [])
        chunk.extend(extract_codes(turn.get("content") or ""))
        for code in chunk:
            if code in ordered:
                ordered.remove(code)
            ordered.append(code)
    return ordered


def _fold_tokens(text: str) -> set[str]:
    nfkd = unicodedata.normalize("NFKD", (text or "").lower())
    folded = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return {token for token in re.findall(r"[a-z0-9]{3,}", folded) if token not in _THIN_TOKENS}


def is_topic_shift(question: str, history: list[dict]) -> bool:
    """True when the new question starts another subject and should not reuse cited codes."""
    prior = previous_history(history, question)
    if not prior:
        return False
    if _CONTINUATION_RE.search(question.strip()):
        return False
    prev_codes = set(cited_codes(history, question))
    new_codes = set(extract_codes(question))
    if new_codes & prev_codes:
        return False
    lexical, _inferred = parse_search_query(question)
    tokens = _fold_tokens(lexical)
    if len(tokens) < 2 or len(question.split()) < 8:
        return False
    prior_user = " ".join(turn["content"] for turn in prior if turn["role"] == "user")
    prior_lexical, _ = parse_search_query(prior_user)
    if tokens & _fold_tokens(prior_lexical):
        return False
    return True


def retrieval_query(question: str, history: list[dict]) -> str:
    """Expand thin follow-ups with the last user turn and cited codes; leave topic shifts as-is."""
    question = (question or "").strip()
    if is_topic_shift(question, history):
        return question
    prior = previous_history(history, question)
    if not prior:
        return question
    last_user = next(
        (turn["content"] for turn in reversed(prior) if turn["role"] == "user"),
        "",
    )
    codes = cited_codes(history, question)[-PINNED_CODE_LIMIT:]
    parts = [last_user, question, " ".join(codes)]
    return " ".join(part for part in parts if part).strip()


def load_items_by_codes(db: Session, codes: list[str]) -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()
    for code in codes:
        if not code or code in seen:
            continue
        item = db.get(Item, code)
        if item is not None:
            items.append(item)
            seen.add(code)
    return items


def follow_up_neighbors(db: Session, pinned: list[Item], question: str) -> list[Item]:
    """When a follow-up names another year, pull same-componente items from that year."""
    _lexical, inferred = parse_search_query(question)
    years = [year for year in (inferred.anos or []) if isinstance(year, int)]
    if not years or not pinned:
        return []
    found: list[Item] = []
    seen = {item.codigo for item in pinned}
    for item in pinned:
        stmt = select(Item).where(Item.codigo != item.codigo, Item.vigencia_status != "revogado")
        if item.componente_id:
            stmt = stmt.where(Item.componente_id == item.componente_id)
        stmt = stmt.where(Item.anos.overlap(years))
        if item.unidade_ou_campo:
            stmt = stmt.where(Item.unidade_ou_campo == item.unidade_ou_campo)
        stmt = stmt.limit(3)
        for row in db.execute(stmt).scalars():
            if row.codigo not in seen:
                found.append(row)
                seen.add(row.codigo)
    return found


def merge_source_items(
    pinned: list,
    searched: list,
    *,
    limit: int,
    pin_cap: int = PINNED_CODE_LIMIT,
) -> list:
    """Keep cited items first, leaving room for newly retrieved sources."""
    seen: set[str] = set()
    out: list = []
    search_reserve = 2 if searched else 0
    pin_budget = min(len(pinned), pin_cap, max(0, limit - search_reserve))
    for item in list(pinned)[:pin_budget] + list(searched):
        codigo = getattr(item, "codigo", None)
        if not codigo or codigo in seen:
            continue
        seen.add(codigo)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def prose_source_budget(query: str, filters: SearchFilters | None = None) -> int:
    if is_item_lookup_query(query, filters):
        return 1
    return settings.perguntar_prose_source_limit


def merge_prose_blocks(
    items: list[Item],
    blocks: list[ProseBlock],
    *,
    prose_cap: int,
    total_cap: int,
) -> list[ProseBlock]:
    item_codes = {item.codigo for item in items}
    remaining = max(0, total_cap - len(items))
    cap = min(prose_cap, remaining)
    out: list[ProseBlock] = []
    for block in blocks:
        if block.item_codigo and block.item_codigo in item_codes:
            continue
        out.append(block)
        if len(out) >= cap:
            break
    return out


def _item_from_source(source: dict) -> dict | None:
    if source.get("kind") == "prose":
        return None
    if source.get("kind") == "item":
        item = source.get("item")
        return item if isinstance(item, dict) else None
    if source.get("codigo"):
        return source
    return None


def allowed_codes_from_sources(sources: list[dict]) -> set[str]:
    allowed: set[str] = set()
    for source in sources:
        item = _item_from_source(source)
        if item and item.get("codigo"):
            allowed.add(item["codigo"])
    return allowed


def source_cache_ids(sources: list[dict]) -> list[str]:
    ids: list[str] = []
    for source in sources:
        if source.get("kind") == "prose" and source.get("block_id"):
            ids.append(source["block_id"])
            continue
        item = _item_from_source(source)
        if item and item.get("codigo"):
            ids.append(item["codigo"])
    return ids


async def retrieve_sources(db: Session, question: str, history: list[dict] | None = None) -> list[dict]:
    history = history or []
    shift = is_topic_shift(question, history)
    pin_codes: list[str] = []
    if previous_history(history, question) and not shift:
        pin_codes.extend(cited_codes(history, question)[-PINNED_CODE_LIMIT:])
    pin_codes.extend(extract_codes(question))
    pinned = load_items_by_codes(db, pin_codes)
    query = retrieval_query(question, history)
    item_limit = item_source_limit_for(query)
    source_limit = max(settings.perguntar_source_limit, item_limit)
    searched, _, _ = await hybrid_search(
        db,
        query,
        SearchFilters(),
        limit=item_limit,
        offset=0,
    )
    extra: list[Item] = []
    if pinned and previous_history(history, question) and not shift:
        extra = follow_up_neighbors(db, pinned, question)
    items = merge_source_items(pinned, extra + searched, limit=item_limit)
    prose_cap = prose_source_budget(question)
    fetched = await hybrid_search_prose(db, query, limit=max(prose_cap * 2, prose_cap))
    prose = merge_prose_blocks(
        items,
        fetched,
        prose_cap=prose_cap,
        total_cap=source_limit,
    )
    fontes = [public_item_fonte(db, item) for item in items]
    fontes.extend(public_prose_fonte(db, block) for block in prose)
    return fontes[:source_limit]


def item_source_limit_for(query: str) -> int:
    if is_catalog_query(query):
        return max(settings.perguntar_item_source_limit, CATALOG_ITEM_LIMIT)
    return settings.perguntar_item_source_limit


def _format_source_block(index: int, source: dict) -> str:
    if source.get("kind") == "prose":
        return (
            f"[{index}] Trecho oficial · {source.get('documento')}, p. {source.get('page')}\n"
            f"Texto oficial (reconstrução): {_truncate_source_text(source.get('texto') or '')}"
        )
    item = _item_from_source(source) or source
    return (
        f"[{index}] {item.get('codigo')} ({item.get('tipo_label')})\n"
        f"Texto da BNCC: {_truncate_source_text(item.get('texto') or '')}\n"
        f"Contexto: {item.get('metadados_linha')}\n"
        f"Documento: {item.get('documento')} · Recorte {item.get('recorte')}"
    )


def build_messages(question: str, history: list[dict], sources: list[dict]) -> list[dict]:
    source_block = [_format_source_block(index, source) for index, source in enumerate(sources, start=1)]
    prior = previous_history(history, question)
    follow_up_note = ""
    if prior:
        follow_up_note = (
            "\n\nContinue a conversa com a pergunta atual. Use só as fontes numeradas acima; "
            "elas já incluem códigos citados antes quando ainda forem pertinentes."
        )
    user = (
        "Fontes recuperadas:\n"
        + "\n\n".join(source_block)
        + follow_up_note
        + "\n\nPergunta:\n"
        + question
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in prior:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user})
    return messages


async def stream_answer(
    db: Session,
    question: str,
    history: list[dict],
    cancel_event: asyncio.Event,
) -> AsyncIterator[dict]:
    if not perguntar_disponivel():
        yield {"event": "unavailable", "data": {"motivo": "desativado"}}
        return

    yield {"event": "status", "data": {"texto": "Procurando trechos na Base…"}}
    sources = await retrieve_sources(db, question, history)
    allowed = allowed_codes_from_sources(sources)
    yield {"event": "sources", "data": {"sources": sources}}

    if not sources:
        yield {
            "event": "status",
            "data": {"texto": "Não encontrei trechos suficientes na Base para responder com segurança."},
        }
        yield {
            "event": "complete",
            "data": {
                "resposta": "Não encontrei trechos suficientes na Base para responder com segurança. Tente informar a etapa, o ano, o componente ou um código.",
                "sources": [],
                "incompleta": False,
            },
        }
        return

    yield {"event": "status", "data": {"texto": "Conferindo códigos e fontes…"}}
    prior = previous_history(history, question)
    cache_parts = (
        question,
        [turn["content"] for turn in prior],
        cited_codes(history, question),
        source_cache_ids(sources),
        settings.generation_model,
    )
    cache = cache_get("perguntar", *cache_parts)
    if cache:
        yield {"event": "status", "data": {"texto": "Resposta em andamento"}}
        yield {"event": "token", "data": {"text": cache["resposta"]}}
        yield {"event": "complete", "data": {**cache, "cache_hit": True}}
        return

    yield {"event": "status", "data": {"texto": "Preparando a resposta…"}}
    messages = build_messages(question, history, sources)
    queue_size = enqueue()
    accumulated = ""
    try:
        if queue_size > 1:
            yield {
                "event": "status",
                "data": {"texto": "Há outras perguntas na fila. A sua será respondida em seguida."},
            }
        timeout = httpx.Timeout(settings.generation_timeout_seconds, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                api_endpoint(settings.cloud_url(settings.generation_api_url), "chat/completions"),
                headers=api_headers(settings.cloud_key(settings.generation_api_key)),
                json=generation_payload(messages),
            ) as response:
                if response.status_code >= 400:
                    yield {
                        "event": "error",
                        "data": {
                            "mensagem": "Não foi possível concluir a busca agora.",
                            "codigo_atendimento": uuid.uuid4().hex[:8].upper(),
                        },
                    }
                    return
                yield {"event": "status", "data": {"texto": "Resposta em andamento"}}
                tokens_in = None
                tokens_out = None
                async for line in response.aiter_lines():
                    if cancel_event.is_set():
                        yield {"event": "cancelled", "data": {"resposta": accumulated, "incompleta": True}}
                        return
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    usage = chunk.get("usage") or {}
                    if usage.get("prompt_tokens") is not None:
                        tokens_in = usage.get("prompt_tokens")
                    if usage.get("completion_tokens") is not None:
                        tokens_out = usage.get("completion_tokens")
                    delta = chunk["choices"][0].get("delta", {}).get("content") or ""
                    if delta:
                        accumulated += delta
                        yield {"event": "token", "data": {"text": delta}}
        accumulated = validate_codes(db, accumulated, allowed)
        result = {
            "resposta": accumulated,
            "sources": sources,
            "incompleta": False,
            "aviso": "Resposta gerada a partir dos trechos encontrados na Base.",
            "cache_hit": False,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
        cacheable = {key: value for key, value in result.items() if key not in {"cache_hit", "tokens_in", "tokens_out"}}
        cache_set("perguntar", cacheable, *cache_parts)
        yield {"event": "complete", "data": result}
    except httpx.HTTPError:
        yield {
            "event": "error",
            "data": {
                "mensagem": "A conexão foi interrompida.",
                "resposta": accumulated,
                "incompleta": True,
                "codigo_atendimento": uuid.uuid4().hex[:8].upper(),
            },
        }
    finally:
        dequeue()
