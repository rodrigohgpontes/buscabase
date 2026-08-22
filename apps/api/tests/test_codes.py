from app.codes import (
    CodeError,
    decodificar,
    looks_like_single_code,
    normalize_code,
    suggestion_like_patterns,
)


def test_normalize_spaces_and_case():
    assert normalize_code("ef 05 ma 03") == "EF05MA03"
    assert normalize_code("  Ei03Eo01 ") == "EI03EO01"


def test_decode_ef05ma03():
    data = decodificar("ef05ma03")
    assert data["codigo"] == "EF05MA03"
    assert data["etapa"] == "EF"
    assert data["anos"] == [5]
    assert data["componente"] == "MA"
    assert data["componente_nome"] == "Matemática"


def test_decode_ei_em_co():
    assert decodificar("EI03EO01")["etapa"] == "EI"
    assert decodificar("EM13CNT101")["area"] == "CNT"
    assert decodificar("EM13LP02")["componente"] == "LP"
    assert decodificar("EF01CO01")["componente"] == "CO"


def test_ill_formed_raises():
    try:
        decodificar("XYZ")
        assert False, "should raise"
    except CodeError:
        pass
    try:
        decodificar("EF99ZZ99")
        assert False, "should raise"
    except CodeError:
        pass


def test_official_gap_is_well_formed():
    """Códigos bem formados ainda podem não existir. A gramática deve aceitar EF05MA99."""
    data = decodificar("EF05MA99")
    assert data["codigo"] == "EF05MA99"


def test_suggestion_patterns_include_computacao_infix():
    assert suggestion_like_patterns("CO") == ["CO%", "EI__CO%", "EF__CO%", "EM13CO%"]
    assert suggestion_like_patterns("co01") == ["CO01%", "EI__CO01%", "EF__CO01%", "EM13CO01%"]
    assert suggestion_like_patterns("EF") == ["EF%"]
    assert suggestion_like_patterns("E") == []


def test_single_code_detection():
    assert looks_like_single_code("EF05MA03")
    assert not looks_like_single_code("frações no 5º ano")
