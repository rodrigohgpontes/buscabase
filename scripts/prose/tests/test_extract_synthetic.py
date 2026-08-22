import pytest

from scripts.prose.blocks import build_pages
from scripts.prose.extract import extract_document
from scripts.prose.normalize import bag_coverage, join_hyphenated
from scripts.prose.validate import reconstruct_page

fitz = pytest.importorskip("fitz")


def test_synthetic_page_roundtrip(tmp_path):
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "I – RELATÓRIO", fontsize=16)
    page.insert_text((72, 120), "A Base Nacional Comum Curricular define aprendizagens essenciais.", fontsize=11)
    page.insert_text((72, 160), "Art. 1º Esta Resolução entra em vigor.", fontsize=11)
    page.insert_text((300, 800), "1", fontsize=9)
    doc.save(path)
    doc.close()

    raw = extract_document(path)
    assert raw[0]["spans"]
    pages = build_pages("sample", raw)
    texts = [block["text"] for block in pages[0]["blocks"] if block["type"] != "figure"]
    joined = join_hyphenated(texts)
    assert "RELATÓRIO" in joined
    assert "aprendizagens essenciais" in joined
    assert bag_coverage("A Base Nacional Comum Curricular define aprendizagens essenciais.", reconstruct_page(pages[0])) >= 0.9
    types = {block["type"] for block in pages[0]["blocks"]}
    assert "article" in types or any(block["text"].startswith("Art.") for block in pages[0]["blocks"])
