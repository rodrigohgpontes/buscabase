import base64
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import desc, select

from app.config import settings
from app.main import app
from app.privacy import device_class, referrer_host, visitor_day

client = TestClient(app)


def test_device_class_bot_mobile_desktop():
    assert device_class("Mozilla/5.0 Googlebot/2.1") == "bot"
    assert device_class("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)") == "mobile"
    assert device_class("Mozilla/5.0 (X11; Linux x86_64) Firefox/128.0") == "desktop"
    assert device_class(None) == "desktop"


def test_referrer_host_strips_origin_and_www():
    settings.public_origin = "https://www.buscabase.com.br"
    assert referrer_host("https://www.google.com/search?q=bncc") == "google.com"
    assert referrer_host("https://www.buscabase.com.br/?modo=buscar") is None
    assert referrer_host("https://instagram.com/") == "instagram.com"
    assert referrer_host(None) is None


def test_visitor_day_is_stable_for_same_inputs():
    first = visitor_day("203.0.113.10", "desktop")
    second = visitor_day("203.0.113.10", "desktop")
    other = visitor_day("203.0.113.11", "desktop")
    assert first == second
    assert first != other
    assert "203.0.113" not in first


def test_uso_404_without_password():
    previous = settings.uso_password
    settings.uso_password = ""
    try:
        response = client.get("/api/uso")
        assert response.status_code == 404
    finally:
        settings.uso_password = previous


def test_uso_401_without_credentials():
    previous = settings.uso_password
    settings.uso_password = "segredo-teste"
    try:
        response = client.get("/api/uso")
        assert response.status_code == 401
        assert "Basic" in response.headers.get("www-authenticate", "")
    finally:
        settings.uso_password = previous


def test_uso_401_wrong_password():
    previous_password = settings.uso_password
    previous_user = settings.uso_user
    settings.uso_password = "segredo-teste"
    settings.uso_user = "uso"
    try:
        token = base64.b64encode(b"uso:errado").decode()
        response = client.get("/api/uso", headers={"Authorization": f"Basic {token}"})
        assert response.status_code == 401
    finally:
        settings.uso_password = previous_password
        settings.uso_user = previous_user


def test_eventos_rejects_unknown_kind():
    response = client.post("/api/eventos", json={"kind": "heatmap"})
    assert response.status_code == 422


def test_eventos_accepts_copy_without_text():
    response = client.post(
        "/api/eventos",
        json={"kind": "copy", "copy_kind": "texto", "codigo": "EF05MA03"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_eventos_rejects_page_without_class():
    response = client.post("/api/eventos", json={"kind": "page"})
    assert response.status_code == 422


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="needs ingested snapshot")
def test_record_event_stores_query_text():
    from app.db import SessionLocal
    from app.models import UsageEvent
    from app.privacy import record_event

    record_event(kind="lookup", mode="codigo", query="EF05MA03", status_code=200, result_count=1)
    db = SessionLocal()
    try:
        row = db.execute(select(UsageEvent).order_by(desc(UsageEvent.id)).limit(1)).scalar_one()
        assert row.query == "EF05MA03"
        assert row.kind == "lookup"
    finally:
        db.close()


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="needs ingested snapshot")
def test_uso_200_with_basic():
    previous_password = settings.uso_password
    previous_user = settings.uso_user
    settings.uso_password = "segredo-teste"
    settings.uso_user = "uso"
    try:
        token = base64.b64encode(b"uso:segredo-teste").decode()
        response = client.get("/api/uso?dias=7", headers={"Authorization": f"Basic {token}"})
        assert response.status_code == 200
        body = response.json()
        assert "consultas" in body
        assert "como" in body
        assert "levar" in body
        assert "origem" in body
    finally:
        settings.uso_password = previous_password
        settings.uso_user = previous_user
