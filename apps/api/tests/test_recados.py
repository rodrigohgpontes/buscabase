import base64
import os

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.recados import email_ok, recado_rate_ok, sanitize_pagina

client = TestClient(app)


@pytest.fixture(autouse=True)
def _allow_recados(monkeypatch):
    monkeypatch.setattr("app.routers.recado_rate_ok", lambda _ip: True)


def test_email_ok_accepts_simple_address():
    assert email_ok("pessoa@escola.edu.br") is True
    assert email_ok("invalido") is False
    assert email_ok("sem@dominio") is False
    assert email_ok("a@b.c") is True


def test_sanitize_pagina_keeps_path_only():
    assert sanitize_pagina("/sobre") == "/sobre"
    assert sanitize_pagina("/?modo=buscar") == "/?modo=buscar"
    assert sanitize_pagina("https://evil.example/x") is None
    assert sanitize_pagina("//cdn.example") is None
    assert sanitize_pagina("/a b") is None
    assert sanitize_pagina(None) is None


def test_recado_rate_ok_caps_at_limit(monkeypatch):
    counts: dict[str, int] = {"n": 0}

    class Fake:
        def incr(self, _key: str) -> int:
            counts["n"] += 1
            return counts["n"]

        def expire(self, _key: str, _ttl: int) -> None:
            return None

    monkeypatch.setattr("app.recados.redis_client", lambda: Fake())
    previous = settings.recado_rate_limit_ip
    settings.recado_rate_limit_ip = 5
    try:
        for _ in range(5):
            assert recado_rate_ok("203.0.113.10") is True
        assert recado_rate_ok("203.0.113.10") is False
    finally:
        settings.recado_rate_limit_ip = previous


def test_recados_get_404_without_password():
    previous = settings.uso_password
    settings.uso_password = ""
    try:
        response = client.get("/api/recados")
        assert response.status_code == 404
    finally:
        settings.uso_password = previous


def test_recados_get_401_without_credentials():
    previous = settings.uso_password
    settings.uso_password = "segredo-teste"
    try:
        response = client.get("/api/recados")
        assert response.status_code == 401
        assert "Basic" in response.headers.get("www-authenticate", "")
    finally:
        settings.uso_password = previous


def test_recados_post_rejects_empty_fields():
    response = client.post(
        "/api/recados",
        json={"nome": "  ", "email": "pessoa@escola.edu.br", "mensagem": "Olá"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["titulo"] == "Preencha nome, e-mail e mensagem."


def test_recados_post_rejects_invalid_email():
    response = client.post(
        "/api/recados",
        json={"nome": "Ana", "email": "nao-e-email", "mensagem": "Olá"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["titulo"] == "Informe um e-mail válido."


def test_recados_post_rejects_too_long_nome():
    response = client.post(
        "/api/recados",
        json={"nome": "A" * 121, "email": "pessoa@escola.edu.br", "mensagem": "Olá"},
    )
    assert response.status_code == 422


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="needs database")
def test_recados_post_and_list():
    previous_password = settings.uso_password
    previous_user = settings.uso_user
    settings.uso_password = "segredo-teste"
    settings.uso_user = "uso"
    try:
        created = client.post(
            "/api/recados",
            json={
                "nome": " Ana ",
                "email": "Ana@Escola.edu.br",
                "mensagem": "O código EF05MA03 não abriu.",
                "pagina": "/habilidade/EF05MA03",
            },
        )
        assert created.status_code == 200
        assert created.json()["ok"] is True
        token = base64.b64encode(b"uso:segredo-teste").decode()
        listed = client.get("/api/recados", headers={"Authorization": f"Basic {token}"})
        assert listed.status_code == 200
        recados = listed.json()["recados"]
        assert recados
        first = recados[0]
        assert first["nome"] == "Ana"
        assert first["email"] == "ana@escola.edu.br"
        assert first["mensagem"] == "O código EF05MA03 não abriu."
        assert first["pagina"] == "/habilidade/EF05MA03"
        assert first["created_at"]
    finally:
        settings.uso_password = previous_password
        settings.uso_user = previous_user
