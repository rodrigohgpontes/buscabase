"""Testes contra linhas reais do recorte quando DATABASE_URL está disponível.

Entradas sintéticas só para códigos malformados e lacunas oficiais da numeração.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HAS_DB = bool(os.environ.get("DATABASE_URL"))


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_lookup_ef05ma03():
    response = client.get("/api/codigos/EF05MA03")
    assert response.status_code == 200
    body = response.json()
    assert body["codigo"] == "EF05MA03"
    assert "Identificar e representar frações" in body["texto"]
    assert "bncc.dev" not in body["permalink"]


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_lookup_400_vs_404():
    bad = client.get("/api/codigos/XYZ")
    assert bad.status_code == 400
    gap = client.get("/api/codigos/EF05MA99")
    assert gap.status_code == 404
    detail = gap.json()["detail"]
    assert "formato válido" in detail["titulo"]


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_suggestions_after_two_chars():
    response = client.get("/api/sugestoes", params={"q": "EF"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert 1 <= len(items) <= 5
    assert all(item["codigo"].startswith("EF") for item in items)


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_suggestions_computacao_prefix():
    response = client.get("/api/sugestoes", params={"q": "CO"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all("CO" in item["codigo"] for item in items)


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_geografia_quinto_ano_is_catalog():
    response = client.get("/api/buscar", params={"q": "geografia no 5º ano"})
    assert response.status_code == 200
    body = response.json()
    assert 10 <= body["total"] <= 20
    assert body["items"]
    assert all(item.get("componente") == "Geografia" for item in body["items"])
    assert all((item.get("codigo") or "").startswith("EF05GE") for item in body["items"])


def test_search_lingua_portuguesa_excludes_ingles():
    response = client.get("/api/buscar", params={"q": "língua portuguesa 8º ano", "limit": 20})
    assert response.status_code == 200
    codes = [item["codigo"] for item in response.json()["items"]]
    assert codes
    assert not any(code.startswith("EF08LI") for code in codes)
    assert any(code.startswith("EF08LP") or "LP" in code for code in codes)


def test_search_fotossintese_setimo_ano_is_not_year_dump():
    response = client.get("/api/buscar", params={"q": "fotossíntese no 7º ano"})
    assert response.status_code == 200
    assert response.json()["total"] < 80


def test_search_fracoes():
    response = client.get("/api/buscar", params={"q": "frações no 5º ano"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    codes = [item["codigo"] for item in body["items"]]
    assert "EF05MA03" in codes or any(c.startswith("EF05MA") for c in codes)
    assert all(5 in (item.get("anos") or []) for item in body["items"])
    assert not any(c.startswith("EF06") for c in codes)
    assert body.get("trechos") == []


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_filters_without_query():
    empty = client.get("/api/buscar")
    assert empty.status_code == 400
    response = client.get("/api/buscar", params=[("etapa", "EF"), ("ano", "5")])
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["q"] == ""
    assert all(item.get("etapa") == "EF" for item in body["items"])
    assert all(5 in (item.get("anos") or []) for item in body["items"])
    blank_q = client.get("/api/buscar?etapa=EI&tipo=objetivo&q=")
    assert blank_q.status_code == 200
    ei = blank_q.json()
    assert ei["total"] >= 1
    assert all(item.get("etapa") == "EI" for item in ei["items"])
    assert all(item["tipo"] == "objetivo" for item in ei["items"])


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_ei_faixas_by_recorte_id():
    for recorte_id, prefix in (
        ("ei-grupo-01", "EI01"),
        ("ei-grupo-02", "EI02"),
        ("ei-grupo-03", "EI03"),
    ):
        response = client.get("/api/buscar", params=[("etapa", "EI"), ("ano", recorte_id)])
        assert response.status_code == 200, recorte_id
        body = response.json()
        assert body["total"] >= 1, recorte_id
        assert all(item["codigo"].startswith(prefix) for item in body["items"]), recorte_id


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_campo_e_documento():
    campo = client.get("/api/buscar", params=[("campo", "ei-campo-eo")])
    assert campo.status_code == 200
    campo_body = campo.json()
    assert campo_body["total"] >= 1
    assert all(item.get("unidade_ou_campo") for item in campo_body["items"])
    doc = client.get("/api/buscar", params=[("documento", "computacao-2022")])
    assert doc.status_code == 200
    assert doc.json()["total"] >= 1


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_competencia_geral_and_impossible_tipo():
    gerais = client.get("/api/buscar", params=[("tipo", "competencia_geral")])
    assert gerais.status_code == 200
    assert gerais.json()["total"] >= 1
    assert all(item["tipo"] == "competencia_geral" for item in gerais.json()["items"])
    with_etapa = client.get(
        "/api/buscar", params=[("etapa", "EI"), ("tipo", "competencia_geral")]
    )
    assert with_etapa.status_code == 200
    assert with_etapa.json()["total"] >= 1
    impossible = client.get("/api/buscar", params=[("etapa", "EI"), ("tipo", "habilidade")])
    assert impossible.status_code == 200
    assert impossible.json()["total"] == 0


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_search_conceptual_may_include_trechos():
    response = client.get("/api/buscar", params={"q": "competências gerais"})
    assert response.status_code == 200
    body = response.json()
    assert "trechos" in body
    assert len(body["trechos"]) <= 3
    for trecho in body["trechos"]:
        assert trecho["kind"] == "prose"
        assert trecho["block_id"]
        assert trecho["url_path"].startswith("/documento/")
        assert "#" in trecho["url_path"]


@pytest.mark.skipif(not HAS_DB, reason="needs ingested snapshot")
def test_prose_page_reading_order():
    meta = client.get("/api/prose/bncc-2018")
    if meta.status_code == 404:
        pytest.skip("prose corpus not loaded")
    assert meta.status_code == 200
    assert meta.json()["page_count"] == 600
    page = client.get("/api/prose/bncc-2018/paginas/1")
    assert page.status_code == 200
    body = page.json()
    assert body["page"] == 1
    seqs = [block["seq"] for block in body["blocks"]]
    assert seqs == sorted(seqs)
    assert all(block["id"] for block in body["blocks"])
