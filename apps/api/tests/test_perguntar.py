from __future__ import annotations

from types import SimpleNamespace

from app.perguntar import (
    SYSTEM_PROMPT,
    allowed_codes_from_sources,
    build_messages,
    cited_codes,
    extract_codes,
    is_topic_shift,
    item_source_limit_for,
    merge_prose_blocks,
    merge_source_items,
    previous_history,
    prose_source_budget,
    retrieval_query,
    validate_codes,
)


def test_previous_history_keeps_eight_turns():
    history = [{"role": "user" if i % 2 == 0 else "assistant", "content": str(i)} for i in range(10)]
    kept = previous_history(history, "outra")
    assert len(kept) == 8
    assert kept[0]["content"] == "2"
    assert kept[-1]["content"] == "9"


def test_previous_history_drops_duplicate_current_question():
    history = [
        {"role": "user", "content": "Antes"},
        {"role": "assistant", "content": "Resposta"},
        {"role": "user", "content": "Compare frações"},
    ]
    assert previous_history(history, "Compare frações") == history[:-1]
    assert previous_history(history, "Outra") == history


def test_previous_history_accepts_text_alias_and_codigos():
    history = [
        {"role": "user", "text": "Explique EF05MA03"},
        {
            "role": "assistant",
            "content": "Frações [1].",
            "codigos": ["EF05MA03", "xyz", "EF05MA03"],
        },
    ]
    kept = previous_history(history, "e no 6º ano")
    assert kept[0]["content"] == "Explique EF05MA03"
    assert kept[1]["codigos"] == ["EF05MA03"]


def test_cited_codes_prefer_structured_then_text_and_keep_recent():
    history = [
        {"role": "user", "content": "Explique EF05MA03"},
        {"role": "assistant", "content": "Texto", "codigos": ["EF05MA03"]},
        {"role": "user", "content": "e EF06MA01?"},
        {"role": "assistant", "content": "A habilidade EF06MA01 [1]."},
    ]
    assert cited_codes(history, "e no 7º ano") == ["EF05MA03", "EF06MA01"]


def test_topic_shift_false_for_year_follow_up():
    history = [
        {"role": "user", "content": "Explique EF05MA03 em palavras mais simples"},
        {"role": "assistant", "content": "Frações no 5º ano.", "codigos": ["EF05MA03"]},
    ]
    assert is_topic_shift("e no 6º ano, o que muda?", history) is False
    assert is_topic_shift("explique melhor", history) is False
    assert is_topic_shift("quero saber sobre frações no 6º ano", history) is False


def test_topic_shift_true_for_new_subject():
    history = [
        {"role": "user", "content": "Explique EF05MA03 em palavras mais simples"},
        {"role": "assistant", "content": "Frações.", "codigos": ["EF05MA03"]},
    ]
    assert is_topic_shift("como a BNCC trata argumentação no Ensino Médio", history) is True


def test_retrieval_query_expands_follow_up_with_last_question_and_codes():
    history = [
        {"role": "user", "content": "Explique EF05MA03 em palavras mais simples"},
        {"role": "assistant", "content": "Frações [1].", "codigos": ["EF05MA03"]},
    ]
    query = retrieval_query("e no 6º ano, o que muda?", history)
    assert "Explique EF05MA03" in query
    assert "6º ano" in query
    assert "EF05MA03" in query


def test_retrieval_query_keeps_topic_shift_verbatim():
    history = [
        {"role": "user", "content": "Explique EF05MA03"},
        {"role": "assistant", "content": "Frações.", "codigos": ["EF05MA03"]},
    ]
    question = "como a BNCC trata argumentação no Ensino Médio"
    assert retrieval_query(question, history) == question


def test_merge_source_items_pins_cited_and_reserves_search_slots():
    pinned = [SimpleNamespace(codigo="EF05MA03"), SimpleNamespace(codigo="EF05MA04")]
    searched = [
        SimpleNamespace(codigo="EF06MA01"),
        SimpleNamespace(codigo="EF06MA02"),
        SimpleNamespace(codigo="EF05MA03"),
        SimpleNamespace(codigo="EF06MA03"),
        SimpleNamespace(codigo="EF06MA04"),
        SimpleNamespace(codigo="EF06MA05"),
    ]
    merged = merge_source_items(pinned, searched, limit=6)
    codes = [item.codigo for item in merged]
    assert codes[:2] == ["EF05MA03", "EF05MA04"]
    assert "EF06MA01" in codes
    assert len(codes) == 6
    assert len(set(codes)) == 6


def test_extract_codes_from_question():
    assert extract_codes("Explique EF05MA03 e ef06ma01") == ["EF05MA03", "EF06MA01"]


def test_build_messages_has_single_current_user_turn():
    sources = [
        {
            "codigo": "EF05MA03",
            "tipo_label": "Habilidade",
            "texto": "Resolver e elaborar problemas",
            "metadados_linha": "5º ano · Matemática",
            "documento": "BNCC",
            "recorte": "dados-2026.07.1",
        }
    ]
    history = [
        {"role": "user", "content": "Antes"},
        {"role": "assistant", "content": "Resposta"},
        {"role": "user", "content": "Explique EF05MA03"},
    ]
    messages = build_messages("Explique EF05MA03", history, sources)
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "Antes"}
    assert messages[2] == {"role": "assistant", "content": "Resposta"}
    assert messages[-1]["role"] == "user"
    assert "Explique EF05MA03" in messages[-1]["content"]
    assert "EF05MA03" in messages[-1]["content"]
    user_turns = [m for m in messages if m["role"] == "user"]
    assert len(user_turns) == 2


def test_build_messages_follow_up_keeps_prior_answer_and_notes_continuation():
    sources = [
        {
            "codigo": "EF05MA03",
            "tipo_label": "Habilidade",
            "texto": "Identificar frações",
            "metadados_linha": "5º ano · Matemática",
            "documento": "BNCC",
            "recorte": "dados-2026.07.1",
        }
    ]
    history = [
        {"role": "user", "content": "Explique EF05MA03"},
        {"role": "assistant", "content": "A habilidade trata de frações [1].", "codigos": ["EF05MA03"]},
    ]
    messages = build_messages("e no 6º ano, o que muda?", history, sources)
    assert messages[1]["content"] == "Explique EF05MA03"
    assert "frações" in messages[2]["content"]
    assert "Continue a conversa" in messages[-1]["content"]
    assert "e no 6º ano, o que muda?" in messages[-1]["content"]


def test_catalog_questions_raise_item_source_limit():
    assert item_source_limit_for("geografia no 5º ano") >= 12
    assert item_source_limit_for("língua portuguesa 8º ano") >= 12
    assert item_source_limit_for("frações no 5º ano") == 4
    assert "recorte pedido" in SYSTEM_PROMPT


def test_prose_source_budget_prefers_items_on_lookup():
    assert prose_source_budget("frações no 5º ano") == 1
    assert prose_source_budget("competências gerais") == 3


def test_merge_prose_blocks_skips_codes_already_in_items():
    items = [SimpleNamespace(codigo="EF05MA03")]
    blocks = [
        SimpleNamespace(id="bncc-2018-p28-b8", item_codigo="EF05MA03"),
        SimpleNamespace(id="bncc-2018-p12-b2", item_codigo=None),
        SimpleNamespace(id="arte-2026-p3-b1", item_codigo=None),
    ]
    merged = merge_prose_blocks(items, blocks, prose_cap=3, total_cap=6)
    assert [block.id for block in merged] == ["bncc-2018-p12-b2", "arte-2026-p3-b1"]


def test_merge_prose_blocks_respects_total_cap():
    items = [SimpleNamespace(codigo=f"I{i}") for i in range(5)]
    blocks = [SimpleNamespace(id=f"p{i}", item_codigo=None) for i in range(4)]
    merged = merge_prose_blocks(items, blocks, prose_cap=3, total_cap=6)
    assert len(merged) == 1


def test_allowed_codes_ignore_prose_item_codigo():
    sources = [
        {"kind": "item", "item": {"codigo": "EF05MA03"}},
        {
            "kind": "prose",
            "block_id": "bncc-2018-p28-b8",
            "item_codigo": "EF05MA99",
            "texto": "Explorar sons",
        },
    ]
    assert allowed_codes_from_sources(sources) == {"EF05MA03"}


def test_validate_codes_ignores_prose_only_codigo():
    db = SimpleNamespace()
    db.get = lambda *_args, **_kwargs: None
    text = validate_codes(db, "A Base cita EF05MA99 [1].", {"EF05MA03"})
    assert "EF05MA99" not in text
    assert "[código não confirmado]" in text


def test_build_messages_formats_prose_with_document_and_page():
    sources = [
        {
            "kind": "item",
            "item": {
                "codigo": "EF05MA03",
                "tipo_label": "Habilidade",
                "texto": "Resolver e elaborar problemas",
                "metadados_linha": "5º ano · Matemática",
                "documento": "BNCC",
                "recorte": "dados-2026.07.1",
            },
        },
        {
            "kind": "prose",
            "documento": "Normas complementares à BNCC — Arte",
            "page": 4,
            "texto": "A Arte na educação básica",
            "block_id": "arte-2026-p4-b2",
        },
    ]
    messages = build_messages("o que o parecer de Arte diz", [], sources)
    user = messages[-1]["content"]
    assert "Texto da BNCC" in user
    assert "Trecho oficial · Normas complementares à BNCC — Arte, p. 4" in user
    assert "Texto oficial (reconstrução): A Arte na educação básica" in user
    assert "não invente códigos" in SYSTEM_PROMPT.lower() or "Não invente códigos" in SYSTEM_PROMPT
