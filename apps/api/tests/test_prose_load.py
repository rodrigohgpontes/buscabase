from app.ingest import sha_text
from app.prose import is_embeddable_block, prose_embed_text, restored_embedding
from app.prose_load import ARTE_DOCUMENTO, ARTE_ID


def test_arte_catalog_identity():
    assert ARTE_ID == "arte-2026"
    assert ARTE_DOCUMENTO["tipo"] == "complemento"
    assert ARTE_DOCUMENTO["derivado_de"] == "bncc-2018"
    assert ARTE_DOCUMENTO["slug"] == "arte-2026"


def test_skip_embed_types_and_empty_text():
    assert is_embeddable_block("running_header", "BNCC") is False
    assert is_embeddable_block("running_footer", "rodapé") is False
    assert is_embeddable_block("page_number", "12") is False
    assert is_embeddable_block("figure", "logo") is False
    assert is_embeddable_block("paragraph", "") is False
    assert is_embeddable_block("card", "Explorar sons") is True


def test_restored_embedding_keeps_matching_hash():
    texto_hash = sha_text("Explorar sons")
    previous = {"bncc-2018-p28-b8": (texto_hash, [0.1, 0.2], "google/gemini-embedding-001")}
    vector, model = restored_embedding(previous, "bncc-2018-p28-b8", texto_hash)
    assert vector == [0.1, 0.2]
    assert model == "google/gemini-embedding-001"


def test_restored_embedding_drops_changed_text():
    previous = {"bncc-2018-p28-b8": (sha_text("antigo"), [0.1], "modelo")}
    vector, model = restored_embedding(previous, "bncc-2018-p28-b8", sha_text("novo"))
    assert vector is None
    assert model is None


def test_prose_embed_text_includes_document_and_page():
    assert prose_embed_text("bncc-2018", 28, "Explorar sons") == "bncc-2018, p. 28. Explorar sons"
