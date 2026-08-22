"""Cache keys (HMAC) and first-party usage events. Consultas are stored; IP is not."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import settings
from app.db import SessionLocal
from app.models import UsageEvent

logger = logging.getLogger(__name__)

_BOT_RE = re.compile(
    r"bot|crawler|spider|slurp|facebookexternalhit|preview|linkedinbot|twitterbot|bingpreview",
    re.I,
)
_MOBILE_RE = re.compile(r"Mobile|Android|iPhone|iPad|iPod", re.I)


def query_hash(text: str) -> str:
    digest = hmac.new(
        settings.cache_hmac_secret.encode(),
        (text or "").encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def cache_key(*parts: object) -> str:
    payload = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return query_hash(payload)


def client_ip(request: Request | None) -> str:
    if request is None:
        return "0.0.0.0"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "0.0.0.0"
    if request.client and request.client.host:
        return request.client.host
    return "0.0.0.0"


def device_class(user_agent: str | None) -> str:
    if not user_agent:
        return "desktop"
    if _BOT_RE.search(user_agent):
        return "bot"
    if _MOBILE_RE.search(user_agent):
        return "mobile"
    return "desktop"


def visitor_day(ip: str, device: str) -> str:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return hmac.new(
        settings.cache_hmac_secret.encode(),
        f"{ip}|{device}|{day}".encode(),
        hashlib.sha256,
    ).hexdigest()


def referrer_host(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip()
    if raw.lower() in {"direct", ""}:
        return "direct"
    try:
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        host = (parsed.hostname or "").lower()
    except ValueError:
        return None
    if not host:
        return None
    if host.startswith("www."):
        host = host[4:]
    origin = urlparse(settings.public_origin).hostname or ""
    if origin.startswith("www."):
        origin = origin[4:]
    if host == origin or host in {"localhost", "127.0.0.1"}:
        return None
    return host[:200] or None


def request_context(request: Request | None) -> tuple[str | None, str | None, str | None]:
    if request is None:
        return None, None, None
    device = device_class(request.headers.get("user-agent"))
    host = referrer_host(request.headers.get("referer"))
    visitor = visitor_day(client_ip(request), device)
    return device, host, visitor


def record_event(
    *,
    kind: str,
    mode: str | None = None,
    page_class: str | None = None,
    query: str | None = None,
    filters: dict | None = None,
    inferred: list | None = None,
    codigos: list[str] | None = None,
    status_code: int | None = None,
    latency_ms: int | None = None,
    result_count: int | None = None,
    result_empty: bool | None = None,
    cache_hit: bool | None = None,
    atalho_codigo: bool | None = None,
    turn: int | None = None,
    export_format: str | None = None,
    copy_kind: str | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    error_id: str | None = None,
    referrer_host: str | None = None,
    device: str | None = None,
    visitor_day: str | None = None,
    request: Request | None = None,
    db: Session | None = None,
) -> None:
    req_device, req_host, req_visitor = request_context(request)
    event = UsageEvent(
        kind=kind,
        mode=mode,
        page_class=page_class,
        query=query,
        filters=filters,
        inferred=inferred,
        codigos=codigos,
        status_code=status_code,
        latency_ms=latency_ms,
        result_count=result_count,
        result_empty=result_empty if result_empty is not None else (result_count == 0 if result_count is not None else None),
        cache_hit=cache_hit,
        atalho_codigo=atalho_codigo,
        turn=turn,
        export_format=export_format,
        copy_kind=copy_kind,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        error_id=error_id,
        referrer_host=referrer_host if referrer_host is not None else req_host,
        device=device or req_device,
        visitor_day=visitor_day or req_visitor,
    )
    own = db is None
    session = db or SessionLocal()
    try:
        session.add(event)
        session.commit()
    except Exception:
        logger.exception("failed to record usage event")
        try:
            session.rollback()
        except Exception:
            pass
    finally:
        if own:
            session.close()
