from app.retrieval import (
    SearchFilters,
    grupo_etario_code_prefix,
    has_scope,
    inferred_labels,
    is_catalog_query,
    is_item_lookup_query,
    merge_filters,
    parse_search_query,
    rrf_merge,
    wants_prose_strip,
)
from app.prose import SKIP_EMBED_TYPES, STRIP_TYPES, is_embeddable_block


def test_parse_fracoes_no_quinto_ano():
    text, filters = parse_search_query("frações no 5º ano")
    assert text.lower() == "frações"
    assert filters.anos == [5]
    assert filters.etapas == ["EF"]


def test_parse_fracoes_ascii_and_ordinal_word():
    text, filters = parse_search_query("fracoes 5 ano")
    assert "fraco" in text.lower() or text.lower() == "fracoes"
    assert filters.anos == [5]

    text, filters = parse_search_query("habilidades de frações no quinto ano")
    assert text.lower() == "frações"
    assert filters.anos == [5]


def test_parse_quinto_e_sexto():
    _text, filters = parse_search_query("frações no 5º e no 6º ano")
    assert filters.anos == [5, 6]


def test_parse_ensino_medio():
    text, filters = parse_search_query("argumentação no Ensino Médio")
    assert "argument" in text.lower()
    assert filters.etapas == ["EM"]
    assert filters.anos is None


def test_explicit_filters_win():
    inferred = SearchFilters(anos=[5], etapas=["EF"], componentes=["ef-comp-ge"], areas=["em-area-cnt"])
    explicit = SearchFilters(anos=["ef-ano-06"], etapas=["EF"])
    merged = merge_filters(explicit, inferred)
    assert merged.anos == ["ef-ano-06"]
    assert merged.componentes == ["ef-comp-ge"]
    assert merged.areas == ["em-area-cnt"]


def test_parse_geografia_no_quinto_ano():
    for query in ("geografia no 5o ano", "geografia no 5º ano", "habilidades de geografia no quinto ano"):
        text, filters = parse_search_query(query)
        assert text == ""
        assert filters.anos == [5]
        assert filters.etapas == ["EF"]
        assert filters.componentes == ["ef-comp-ge"]


def test_parse_portugues_not_ingles():
    text, filters = parse_search_query("português no 8º ano")
    assert text == ""
    assert filters.anos == [8]
    assert filters.componentes == ["ef-comp-lp"]
    assert "ef-comp-li" not in (filters.componentes or [])


def test_parse_educacao_fisica():
    text, filters = parse_search_query("educação física 2º ano")
    assert text == ""
    assert filters.anos == [2]
    assert filters.componentes == ["ef-comp-ef"]


def test_parse_biologia_ensino_medio_uses_area():
    text, filters = parse_search_query("biologia no ensino médio")
    assert text == ""
    assert filters.etapas == ["EM"]
    assert filters.areas == ["em-area-cnt"]
    assert filters.componentes is None


def test_parse_competencias_gerais():
    text, filters = parse_search_query("competências gerais")
    assert text == ""
    assert filters.tipos == ["competencia_geral"]


def test_parse_fracoes_does_not_infer_componente():
    text, filters = parse_search_query("frações no 5º ano")
    assert text.lower() == "frações"
    assert filters.componentes is None
    assert filters.anos == [5]


def test_parse_geografia_e_historia():
    _text, filters = parse_search_query("geografia e história no 5º ano")
    assert filters.anos == [5]
    assert set(filters.componentes or []) == {"ef-comp-ge", "ef-comp-hi"}


def test_is_catalog_query():
    assert is_catalog_query("geografia no 5º ano") is True
    assert is_catalog_query("competências gerais") is True
    assert is_catalog_query("frações no 5º ano") is False
    assert is_catalog_query("5º ano") is False


def test_inferred_labels_for_chips():
    labels = inferred_labels("geografia no 5º ano")
    kinds = {item["kind"] for item in labels}
    assert "ano" in kinds
    assert "componente" in kinds
    assert any(item["id"] == "ef-comp-ge" for item in labels)


def test_has_scope():
    assert not has_scope(SearchFilters())
    assert has_scope(SearchFilters(etapas=["EF"]))
    assert has_scope(SearchFilters(anos=[5]))
    assert has_scope(SearchFilters(campos=["ei-campo-eo"]))
    assert not has_scope(SearchFilters(incluir_revogados=True))


def test_grupo_etario_code_prefix():
    assert grupo_etario_code_prefix("ei-grupo-01") == "EI01"
    assert grupo_etario_code_prefix("ei-grupo-02") == "EI02"
    assert grupo_etario_code_prefix("ei-grupo-03") == "EI03"
    assert grupo_etario_code_prefix("ef-ano-05") is None


def test_item_lookup_query_signals():
    assert is_item_lookup_query("frações no 5º ano") is True
    assert is_item_lookup_query("EF05MA03") is True
    assert is_item_lookup_query("competências gerais") is False
    assert is_item_lookup_query("o que o parecer de Arte diz") is False
    assert is_item_lookup_query("argumentação no Ensino Médio") is False
    assert is_item_lookup_query("frações", SearchFilters(anos=[5])) is True
    assert is_item_lookup_query("frações", SearchFilters(componentes=["matematica"])) is True


def test_wants_prose_strip():
    assert wants_prose_strip("competências gerais") is False
    assert wants_prose_strip("o que o parecer de Arte diz") is True
    assert wants_prose_strip("frações no 5º ano") is False
    assert wants_prose_strip("EF05MA03") is False
    assert wants_prose_strip("competências gerais", offset=20) is False
    assert wants_prose_strip("competências gerais", atalho_codigo=True) is False
    assert wants_prose_strip("BNCC") is False


def test_chrome_types_are_not_embeddable():
    for block_type in SKIP_EMBED_TYPES:
        assert is_embeddable_block(block_type, "texto") is False
    assert is_embeddable_block("paragraph", "") is False
    assert is_embeddable_block("paragraph", "  ") is False
    assert is_embeddable_block("paragraph", "os fundamentos") is True
    assert "figure" not in STRIP_TYPES
    assert "card" in STRIP_TYPES


def test_rrf_prose_ids_do_not_collide_with_item_codes():
    merged = rrf_merge(["EF05MA03", "bncc-2018-p28-b8"], ["bncc-2018-p28-b8"])
    assert "bncc-2018-p28-b8" in merged
    assert "EF05MA03" in merged
    assert merged[0] == "bncc-2018-p28-b8"
