"""Recados enviados pelo widget público. IP não é gravado."""

from __future__ import annotations

import logging
import re

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.config import settings
from app.models import Recado

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LIST_LIMIT = 200


def recado_rate_ok(ip: str) -> bool:
    try:
        client = redis_client()
        key = f"rl:recado:{ip}"
        count = client.incr(key)
        if count == 1:
            client.expire(key, settings.recado_rate_window_seconds)
        return count <= settings.recado_rate_limit_ip
    except Exception:
        logger.exception("recado rate limit unavailable")
        return True


def email_ok(value: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(value))


def sanitize_pagina(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not text.startswith("/") or text.startswith("//") or "://" in text:
        return None
    if any(ch.isspace() for ch in text):
        return None
    return text[:200]


def criar_recado(
    db: Session, *, nome: str, email: str, mensagem: str, pagina: str | None
) -> Recado:
    row = Recado(nome=nome, email=email, mensagem=mensagem, pagina=pagina)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def listar_recados(db: Session) -> list[Recado]:
    return list(
        db.execute(select(Recado).order_by(desc(Recado.created_at)).limit(LIST_LIMIT)).scalars()
    )


def public_recado(row: Recado) -> dict:
    return {
        "id": row.id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "nome": row.nome,
        "email": row.email,
        "mensagem": row.mensagem,
        "pagina": row.pagina,
    }
