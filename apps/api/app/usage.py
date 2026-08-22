from __future__ import annotations

import hmac
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.config import settings
from app.models import UsageEvent

logger = logging.getLogger(__name__)

_basic = HTTPBasic(auto_error=False)
_CODIGO_RE = re.compile(r"^[A-Za-z0-9]{1,32}$")
_HOST_RE = re.compile(r"^[a-zA-Z0-9.-]{1,200}$")

PAGE_CLASSES = {
    "home",
    "home_consulta",
    "habilidade",
    "indices",
    "documento",
    "dimensao",
    "institucional",
    "outro",
}
INGEST_KINDS = {"page", "copy", "share"}
COPY_KINDS = {"texto", "texto_e_referencia", "link"}
MODES = {"codigo", "filtros", "buscar", "perguntar"}
DEVICES = {"mobile", "desktop", "bot"}


def _same(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def require_uso(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_basic)],
) -> str:
    if not settings.uso_password:
        raise HTTPException(
            status_code=404,
            detail={
                "titulo": "Não encontramos este endereço.",
                "texto": "Confira o endereço ou volte à busca.",
            },
        )
    if credentials is None or not (
        _same(credentials.username, settings.uso_user)
        and _same(credentials.password, settings.uso_password)
    ):
        raise HTTPException(
            status_code=401,
            detail={
                "titulo": "Autenticação necessária.",
                "texto": "Informe o usuário e a senha de uso.",
            },
            headers={"WWW-Authenticate": 'Basic realm="Busca Base"'},
        )
    return credentials.username


def event_rate_ok(ip: str) -> bool:
    try:
        client = redis_client()
        key = f"rl:evt:{ip}"
        count = client.incr(key)
        if count == 1:
            client.expire(key, settings.perguntar_rate_window_seconds)
        return count <= max(settings.perguntar_rate_limit_ip * 3, 60)
    except Exception:
        logger.exception("event rate limit unavailable")
        return True


def sanitize_codigo(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not _CODIGO_RE.match(text):
        return None
    return text.upper()


def sanitize_host(value: str | None) -> str | None:
    if not value:
        return None
    host = value.strip().lower()
    if host.startswith("www."):
        host = host[4:]
    if host == "direct":
        return "direct"
    if not _HOST_RE.match(host):
        return None
    return host


def _cutoff(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def _human(cutoff: datetime):
    return and_(
        UsageEvent.created_at >= cutoff,
        or_(UsageEvent.device.is_(None), UsageEvent.device != "bot"),
    )


def _count(db: Session, *clauses) -> int:
    return int(db.execute(select(func.count()).where(*clauses)).scalar() or 0)


def _group_counts(db: Session, column, *clauses, limit: int = 20) -> list[dict]:
    filters = [*clauses, column.isnot(None)]
    if getattr(column.type, "python_type", None) is str:
        filters.append(column != "")
    rows = db.execute(
        select(column, func.count().label("n"))
        .where(*filters)
        .group_by(column)
        .order_by(desc("n"))
        .limit(limit)
    ).all()
    return [{"valor": value, "n": int(n)} for value, n in rows]


def _filter_stats(db: Session, *clauses) -> dict:
    keys: dict[str, int] = {}
    values: dict[str, int] = {}
    blobs = db.execute(select(UsageEvent.filters).where(*clauses, UsageEvent.filters.isnot(None))).scalars()
    for blob in blobs:
        if not isinstance(blob, dict):
            continue
        for key, raw in blob.items():
            if key == "incluir_revogados":
                if raw:
                    keys[key] = keys.get(key, 0) + 1
                continue
            if not raw:
                continue
            keys[key] = keys.get(key, 0) + 1
            items = raw if isinstance(raw, list) else [raw]
            for item in items:
                label = f"{key}:{item}"
                values[label] = values.get(label, 0) + 1
    top_keys = [{"valor": key, "n": n} for key, n in sorted(keys.items(), key=lambda row: -row[1])[:12]]
    top_values = [{"valor": key, "n": n} for key, n in sorted(values.items(), key=lambda row: -row[1])[:20]]
    return {"chaves": top_keys, "valores": top_values}


def _exported_codes(db: Session, *clauses) -> list[dict]:
    rows = db.execute(select(UsageEvent.codigos).where(*clauses, UsageEvent.kind == "export")).scalars()
    counts: dict[str, int] = {}
    for codes in rows:
        if not codes:
            continue
        for code in codes:
            counts[code] = counts.get(code, 0) + 1
    return [{"valor": code, "n": n} for code, n in sorted(counts.items(), key=lambda row: -row[1])[:20]]


def uso_resumo(db: Session, days: int) -> dict:
    cutoff = _cutoff(days)
    human = _human(cutoff)
    consulta = and_(human, UsageEvent.kind.in_(["lookup", "search", "perguntar"]))
    fim = datetime.now(timezone.utc)
    unicos = int(
        db.execute(
            select(func.count(func.distinct(UsageEvent.visitor_day))).where(
                human, UsageEvent.visitor_day.isnot(None)
            )
        ).scalar()
        or 0
    )
    latencies = and_(consulta, UsageEvent.latency_ms.isnot(None))
    p50 = db.execute(select(func.percentile_cont(0.5).within_group(UsageEvent.latency_ms)).where(latencies)).scalar()
    p95 = db.execute(select(func.percentile_cont(0.95).within_group(UsageEvent.latency_ms)).where(latencies)).scalar()
    cache_total = _count(db, consulta, UsageEvent.cache_hit.isnot(None))
    cache_hits = _count(db, consulta, UsageEvent.cache_hit.is_(True))
    tokens_in = int(
        db.execute(select(func.coalesce(func.sum(UsageEvent.tokens_in), 0)).where(human, UsageEvent.kind == "perguntar")).scalar()
        or 0
    )
    tokens_out = int(
        db.execute(select(func.coalesce(func.sum(UsageEvent.tokens_out), 0)).where(human, UsageEvent.kind == "perguntar")).scalar()
        or 0
    )
    return {
        "periodo": {"dias": days, "inicio": cutoff.isoformat(), "fim": fim.isoformat()},
        "visitas": {
            "unicos": unicos,
            "paginas": _count(db, human, UsageEvent.kind == "page"),
            "por_classe": _group_counts(db, UsageEvent.page_class, human, UsageEvent.kind == "page"),
        },
        "consultas": {
            "total": _count(db, consulta),
            "por_modo": _group_counts(db, UsageEvent.mode, consulta),
            "p50_ms": int(p50) if p50 is not None else None,
            "p95_ms": int(p95) if p95 is not None else None,
            "cache_total": cache_total,
            "cache_hits": cache_hits,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "perguntar_429": _count(db, human, UsageEvent.kind == "perguntar", UsageEvent.status_code == 429),
            "perguntar_503": _count(db, human, UsageEvent.kind == "perguntar", UsageEvent.status_code == 503),
        },
        "como": {
            "top_consultas": _group_counts(db, UsageEvent.query, consulta, limit=20),
            "top_codigos": _group_counts(
                db, UsageEvent.query, human, UsageEvent.kind == "lookup", UsageEvent.status_code == 200
            ),
            "vazias": _group_counts(
                db,
                UsageEvent.query,
                human,
                or_(UsageEvent.result_empty.is_(True), and_(UsageEvent.kind == "search", UsageEvent.result_count == 0)),
            ),
            "codigo_404": _group_counts(
                db, UsageEvent.query, human, UsageEvent.kind == "lookup", UsageEvent.status_code == 404
            ),
            "codigo_400": _group_counts(
                db, UsageEvent.query, human, UsageEvent.kind == "lookup", UsageEvent.status_code == 400
            ),
            "filtros": _filter_stats(db, human, UsageEvent.kind == "search"),
            "perguntar_turnos": _group_counts(db, UsageEvent.turn, human, UsageEvent.kind == "perguntar"),
        },
        "levar": {
            "copias": _count(db, human, UsageEvent.kind == "copy"),
            "por_copia": _group_counts(db, UsageEvent.copy_kind, human, UsageEvent.kind == "copy"),
            "exportacoes": _count(db, human, UsageEvent.kind == "export"),
            "por_formato": _group_counts(db, UsageEvent.export_format, human, UsageEvent.kind == "export"),
            "compartilhamentos": _count(db, human, UsageEvent.kind == "share"),
            "top_exportados": _exported_codes(db, human),
        },
        "origem": {
            "referers": _group_counts(db, UsageEvent.referrer_host, human),
            "landings": _group_counts(db, UsageEvent.page_class, human, UsageEvent.kind == "page"),
            "dispositivos": _group_counts(db, UsageEvent.device, human),
        },
    }


def ingest_from_request(request: Request, body: dict) -> None:
    from app.privacy import record_event

    kind = body.get("kind")
    if kind not in INGEST_KINDS:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Os dados enviados não estão no formato esperado.",
                "texto": "Confira os campos e tente novamente.",
            },
        )
    page_class = body.get("page_class")
    if page_class is not None and page_class not in PAGE_CLASSES:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Os dados enviados não estão no formato esperado.",
                "texto": "Confira os campos e tente novamente.",
            },
        )
    if kind == "page" and page_class not in PAGE_CLASSES:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Os dados enviados não estão no formato esperado.",
                "texto": "Confira os campos e tente novamente.",
            },
        )
    copy_kind = body.get("copy_kind")
    if copy_kind is not None and copy_kind not in COPY_KINDS:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Os dados enviados não estão no formato esperado.",
                "texto": "Confira os campos e tente novamente.",
            },
        )
    mode = body.get("mode")
    if mode is not None and mode not in MODES:
        raise HTTPException(
            status_code=422,
            detail={
                "titulo": "Os dados enviados não estão no formato esperado.",
                "texto": "Confira os campos e tente novamente.",
            },
        )
    device = body.get("device")
    if device is not None and device not in DEVICES:
        device = None
    record_event(
        kind=kind,
        mode=mode,
        page_class=page_class,
        copy_kind=copy_kind,
        codigos=[code] if (code := sanitize_codigo(body.get("codigo"))) else None,
        referrer_host=sanitize_host(body.get("referrer_host")),
        device=device,
        request=request,
    )
