from __future__ import annotations

import pytest

from app import ml
from app.config import settings
from app.perguntar import perguntar_disponivel


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeAsyncClient:
    def __init__(self, response: FakeResponse, calls: list[dict], **_kwargs):
        self.response = response
        self.calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def post(self, url: str, **kwargs):
        self.calls.append({"url": url, **kwargs})
        return self.response


def test_generation_payload_is_provider_configurable(monkeypatch):
    monkeypatch.setattr(settings, "generation_model", "provider/model")
    monkeypatch.setattr(settings, "generation_extra_body", {"reasoning": {"enabled": False}})

    payload = ml.generation_payload([{"role": "user", "content": "Pergunta"}])

    assert payload["model"] == "provider/model"
    assert payload["reasoning"] == {"enabled": False}
    assert payload["stream"] is True


def test_generation_extra_body_does_not_override_core_fields(monkeypatch):
    monkeypatch.setattr(settings, "generation_model", "deepseek/deepseek-v4-flash")
    monkeypatch.setattr(
        settings,
        "generation_extra_body",
        {
            "thinking": {"type": "disabled"},
            "reasoning": {"enabled": False, "effort": "none"},
        },
    )

    payload = ml.generation_payload([{"role": "user", "content": "Pergunta"}])

    assert payload["model"] == "deepseek/deepseek-v4-flash"
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["reasoning"] == {"enabled": False, "effort": "none"}
    assert payload["stream"] is True


def test_perguntar_requires_enabled_cloud_generation(monkeypatch):
    monkeypatch.setattr(settings, "perguntar_enabled", True)
    monkeypatch.setattr(settings, "generation_api_key", "")
    monkeypatch.setattr(settings, "openrouter_api_key", "")
    assert perguntar_disponivel() is False

    monkeypatch.setattr(settings, "generation_api_key", "secret")
    assert perguntar_disponivel() is True


def test_openrouter_key_fills_empty_layer_keys(monkeypatch):
    monkeypatch.setattr(settings, "perguntar_enabled", True)
    monkeypatch.setattr(settings, "openrouter_api_key", "or-secret")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "rerank_api_key", "")
    monkeypatch.setattr(settings, "generation_api_key", "")

    assert settings.cloud_key(settings.embedding_api_key) == "or-secret"
    assert settings.cloud_key(settings.rerank_api_key) == "or-secret"
    assert settings.cloud_key(settings.generation_api_key) == "or-secret"
    assert perguntar_disponivel() is True


@pytest.mark.asyncio
async def test_embed_texts_uses_configured_openai_compatible_api(monkeypatch):
    calls: list[dict] = []
    response = FakeResponse(
        {"data": [{"index": 1, "embedding": [0.3, 0.4]}, {"index": 0, "embedding": [0.1, 0.2]}]}
    )
    monkeypatch.setattr(
        ml.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response, calls, **kwargs),
    )
    monkeypatch.setattr(settings, "embedding_api_url", "https://embedding.example/v1")
    monkeypatch.setattr(settings, "embedding_api_key", "embedding-secret")
    monkeypatch.setattr(settings, "embedding_model", "embedding-model")
    monkeypatch.setattr(settings, "embedding_dimension", 2)

    vectors = await ml.embed_texts(["um", "dois"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert calls[0]["url"] == "https://embedding.example/v1/embeddings"
    assert calls[0]["headers"]["Authorization"] == "Bearer embedding-secret"
    assert calls[0]["json"] == {"model": "embedding-model", "input": ["um", "dois"]}


@pytest.mark.asyncio
async def test_rerank_uses_configured_api(monkeypatch):
    calls: list[dict] = []
    response = FakeResponse(
        {
            "results": [
                {"index": 1, "relevance_score": 0.9},
                {"index": 0, "relevance_score": 0.4},
            ]
        }
    )
    monkeypatch.setattr(
        ml.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response, calls, **kwargs),
    )
    monkeypatch.setattr(settings, "rerank_api_url", "https://rerank.example/v1")
    monkeypatch.setattr(settings, "rerank_api_key", "rerank-secret")
    monkeypatch.setattr(settings, "rerank_model", "rerank-model")

    ranked = await ml.rerank("frações", ["a", "b"])

    assert ranked == [(1, 0.9), (0, 0.4)]
    assert calls[0]["url"] == "https://rerank.example/v1/rerank"
    assert calls[0]["headers"]["Authorization"] == "Bearer rerank-secret"
    assert calls[0]["json"]["documents"] == ["a", "b"]
    assert calls[0]["json"]["top_n"] == 2
