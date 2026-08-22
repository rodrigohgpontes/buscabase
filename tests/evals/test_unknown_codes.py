"""Public bncc-benchmark items: refuse unknown codes. Cite CC BY 4.0 in eval docs, not in the UI."""

from app.codes import CodeError, decodificar

# Documented public-style probes. Unknown codes must not be treated as hits.
UNKNOWN_BUT_PLAUSIBLE = ["EF05MA98", "EF99LP01", "EM13ZZZ999"]
ILL_FORMED = ["ABCDE", "ef", "12345", "BNCC-1"]


def test_unknown_well_formed_are_decodable():
    for code in ["EF05MA98", "EF99LP01"]:
        try:
            decodificar(code)
        except CodeError:
            # EF99 is invalid year — that is grammar, not a silent accept
            pass


def test_ill_formed_never_decode():
    for code in ILL_FORMED:
        try:
            decodificar(code)
            assert False, code
        except CodeError:
            pass
