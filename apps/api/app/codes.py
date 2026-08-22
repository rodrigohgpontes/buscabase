"""Gramática dos códigos da BNCC, a partir de bncc-dados pipeline/codigos.py (MIT).

Um código bem formado ainda pode não existir: a numeração oficial tem lacunas legítimas.
"""

from __future__ import annotations

import re
import unicodedata

CAMPOS_EI = {
    "EO": "O eu, o outro e o nós",
    "CG": "Corpo, gestos e movimentos",
    "TS": "Traços, sons, cores e formas",
    "EF": "Escuta, fala, pensamento e imaginação",
    "ET": "Espaços, tempos, quantidades, relações e transformações",
}
GRUPOS_EI = {
    "01": "Bebês (0–1a6m)",
    "02": "Crianças bem pequenas (1a7m–3a11m)",
    "03": "Crianças pequenas (4a–5a11m)",
}
COMPONENTES_EF = {
    "AR": "Arte",
    "CI": "Ciências",
    "EF": "Educação Física",
    "ER": "Ensino Religioso",
    "GE": "Geografia",
    "HI": "História",
    "LI": "Língua Inglesa",
    "LP": "Língua Portuguesa",
    "MA": "Matemática",
}
BLOCOS_EF = {
    "15": [1, 2, 3, 4, 5],
    "69": [6, 7, 8, 9],
    "12": [1, 2],
    "35": [3, 4, 5],
    "67": [6, 7],
    "89": [8, 9],
}
BLOCOS_VALIDOS_POR_COMPONENTE = {
    "AR": {"15", "69"},
    "LP": {"15", "69", "12", "35", "67", "89"},
    "EF": {"12", "35", "67", "89"},
}
AREAS_EM = {
    "LGG": "Linguagens e suas Tecnologias",
    "MAT": "Matemática e suas Tecnologias",
    "CNT": "Ciências da Natureza e suas Tecnologias",
    "CHS": "Ciências Humanas e Sociais Aplicadas",
}

PREFIX_OK = re.compile(r"^(EI|EF|EM|CO)")
_ETAPA_TYPED = ("EI", "EF", "EM")


class CodeError(ValueError):
    """Código malformado (HTTP 400)."""


def normalize_code(raw: str) -> str:
    collapsed = re.sub(r"[^A-Za-z0-9]+", "", unicodedata.normalize("NFKC", raw or ""))
    return collapsed.upper()


def alphanumeric_prefix_len(raw: str) -> int:
    return len(normalize_code(raw))


def suggestion_like_patterns(raw: str) -> list[str]:
    """SQL LIKE patterns for typed code prefixes.

    Official codes start with EI, EF or EM. Computação (CO) and other
    componentes sit after the year: EF05CO01, EI03CO01, EM13CO01.
    """
    prefix = normalize_code(raw)
    if len(prefix) < 2:
        return []
    patterns = [f"{prefix}%"]
    if not prefix.startswith(_ETAPA_TYPED):
        patterns.extend([f"EI__{prefix}%", f"EF__{prefix}%", f"EM13{prefix}%"])
    return patterns


def decodificar(codigo: str) -> dict:
    codigo = normalize_code(codigo)
    if not codigo:
        raise CodeError("vazio")

    m = re.fullmatch(r"EI03CO(\d{2})", codigo)
    if m:
        return {
            "codigo": codigo,
            "etapa": "EI",
            "grupo_etario": "03",
            "grupo_etario_nome": GRUPOS_EI["03"],
            "componente": "CO",
            "componente_nome": "Computação",
            "documento": "computacao-2022",
            "sequencia": int(m.group(1)),
            "tipo_esperado": "objetivo",
        }

    m = re.fullmatch(r"EF(\d{2})CO(\d{2})", codigo)
    if m:
        anos_str, seq = m.groups()
        if anos_str in ("15", "69"):
            anos = BLOCOS_EF[anos_str]
        elif anos_str.startswith("0") and 1 <= int(anos_str) <= 9:
            anos = [int(anos_str)]
        else:
            raise CodeError(f"{codigo}: ano/bloco {anos_str!r} inválido para Computação")
        return {
            "codigo": codigo,
            "etapa": "EF",
            "anos": anos,
            "bloco": anos_str in BLOCOS_EF,
            "componente": "CO",
            "componente_nome": "Computação",
            "documento": "computacao-2022",
            "sequencia": int(seq),
            "tipo_esperado": "habilidade",
        }

    m = re.fullmatch(r"EM13CO(\d{2})", codigo)
    if m:
        return {
            "codigo": codigo,
            "etapa": "EM",
            "seriacao": None,
            "componente": "CO",
            "componente_nome": "Computação",
            "documento": "computacao-2022",
            "sequencia": int(m.group(1)),
            "tipo_esperado": "habilidade",
        }

    m = re.fullmatch(r"EI(0[123])(EO|CG|TS|EF|ET)(\d{2})", codigo)
    if m:
        grupo, campo, seq = m.groups()
        return {
            "codigo": codigo,
            "etapa": "EI",
            "grupo_etario": grupo,
            "grupo_etario_nome": GRUPOS_EI[grupo],
            "campo_experiencias": campo,
            "campo_experiencias_nome": CAMPOS_EI[campo],
            "sequencia": int(seq),
            "tipo_esperado": "objetivo",
        }

    m = re.fullmatch(r"EF(\d{2})([A-Z]{2})(\d{2})", codigo)
    if m:
        anos_str, comp, seq = m.groups()
        if comp not in COMPONENTES_EF:
            raise CodeError(f"{codigo}: componente {comp!r} desconhecido")
        if anos_str in BLOCOS_EF:
            if anos_str not in BLOCOS_VALIDOS_POR_COMPONENTE.get(comp, set()):
                raise CodeError(
                    f"{codigo}: bloco {anos_str!r} inválido para {COMPONENTES_EF[comp]}"
                )
            anos = BLOCOS_EF[anos_str]
        elif anos_str.startswith("0") and 1 <= int(anos_str) <= 9:
            anos = [int(anos_str)]
        else:
            raise CodeError(f"{codigo}: ano/bloco {anos_str!r} inválido")
        return {
            "codigo": codigo,
            "etapa": "EF",
            "anos": anos,
            "bloco": anos_str in BLOCOS_EF,
            "componente": comp,
            "componente_nome": COMPONENTES_EF[comp],
            "sequencia": int(seq),
            "tipo_esperado": "habilidade",
        }

    m = re.fullmatch(r"EM13([A-Z]{3})(\d)(\d{2})", codigo)
    if m and m.group(1) in AREAS_EM:
        area, ce, seq = m.groups()
        return {
            "codigo": codigo,
            "etapa": "EM",
            "seriacao": None,
            "area": area,
            "area_nome": AREAS_EM[area],
            "competencia_especifica": int(ce),
            "sequencia": int(seq),
            "tipo_esperado": "habilidade",
        }

    m = re.fullmatch(r"EM13LP(\d{2})", codigo)
    if m:
        return {
            "codigo": codigo,
            "etapa": "EM",
            "seriacao": None,
            "area": "LGG",
            "area_nome": AREAS_EM["LGG"],
            "componente": "LP",
            "competencia_especifica": None,
            "sequencia": int(m.group(1)),
            "tipo_esperado": "habilidade",
        }

    raise CodeError(f"{codigo}: não corresponde a nenhuma gramática BNCC (EI/EF/EM)")


def looks_like_single_code(query: str) -> bool:
    try:
        decodificar(query)
        return True
    except CodeError:
        return False
