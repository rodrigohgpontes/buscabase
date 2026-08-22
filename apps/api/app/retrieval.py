from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

from sqlalchemy import Text, and_, func, or_, select
from sqlalchemy.orm import Session

from app.codes import (
    CAMPOS_EI,
    CodeError,
    decodificar,
    looks_like_single_code,
    normalize_code,
    suggestion_like_patterns,
)
from app.config import settings
from app.ml import embed_texts, rerank
from app.models import Area, Componente, Item, ProseBlock, Recorte, Snapshot
from app.prose import SKIP_EMBED_TYPES

_ORDINAL_WORDS = {
    "primeiro": 1,
    "primeira": 1,
    "segundo": 2,
    "segunda": 2,
    "terceiro": 3,
    "terceira": 3,
    "quarto": 4,
    "quarta": 4,
    "quinto": 5,
    "quinta": 5,
    "sexto": 6,
    "sexta": 6,
    "setimo": 7,
    "setima": 7,
    "oitavo": 8,
    "oitava": 8,
    "nono": 9,
    "nona": 9,
}
_YEAR_ANO_RE = re.compile(
    r"(?i)(?:\b(?:no|na|nos|nas|do|da|dos|das|em|de|para(?:\s+o)?)\s+)?"
    r"(\d{1,2})\s*[ºo°ª]?\s*anos?\b"
)
_YEAR_ORDINAL_WORD_RE = re.compile(
    r"(?i)(?:\b(?:no|na|nos|nas|do|da|dos|das|em|de|para(?:\s+o)?)\s+)?"
    r"(primeiro|primeira|segundo|segunda|terceiro|terceira|quarto|quarta|"
    r"quinto|quinta|sexto|sexta|s[eé]timo|s[eé]tima|oitavo|oitava|nono|nona)"
    r"\s+anos?\b"
)
_ORPHAN_ORDINAL_RE = re.compile(r"(?i)(\d{1,2})\s*[ºo°ª]")
_ETAPA_RE = re.compile(
    r"(?i)(?:\b(?:no|na|do|da|em|de)\s+)?("
    r"ensino\s+m[eé]dio|"
    r"ensino\s+fundamental|"
    r"educa[cç][aã]o\s+infantil"
    r")\b"
)
_NOISE_RE = re.compile(
    r"(?i)\b("
    r"habilidades?|objetivos?(?:\s+de\s+aprendizagem(?:\s+e\s+desenvolvimento)?)?|"
    r"compet[eê]ncias?|itens?|c[oó]digos?|bncc|"
    r"base(?:\s+nacional(?:\s+comum(?:\s+curricular)?)?)?|"
    r"o\s+que|aprende[mn]?|ensina[mn]?|sobre|quais|qual|como"
    r")\b"
)
_STOP_RE = re.compile(
    r"(?i)\b(?:no|na|nos|nas|do|da|dos|das|de|em|para|pelo|pela|e|ou|a|o|as|os)\b"
)
_DENSE_EXPAND = 8
_RELATED_WHEN_EMPTY = 5
_CAMPO_CODE = {
    "ei-campo-eo": "EO",
    "ei-campo-cg": "CG",
    "ei-campo-ts": "TS",
    "ei-campo-ef": "EF",
    "ei-campo-et": "ET",
}


_GRUPO_ETARIO_ID_RE = re.compile(r"(?i)^ei-grupo-(0[123])$")


@dataclass
class SearchFilters:
    etapas: list[str] | None = None
    anos: list[int] | list[str] | None = None
    componentes: list[str] | None = None
    documentos: list[str] | None = None
    areas: list[str] | None = None
    campos: list[str] | None = None
    tipos: list[str] | None = None
    incluir_revogados: bool = False


@dataclass(frozen=True)
class InferredLabel:
    kind: str
    id: str
    label: str
    phrase: str


@dataclass(frozen=True)
class _GazetteerEntry:
    phrases: tuple[str, ...]
    label: str
    kind: str
    ef_componente: str | None = None
    em_componente: str | None = None
    ef_area: str | None = None
    em_area: str | None = None
    tipo: str | None = None
    documento: str | None = None
    campo: str | None = None
    em_only: bool = False


_GAZETTEER: tuple[_GazetteerEntry, ...] = (
    _GazetteerEntry(
        ("ciencias da natureza e suas tecnologias",),
        "Ciências da Natureza e suas Tecnologias",
        "area",
        em_area="em-area-cnt",
    ),
    _GazetteerEntry(
        ("ciencias humanas e sociais aplicadas",),
        "Ciências Humanas e Sociais Aplicadas",
        "area",
        em_area="em-area-chs",
    ),
    _GazetteerEntry(
        ("matematica e suas tecnologias",),
        "Matemática e suas Tecnologias",
        "area",
        em_area="em-area-mat",
    ),
    _GazetteerEntry(
        ("linguagens e suas tecnologias",),
        "Linguagens e suas Tecnologias",
        "area",
        em_area="em-area-lgg",
    ),
    _GazetteerEntry(
        ("ciencias da natureza",),
        "Ciências da Natureza",
        "area",
        ef_area="ef-area-ciencias-da-natureza",
        em_area="em-area-cnt",
    ),
    _GazetteerEntry(
        ("ciencias humanas",),
        "Ciências Humanas",
        "area",
        ef_area="ef-area-ciencias-humanas",
        em_area="em-area-chs",
    ),
    _GazetteerEntry(
        ("lingua portuguesa", "portugues"),
        "Língua Portuguesa",
        "componente",
        ef_componente="ef-comp-lp",
        em_componente="em-comp-lp",
    ),
    _GazetteerEntry(
        ("lingua inglesa", "ingles"),
        "Língua Inglesa",
        "componente",
        ef_componente="ef-comp-li",
    ),
    _GazetteerEntry(
        ("educacao fisica", "ed fisica"),
        "Educação Física",
        "componente",
        ef_componente="ef-comp-ef",
    ),
    _GazetteerEntry(
        ("ensino religioso",),
        "Ensino Religioso",
        "componente",
        ef_componente="ef-comp-er",
    ),
    _GazetteerEntry(
        ("o eu o outro e o nos",),
        "O eu, o outro e o nós",
        "campo",
        campo="ei-campo-eo",
    ),
    _GazetteerEntry(
        ("corpo gestos e movimentos",),
        "Corpo, gestos e movimentos",
        "campo",
        campo="ei-campo-cg",
    ),
    _GazetteerEntry(
        ("tracos sons cores e formas",),
        "Traços, sons, cores e formas",
        "campo",
        campo="ei-campo-ts",
    ),
    _GazetteerEntry(
        ("escuta fala pensamento e imaginacao",),
        "Escuta, fala, pensamento e imaginação",
        "campo",
        campo="ei-campo-ef",
    ),
    _GazetteerEntry(
        ("espacos tempos quantidades relacoes e transformacoes",),
        "Espaços, tempos, quantidades, relações e transformações",
        "campo",
        campo="ei-campo-et",
    ),
    _GazetteerEntry(
        ("competencias gerais", "competencia geral"),
        "Competência geral",
        "tipo",
        tipo="competencia_geral",
    ),
    _GazetteerEntry(
        ("computacao", "informatica"),
        "Computação",
        "documento",
        documento="computacao-2022",
    ),
    _GazetteerEntry(
        ("geografia",),
        "Geografia",
        "componente",
        ef_componente="ef-comp-ge",
        em_area="em-area-chs",
    ),
    _GazetteerEntry(
        ("historia",),
        "História",
        "componente",
        ef_componente="ef-comp-hi",
        em_area="em-area-chs",
    ),
    _GazetteerEntry(
        ("matematica",),
        "Matemática",
        "componente",
        ef_componente="ef-comp-ma",
        em_area="em-area-mat",
    ),
    _GazetteerEntry(
        ("ciencias",),
        "Ciências",
        "componente",
        ef_componente="ef-comp-ci",
        em_area="em-area-cnt",
    ),
    _GazetteerEntry(("arte", "artes"), "Arte", "componente", ef_componente="ef-comp-ar"),
    _GazetteerEntry(
        ("biologia",),
        "Biologia",
        "componente",
        em_area="em-area-cnt",
        em_only=True,
    ),
    _GazetteerEntry(
        ("quimica",),
        "Química",
        "componente",
        em_area="em-area-cnt",
        em_only=True,
    ),
    _GazetteerEntry(
        ("filosofia",),
        "Filosofia",
        "componente",
        em_area="em-area-chs",
        em_only=True,
    ),
    _GazetteerEntry(
        ("sociologia",),
        "Sociologia",
        "componente",
        em_area="em-area-chs",
        em_only=True,
    ),
    _GazetteerEntry(
        ("fisica",),
        "Física",
        "componente",
        em_area="em-area-cnt",
        em_only=True,
    ),
)


def grupo_etario_code_prefix(recorte_id: str) -> str | None:
    match = _GRUPO_ETARIO_ID_RE.match(recorte_id or "")
    return f"EI{match.group(1)}" if match else None


def recorte_item_clauses(rec: Recorte):
    clauses = [Item.recorte_id == rec.id]
    if rec.anos:
        year_match = Item.anos.overlap(list(rec.anos))
        if rec.etapa_id:
            year_match = and_(year_match, Item.etapa == rec.etapa_id)
        clauses.append(year_match)
    elif rec.tipo == "sem_seriacao" and rec.etapa_id:
        clauses.append(and_(Item.etapa == rec.etapa_id, Item.anos.is_(None)))
    prefix = grupo_etario_code_prefix(rec.id)
    if rec.tipo == "grupo_etario" and prefix:
        clauses.append(Item.codigo.startswith(prefix))
    return clauses


def _fold_key(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _fold_with_map(text: str) -> tuple[str, list[int]]:
    folded: list[str] = []
    index_map: list[int] = []
    for index, char in enumerate(text):
        for sub in unicodedata.normalize("NFKD", char.lower()):
            if unicodedata.combining(sub):
                continue
            token = sub if sub.isalnum() else " "
            if token == " " and (not folded or folded[-1] == " "):
                continue
            folded.append(token)
            index_map.append(index)
    while folded and folded[-1] == " ":
        folded.pop()
        index_map.pop()
    return "".join(folded), index_map


def _etapa_code(phrase: str) -> str:
    folded = _fold_key(phrase)
    if "medio" in folded:
        return "EM"
    if "fundamental" in folded:
        return "EF"
    return "EI"


def _clean_remaining(text: str) -> str:
    text = _STOP_RE.sub(" ", text)
    text = re.sub(r"[^\wÀ-ÿ]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _word_boundary(folded: str, start: int, end: int) -> bool:
    if start > 0 and folded[start - 1].isalnum():
        return False
    if end < len(folded) and folded[end].isalnum():
        return False
    return True


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _resolve_entry(
    entry: _GazetteerEntry,
    etapas: list[str],
    anos: list[int],
) -> tuple[list[str], list[str], list[str], list[str], list[str], list[InferredLabel]]:
    em = "EM" in etapas
    ef = "EF" in etapas or bool(anos)
    if entry.em_only and anos and not em:
        return [], [], [], [], [], []

    componentes: list[str] = []
    areas: list[str] = []
    tipos: list[str] = []
    documentos: list[str] = []
    campos: list[str] = []
    labels: list[InferredLabel] = []

    if entry.tipo:
        tipos.append(entry.tipo)
        labels.append(InferredLabel("tipo", entry.tipo, entry.label, entry.label))
    if entry.documento:
        documentos.append(entry.documento)
        labels.append(InferredLabel("documento", entry.documento, entry.label, entry.label))
    if entry.campo:
        campos.append(entry.campo)
        labels.append(InferredLabel("campo", entry.campo, entry.label, entry.label))

    chosen_ids: list[tuple[str, str]] = []
    if em and not anos:
        if entry.em_componente:
            componentes.append(entry.em_componente)
            chosen_ids.append(("componente", entry.em_componente))
        elif entry.em_area:
            areas.append(entry.em_area)
            chosen_ids.append(("area", entry.em_area))
        elif entry.ef_componente:
            componentes.append(entry.ef_componente)
            chosen_ids.append(("componente", entry.ef_componente))
    elif ef:
        if entry.ef_componente:
            componentes.append(entry.ef_componente)
            chosen_ids.append(("componente", entry.ef_componente))
        elif entry.ef_area:
            areas.append(entry.ef_area)
            chosen_ids.append(("area", entry.ef_area))
    else:
        if entry.ef_componente:
            componentes.append(entry.ef_componente)
            chosen_ids.append(("componente", entry.ef_componente))
        if entry.em_componente:
            componentes.append(entry.em_componente)
            chosen_ids.append(("componente", entry.em_componente))
        if entry.em_only and entry.em_area:
            areas.append(entry.em_area)
            chosen_ids.append(("area", entry.em_area))
        if entry.ef_area and not entry.ef_componente:
            areas.append(entry.ef_area)
            chosen_ids.append(("area", entry.ef_area))

    if not labels:
        for kind, identifier in chosen_ids:
            labels.append(InferredLabel(kind, identifier, entry.label, entry.label))
    return componentes, areas, tipos, documentos, campos, labels


def _extract_taxonomy(
    text: str, etapas: list[str], anos: list[int]
) -> tuple[str, SearchFilters, list[InferredLabel]]:
    folded, index_map = _fold_with_map(text)
    occupied = [False] * len(folded)
    phrases = []
    for entry in _GAZETTEER:
        for phrase in sorted(entry.phrases, key=len, reverse=True):
            phrases.append((phrase, entry))
    phrases.sort(key=lambda item: len(item[0]), reverse=True)

    componentes: list[str] = []
    areas: list[str] = []
    tipos: list[str] = []
    documentos: list[str] = []
    campos: list[str] = []
    labels: list[InferredLabel] = []
    remove: list[tuple[int, int]] = []

    for phrase, entry in phrases:
        start = 0
        while True:
            index = folded.find(phrase, start)
            if index < 0:
                break
            end = index + len(phrase)
            if _word_boundary(folded, index, end) and not any(occupied[index:end]):
                resolved = _resolve_entry(entry, etapas, anos)
                extra_comp, extra_area, extra_tipo, extra_doc, extra_campo, extra_labels = resolved
                if extra_comp or extra_area or extra_tipo or extra_doc or extra_campo:
                    componentes.extend(extra_comp)
                    areas.extend(extra_area)
                    tipos.extend(extra_tipo)
                    documentos.extend(extra_doc)
                    campos.extend(extra_campo)
                    orig_start = index_map[index]
                    orig_end = index_map[end - 1] + 1
                    phrase_text = text[orig_start:orig_end].strip()
                    labels.extend(
                        InferredLabel(label.kind, label.id, label.label, phrase_text)
                        for label in extra_labels
                    )
                    for pos in range(index, end):
                        occupied[pos] = True
                    remove.append((orig_start, orig_end))
                start = end
            else:
                start = index + 1

    remaining = text
    for start, end in sorted(remove, reverse=True):
        remaining = remaining[:start] + " " + remaining[end:]
    return remaining, SearchFilters(
        componentes=_unique(componentes) or None,
        areas=_unique(areas) or None,
        tipos=_unique(tipos) or None,
        documentos=_unique(documentos) or None,
        campos=_unique(campos) or None,
    ), labels


def parse_search_query(query: str) -> tuple[str, SearchFilters]:
    """Tira ano, etapa e componente da pergunta e deixa o tema para o FTS."""
    leftover, filters, _labels = parse_search_details(query)
    return leftover, filters


def parse_search_details(query: str) -> tuple[str, SearchFilters, list[InferredLabel]]:
    """Como parse_search_query, com os recortes inferidos para a interface."""
    anos: list[int] = []
    etapas: list[str] = []
    labels: list[InferredLabel] = []
    remaining = query

    def take_year(match: re.Match[str]) -> str:
        n = int(match.group(1))
        if 1 <= n <= 9:
            anos.append(n)
            labels.append(InferredLabel("ano", str(n), f"{n}º ano", match.group(0).strip()))
            return " "
        return match.group(0)

    remaining = _YEAR_ANO_RE.sub(take_year, remaining)

    def take_ordinal_word(match: re.Match[str]) -> str:
        n = _ORDINAL_WORDS.get(_fold_key(match.group(1)))
        if n:
            anos.append(n)
            labels.append(InferredLabel("ano", str(n), f"{n}º ano", match.group(0).strip()))
            return " "
        return match.group(0)

    remaining = _YEAR_ORDINAL_WORD_RE.sub(take_ordinal_word, remaining)

    if anos:

        def take_orphan(match: re.Match[str]) -> str:
            n = int(match.group(1))
            if 1 <= n <= 9:
                anos.append(n)
                labels.append(InferredLabel("ano", str(n), f"{n}º ano", match.group(0).strip()))
                return " "
            return match.group(0)

        remaining = _ORPHAN_ORDINAL_RE.sub(take_orphan, remaining)

    def take_etapa(match: re.Match[str]) -> str:
        code = _etapa_code(match.group(1))
        etapas.append(code)
        labels.append(InferredLabel("etapa", code, match.group(1).strip(), match.group(0).strip()))
        return " "

    remaining = _ETAPA_RE.sub(take_etapa, remaining)

    unique_anos = sorted(set(anos))
    unique_etapas = _unique(etapas)
    if unique_anos and not unique_etapas:
        unique_etapas = ["EF"]

    remaining, taxonomy, tax_labels = _extract_taxonomy(remaining, unique_etapas, unique_anos)
    remaining = _NOISE_RE.sub(" ", remaining)
    remaining = _clean_remaining(remaining)
    labels.extend(tax_labels)

    seen: set[tuple[str, str]] = set()
    unique_labels: list[InferredLabel] = []
    for label in labels:
        key = (label.kind, label.id)
        if key in seen:
            continue
        seen.add(key)
        unique_labels.append(label)

    return remaining, SearchFilters(
        etapas=unique_etapas or None,
        anos=unique_anos or None,
        componentes=taxonomy.componentes,
        areas=taxonomy.areas,
        tipos=taxonomy.tipos,
        documentos=taxonomy.documentos,
        campos=taxonomy.campos,
    ), unique_labels


def inferred_labels(query: str) -> list[dict[str, str]]:
    _leftover, _filters, labels = parse_search_details(query)
    return [
        {"kind": label.kind, "id": label.id, "label": label.label, "phrase": label.phrase}
        for label in labels
    ]


def is_catalog_query(query: str, filters: SearchFilters | None = None) -> bool:
    lexical, inferred = parse_search_query(query or "")
    merged = merge_filters(filters or SearchFilters(), inferred)
    return not lexical and bool(
        merged.componentes or merged.areas or merged.tipos or merged.documentos or merged.campos
    )


def merge_filters(explicit: SearchFilters, inferred: SearchFilters) -> SearchFilters:
    return replace(
        explicit,
        etapas=explicit.etapas or inferred.etapas,
        anos=explicit.anos or inferred.anos,
        componentes=explicit.componentes or inferred.componentes,
        documentos=explicit.documentos or inferred.documentos,
        areas=explicit.areas or inferred.areas,
        campos=explicit.campos or inferred.campos,
        tipos=explicit.tipos or inferred.tipos,
    )


def active_snapshot(db: Session) -> Snapshot | None:
    return db.execute(select(Snapshot).where(Snapshot.active.is_(True))).scalar_one_or_none()


def apply_filters(stmt, filters: SearchFilters, db: Session | None = None, *, ignore: bool = False):
    if ignore:
        return stmt
    if not filters.incluir_revogados:
        stmt = stmt.where(Item.vigencia_status != "revogado")
    if filters.etapas:
        etapas = [e.upper() if len(e) <= 3 else e for e in filters.etapas]
        etapa_match = or_(Item.etapa.in_(etapas), Item.etapa.in_(filters.etapas))
        if filters.tipos and "competencia_geral" in filters.tipos:
            stmt = stmt.where(or_(etapa_match, Item.tipo == "competencia_geral"))
        else:
            stmt = stmt.where(etapa_match)
    if filters.anos:
        ints = [a for a in filters.anos if isinstance(a, int) or str(a).isdigit()]
        ids = [str(a) for a in filters.anos if not str(a).isdigit()]
        clauses = []
        if ints:
            clauses.append(Item.anos.overlap([int(a) for a in ints]))
        if ids:
            clauses.append(Item.recorte_id.in_(ids))
            if db is not None:
                recortes = list(db.execute(select(Recorte).where(Recorte.id.in_(ids))).scalars())
                for rec in recortes:
                    clauses.extend(recorte_item_clauses(rec))
            else:
                for recorte_id in ids:
                    prefix = grupo_etario_code_prefix(recorte_id)
                    if prefix:
                        clauses.append(Item.codigo.startswith(prefix))
        if clauses:
            stmt = stmt.where(or_(*clauses))
    if filters.componentes:
        stmt = stmt.where(Item.componente_id.in_(filters.componentes))
    if filters.documentos:
        stmt = stmt.where(Item.documento_id.in_(filters.documentos))
    if filters.areas:
        area_clauses = [Item.area_id.in_(filters.areas)]
        if db is not None:
            comp_ids = list(
                db.execute(select(Componente.id).where(Componente.area_id.in_(filters.areas))).scalars()
            )
            if comp_ids:
                area_clauses.append(Item.componente_id.in_(comp_ids))
        stmt = stmt.where(or_(*area_clauses))
    if filters.campos:
        clauses = []
        for campo_id in filters.campos:
            code = _CAMPO_CODE.get(campo_id, campo_id if len(campo_id) == 2 else "")
            name = CAMPOS_EI.get(code)
            if name:
                clauses.append(Item.unidade_ou_campo == name)
            if code:
                clauses.append(and_(Item.etapa == "EI", Item.codigo.like(f"EI__{code}%")))
        if clauses:
            stmt = stmt.where(or_(*clauses))
    if filters.tipos:
        stmt = stmt.where(Item.tipo.in_(filters.tipos))
    return stmt


def lookup_item(db: Session, raw: str) -> tuple[str, Item | None]:
    """Retorna ('invalid'|'missing'|'ok', item)."""
    try:
        decoded = decodificar(raw)
    except CodeError:
        return "invalid", None
    item = db.get(Item, decoded["codigo"])
    if item is None:
        return "missing", None
    return "ok", item


def suggest_codes(db: Session, raw: str, limit: int = 6) -> list[Item]:
    patterns = suggestion_like_patterns(raw)
    if not patterns:
        return []
    stmt = (
        select(Item)
        .where(or_(*[Item.codigo.like(pattern) for pattern in patterns]))
        .order_by(Item.codigo.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


def is_item_lookup_query(query: str, filters: SearchFilters | None = None) -> bool:
    if looks_like_single_code(query):
        return True
    _lexical, inferred = parse_search_query(query or "")
    if inferred.anos:
        return True
    if filters and (filters.anos or filters.componentes):
        return True
    return False


def wants_prose_strip(
    query: str,
    filters: SearchFilters | None = None,
    *,
    atalho_codigo: bool = False,
    offset: int = 0,
) -> bool:
    if offset != 0 or atalho_codigo:
        return False
    if not (query or "").strip():
        return False
    if is_item_lookup_query(query, filters):
        return False
    lexical, _inferred = parse_search_query(query)
    return bool(lexical)


def rrf_merge(*ranked_lists: list[str], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, codigo in enumerate(ranked, start=1):
            scores[codigo] = scores.get(codigo, 0.0) + 1.0 / (k + rank)
    return [codigo for codigo, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]


async def hybrid_search(
    db: Session,
    query: str,
    filters: SearchFilters,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Item], int, str | None]:
    query = (query or "").strip()
    if not query:
        if not has_scope(filters):
            return [], 0, None
        count_stmt = apply_filters(select(func.count()).select_from(Item), filters, db)
        total = int(db.execute(count_stmt).scalar_one() or 0)
        stmt = (
            apply_filters(select(Item), filters, db)
            .order_by(Item.codigo.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars()), total, None

    if looks_like_single_code(query):
        status, item = lookup_item(db, query)
        if status == "ok" and item is not None:
            return [item], 1, "codigo"

    lexical_query, inferred = parse_search_query(query)
    filters = merge_filters(filters, inferred)

    if not lexical_query and has_scope(filters):
        return _catalog_search(db, filters, limit, offset)

    candidates = settings.retrieve_candidates
    lexical = _lexical_search(db, lexical_query, filters, candidates)
    dense_limit = _DENSE_EXPAND if lexical else _RELATED_WHEN_EMPTY
    dense = await _dense_search(db, query, filters, dense_limit) if lexical_query else []
    if lexical:
        lexical_ids = {item.codigo for item in lexical}
        merged_ids = rrf_merge(
            [item.codigo for item in lexical],
            [item.codigo for item in dense],
        )
        dense_only = [codigo for codigo in merged_ids if codigo not in lexical_ids]
        keep = {codigo for codigo in lexical_ids}
        keep.update(dense_only[:_DENSE_EXPAND])
        merged_ids = [codigo for codigo in merged_ids if codigo in keep]
    else:
        merged_ids = [item.codigo for item in dense]
    if not merged_ids:
        return [], 0, None

    by_id = {item.codigo: item for item in lexical + dense}
    ordered = [by_id[cid] for cid in merged_ids if cid in by_id]

    try:
        rerank_n = min(len(ordered), settings.rerank_candidates)
        texts = [f"{item.codigo}: {item.texto}" for item in ordered[:rerank_n]]
        ranked = await rerank(query, texts)
        reranked = [ordered[index] for index, _ in ranked if index < rerank_n]
        seen = {item.codigo for item in reranked}
        for item in ordered:
            if item.codigo not in seen:
                reranked.append(item)
        ordered = reranked
    except Exception:
        # Rerank API down: keep RRF order. Buscar must still work.
        pass

    total = len(ordered)
    return ordered[offset : offset + limit], total, None


def _catalog_search(
    db: Session, filters: SearchFilters, limit: int, offset: int
) -> tuple[list[Item], int, str | None]:
    count_stmt = apply_filters(select(func.count()).select_from(Item), filters, db)
    total = int(db.execute(count_stmt).scalar_one() or 0)
    stmt = (
        apply_filters(select(Item), filters, db)
        .order_by(Item.codigo.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars()), total, None


def _search_document():
    objetos_text = func.coalesce(func.cast(Item.objetos, Text), "")
    return func.concat(
        Item.texto,
        " ",
        func.coalesce(Item.unidade_ou_campo, ""),
        " ",
        Item.codigo,
        " ",
        func.coalesce(Componente.nome, ""),
        " ",
        func.coalesce(Area.nome, ""),
        " ",
        objetos_text,
    )


def _with_taxonomy(stmt):
    return stmt.outerjoin(Componente, Item.componente_id == Componente.id).outerjoin(
        Area, Item.area_id == Area.id
    )


def has_scope(filters: SearchFilters) -> bool:
    return bool(
        filters.etapas
        or filters.anos
        or filters.componentes
        or filters.documentos
        or filters.areas
        or filters.campos
        or filters.tipos
    )


def _lexical_search(db: Session, query: str, filters: SearchFilters, limit: int) -> list[Item]:
    if not query:
        if not has_scope(filters):
            return []
        stmt = apply_filters(select(Item), filters, db).limit(limit)
        return list(db.execute(stmt).scalars())

    ts_query = func.plainto_tsquery("portuguese", query)
    tsv = func.to_tsvector("portuguese", _search_document())
    stmt = _with_taxonomy(select(Item).where(tsv.op("@@")(ts_query)))
    stmt = apply_filters(stmt, filters, db)
    stmt = stmt.order_by(func.ts_rank_cd(tsv, ts_query).desc()).limit(limit)
    rows = list(db.execute(stmt).scalars())
    if rows:
        return rows
    tokens = re.findall(r"[\wÀ-ÿ]{3,}", query, flags=re.UNICODE)
    if not tokens:
        return []
    clauses = [
        or_(
            Item.texto.ilike(f"%{token}%"),
            Item.codigo.ilike(f"%{token}%"),
            Item.unidade_ou_campo.ilike(f"%{token}%"),
            Componente.nome.ilike(f"%{token}%"),
            Area.nome.ilike(f"%{token}%"),
        )
        for token in tokens
    ]
    stmt = _with_taxonomy(select(Item).where(or_(*clauses)))
    stmt = apply_filters(stmt, filters, db).limit(limit)
    return list(db.execute(stmt).scalars())


async def _dense_search(db: Session, query: str, filters: SearchFilters, limit: int) -> list[Item]:
    try:
        vectors = await embed_texts([query])
    except Exception:
        return []
    vector = vectors[0]
    stmt = select(Item).where(Item.embedding.is_not(None))
    stmt = apply_filters(stmt, filters, db)
    stmt = stmt.order_by(Item.embedding.cosine_distance(vector)).limit(limit)
    return list(db.execute(stmt).scalars())


def _prose_searchable_clause():
    return and_(
        ProseBlock.type.notin_(list(SKIP_EMBED_TYPES)),
        ProseBlock.text != "",
    )


def _lexical_search_prose(
    db: Session,
    query: str,
    limit: int,
    types: frozenset[str] | None = None,
) -> list[ProseBlock]:
    if not query:
        return []
    ts_query = func.plainto_tsquery("portuguese", query)
    tsv = func.to_tsvector("portuguese", ProseBlock.text)
    stmt = select(ProseBlock).where(tsv.op("@@")(ts_query), _prose_searchable_clause())
    if types:
        stmt = stmt.where(ProseBlock.type.in_(list(types)))
    stmt = stmt.order_by(func.ts_rank_cd(tsv, ts_query).desc()).limit(limit)
    rows = list(db.execute(stmt).scalars())
    if rows:
        return rows
    tokens = re.findall(r"[\wÀ-ÿ]{3,}", query, flags=re.UNICODE)
    if not tokens:
        return []
    clauses = [ProseBlock.text.ilike(f"%{token}%") for token in tokens]
    stmt = select(ProseBlock).where(or_(*clauses), _prose_searchable_clause())
    if types:
        stmt = stmt.where(ProseBlock.type.in_(list(types)))
    return list(db.execute(stmt.limit(limit)).scalars())


async def _dense_search_prose(
    db: Session,
    query: str,
    limit: int,
    types: frozenset[str] | None = None,
) -> list[ProseBlock]:
    try:
        vectors = await embed_texts([query])
    except Exception:
        return []
    vector = vectors[0]
    stmt = select(ProseBlock).where(ProseBlock.embedding.is_not(None), _prose_searchable_clause())
    if types:
        stmt = stmt.where(ProseBlock.type.in_(list(types)))
    stmt = stmt.order_by(ProseBlock.embedding.cosine_distance(vector)).limit(limit)
    return list(db.execute(stmt).scalars())


async def hybrid_search_prose(
    db: Session,
    query: str,
    *,
    limit: int = 6,
    types: frozenset[str] | None = None,
) -> list[ProseBlock]:
    query = (query or "").strip()
    if not query:
        return []
    lexical_query, _inferred = parse_search_query(query)
    search_text = lexical_query or query
    candidates = settings.retrieve_candidates
    lexical = _lexical_search_prose(db, search_text, candidates, types)
    dense = await _dense_search_prose(db, query, candidates, types)
    merged_ids = rrf_merge([block.id for block in lexical], [block.id for block in dense])
    by_id = {block.id: block for block in lexical + dense}
    return [by_id[block_id] for block_id in merged_ids if block_id in by_id][:limit]


def related_items(db: Session, item: Item, limit: int = 8) -> list[Item]:
    stmt = select(Item).where(Item.codigo != item.codigo)
    if item.componente_id:
        stmt = stmt.where(Item.componente_id == item.componente_id)
    if item.anos:
        stmt = stmt.where(Item.anos.overlap(item.anos))
    stmt = stmt.where(Item.vigencia_status != "revogado").limit(limit)
    return list(db.execute(stmt).scalars())
