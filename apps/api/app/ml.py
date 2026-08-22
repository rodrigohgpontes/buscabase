from __future__ import annotations

import httpx

from app.config import settings


def api_headers(api_key: str) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": settings.public_origin,
        "X-Title": "Busca Base",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def api_endpoint(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def generation_payload(messages: list[dict[str, str]]) -> dict:
    return {
        **settings.generation_extra_body,
        "model": settings.generation_model,
        "messages": messages,
        "temperature": settings.generation_temperature,
        "max_tokens": settings.generation_max_tokens,
        "stream": True,
    }


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    async with httpx.AsyncClient(timeout=settings.embedding_timeout_seconds) as client:
        response = await client.post(
            api_endpoint(settings.cloud_url(settings.embedding_api_url), "embeddings"),
            headers=api_headers(settings.cloud_key(settings.embedding_api_key)),
            json={"model": settings.embedding_model, "input": texts},
        )
        response.raise_for_status()
        data = response.json()["data"]
        data.sort(key=lambda row: row["index"])
        vectors = [row["embedding"] for row in data]
        for vector in vectors:
            if len(vector) != settings.embedding_dimension:
                raise RuntimeError(
                    f"Dimensão do vetor {len(vector)} diferente da dimensão fixa {settings.embedding_dimension}"
                )
        return vectors


def embed_texts_sync(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    with httpx.Client(timeout=settings.embedding_timeout_seconds) as client:
        response = client.post(
            api_endpoint(settings.cloud_url(settings.embedding_api_url), "embeddings"),
            headers=api_headers(settings.cloud_key(settings.embedding_api_key)),
            json={"model": settings.embedding_model, "input": texts},
        )
        response.raise_for_status()
        data = response.json()["data"]
        data.sort(key=lambda row: row["index"])
        vectors = [row["embedding"] for row in data]
        for vector in vectors:
            if len(vector) != settings.embedding_dimension:
                raise RuntimeError(
                    f"Dimensão do vetor {len(vector)} diferente da dimensão fixa {settings.embedding_dimension}"
                )
        return vectors


async def rerank(query: str, texts: list[str]) -> list[tuple[int, float]]:
    if not texts:
        return []
    if not settings.cloud_key(settings.rerank_api_key):
        return []
    async with httpx.AsyncClient(timeout=settings.rerank_timeout_seconds) as client:
        response = await client.post(
            api_endpoint(settings.cloud_url(settings.rerank_api_url), "rerank"),
            json={
                "model": settings.rerank_model,
                "query": query,
                "documents": texts,
                "top_n": min(len(texts), settings.rerank_top_k),
                "return_documents": False,
            },
            headers=api_headers(settings.cloud_key(settings.rerank_api_key)),
        )
        response.raise_for_status()
        payload = response.json()
        rows = payload if isinstance(payload, list) else payload.get("results", payload)
        scored: list[tuple[int, float]] = []
        for row in rows:
            index = int(row.get("index", 0))
            score = float(row.get("score", row.get("relevance_score", 0.0)))
            scored.append((index, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored
