from __future__ import annotations

import json

import redis

from app.config import settings
from app.privacy import cache_key

_client: redis.Redis | None = None


def redis_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def cache_get(namespace: str, *parts: object) -> dict | list | None:
    raw = redis_client().get(f"{namespace}:{cache_key(*parts)}")
    if not raw:
        return None
    return json.loads(raw)


def cache_set(namespace: str, value: object, *parts: object, ttl: int | None = None) -> None:
    redis_client().setex(
        f"{namespace}:{cache_key(*parts)}",
        ttl or settings.cache_ttl_seconds,
        json.dumps(value, ensure_ascii=False, default=str),
    )


def cache_delete_prefix(namespace: str) -> None:
    client = redis_client()
    for key in client.scan_iter(f"{namespace}:*"):
        client.delete(key)
