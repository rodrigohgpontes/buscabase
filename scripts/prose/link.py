"""Overlay item_codigo on blocks that contain known BNCC codes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from scripts.prose.documents import REPO_ROOT
from scripts.prose.normalize import normalize

CODE_RE = re.compile(
    r"\b(EI\d{2}(?:CO|[A-Z]{2})\d{2,3}|EF\d{2}(?:CO|[A-Z]{2,3})\d{2,3}|EM13(?:CO|[A-Z]{2,3})\d{2,3})\b"
)
PAGE_RE = re.compile(r"página PDF\s+(\d+)", re.I)

sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))
try:
    from app.codes import CodeError, decodificar
except Exception:  # pragma: no cover - used when API package is unavailable
    CodeError = ValueError  # type: ignore[misc,assignment]

    def decodificar(codigo: str) -> dict[str, Any]:
        if not CODE_RE.fullmatch(codigo):
            raise CodeError(codigo)
        return {"codigo": codigo}


def parse_page(locator: str | None) -> int | None:
    if not locator:
        return None
    match = PAGE_RE.search(locator)
    return int(match.group(1)) if match else None


def load_catalog_codes(catalog_path: Path | None) -> set[str]:
    if catalog_path is None or not catalog_path.is_file():
        return set()
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return {item["codigo"] for item in data.get("items") or [] if item.get("codigo")}


def load_snapshot_items(snapshot_dir: Path | None) -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    if snapshot_dir is None or not snapshot_dir.exists():
        return items
    for path in snapshot_dir.rglob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        groups = []
        if isinstance(payload, dict):
            for key in (
                "habilidades",
                "objetivos",
                "habilidades_ef",
                "habilidades_em",
                "objetivos_ei",
                "competencias",
                "competencias_gerais",
                "competencias_especificas",
            ):
                if isinstance(payload.get(key), list):
                    groups.extend(payload[key])
        for row in groups:
            if not isinstance(row, dict):
                continue
            codigo = row.get("codigo") or row.get("id")
            if not codigo:
                continue
            fonte = row.get("fonte") or {}
            items[str(codigo)] = {
                "codigo": str(codigo),
                "texto": row.get("texto") or "",
                "pagina": parse_page(fonte.get("localizador_pdf")),
                "arquivo": fonte.get("arquivo") or "",
            }
    return items


def codes_in_text(text: str) -> list[str]:
    found: list[str] = []
    for match in CODE_RE.finditer(text or ""):
        codigo = match.group(1)
        try:
            decodificar(codigo)
        except CodeError:
            continue
        if codigo not in found:
            found.append(codigo)
    return found


def _best_competencia(text: str, items: dict[str, dict[str, Any]]) -> str | None:
    needle = normalize(text)
    if len(needle) < 40:
        return None
    best_id = None
    best_score = 0.0
    for codigo, row in items.items():
        if not str(codigo).startswith(("cg-", "ef-", "em-", "computacao-")):
            continue
        hay = normalize(row.get("texto") or "")
        if not hay or len(hay) < 40:
            continue
        if hay in needle or needle in hay:
            score = min(len(hay), len(needle)) / max(len(hay), len(needle))
            if score > best_score:
                best_score = score
                best_id = codigo
    return best_id if best_score >= 0.86 else None


def link_document(
    pages: list[dict[str, Any]],
    *,
    known_codes: set[str],
    items: dict[str, dict[str, Any]],
    skip_catalog_gate: bool,
) -> dict[str, Any]:
    report: dict[str, Any] = {"linked": 0, "unknown_codes": [], "page_mismatches": []}
    for page in pages:
        for block in page.get("blocks") or []:
            if block.get("type") == "figure":
                continue
            text = block.get("text") or ""
            codes = codes_in_text(text)
            chosen = None
            for codigo in codes:
                if known_codes and codigo not in known_codes and codigo not in items:
                    if codigo not in report["unknown_codes"]:
                        report["unknown_codes"].append(codigo)
                    continue
                chosen = codigo
                expected = (items.get(codigo) or {}).get("pagina")
                if expected and expected != page["page"]:
                    report["page_mismatches"].append(
                        {"codigo": codigo, "bloco": block["id"], "pagina_bloco": page["page"], "pagina_catalogo": expected}
                    )
                break
            if chosen is None and not skip_catalog_gate:
                chosen = _best_competencia(text, items)
            if chosen:
                block["item_codigo"] = chosen
                report["linked"] += 1
    return report


def default_catalog_path() -> Path | None:
    env = Path(__file__).resolve()
    candidates = [
        REPO_ROOT / "data" / "catalog" / "catalog.json",
        Path("/data/catalog/catalog.json"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None
