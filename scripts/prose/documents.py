"""Pinned official PDFs for the prose extract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DocumentSpec:
    id: str
    arquivo: str
    sha256: str
    page_count: int
    data_version: str
    source: str
    needs_ghostscript: bool = False
    local_path: Path | None = None
    nome: str | None = None
    tipo: str = "documento"
    derivado_de: str | None = None


DOCUMENTS: tuple[DocumentSpec, ...] = (
    DocumentSpec(
        id="bncc-2018",
        arquivo="Base-Nacional-Comum-Curricular-BNCC.pdf",
        sha256="81cd44ba5444ff1e8ff7b82d83512a49de9ce54efa72c4d285a452d3321128a4",
        page_count=600,
        data_version="dados-2026.07.1",
        source="bncc-dados",
        nome="Base Nacional Comum Curricular",
    ),
    DocumentSpec(
        id="computacao-2022",
        arquivo="anexo-ao-parecer-cneceb-no-2-2022-bncc-computacao.pdf",
        sha256="b0f021db3c7c2c042b821cec5fab7d77ed1888dbb61590461ce2afef404865b7",
        page_count=75,
        data_version="dados-2026.07.1",
        source="bncc-dados",
        needs_ghostscript=True,
        nome="Computação na Educação Básica (complemento à BNCC)",
        tipo="complemento",
        derivado_de="bncc-2018",
    ),
    DocumentSpec(
        id="arte-2026",
        arquivo="pceb002_26.pdf",
        sha256="a424936c08b90cf060c6cb4224d21e5e204c7acf3cdda32d8aea4673b7a38c23",
        page_count=54,
        data_version="local-pceb002-26",
        source="local",
        local_path=REPO_ROOT / "research" / "pceb002_26.pdf",
        nome="Normas complementares à BNCC — Arte (Parecer CNE/CEB nº 2/2026)",
        tipo="complemento",
        derivado_de="bncc-2018",
    ),
)

ARTE_PAYLOAD = {
    "parecer": "CNE/CEB nº 2/2026",
    "processo": "23001.000221/2022-97",
    "aprovado_em": "2026-03-19",
    "homologacao": "DOU 18/8/2026, Seção 1, pág. 73",
    "arquivo": "pceb002_26.pdf",
    "sha256": "a424936c08b90cf060c6cb4224d21e5e204c7acf3cdda32d8aea4673b7a38c23",
    "page_count": 54,
    "proveniencia": "research/pceb002_26.pdf",
}

# bncc-dados visual exceptions: PDF text layer loses a glyph; do not fail coverage.
GLYPH_ALLOWLIST = {
    "bncc-2018": {"π", "pi"},
}


def by_id(documento_id: str) -> DocumentSpec:
    for spec in DOCUMENTS:
        if spec.id == documento_id:
            return spec
    raise KeyError(documento_id)
