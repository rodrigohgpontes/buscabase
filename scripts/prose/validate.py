"""pdftotext coverage gate and page-count checks."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from scripts.prose.documents import DocumentSpec
from scripts.prose.normalize import bag_coverage, normalize

MIN_COVERAGE = 0.985


def pdftotext_pages(pdf_path: Path) -> list[str]:
    raw = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8", errors="replace")
    pages = raw.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    return pages


def reconstruct_page(page: dict[str, Any]) -> str:
    parts = []
    for block in page.get("blocks") or []:
        if block.get("type") == "figure":
            continue
        parts.append(block.get("text") or "")
    return "\n".join(parts)


def validate_document(
    spec: DocumentSpec,
    extractable_pdf: Path,
    pages: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    if len(pages) != spec.page_count:
        errors.append(f"{spec.id}: {len(pages)} páginas extraídas, esperado {spec.page_count}")

    oracle_pages = pdftotext_pages(extractable_pdf)
    if spec.id == "computacao-2022" and len(oracle_pages) != spec.page_count:
        # Ghostscript rewrite can add a blank trailer; compare overlapping pages.
        oracle_pages = oracle_pages[: spec.page_count]

    worst = 1.0
    weak: list[dict[str, Any]] = []
    comparable = min(len(pages), len(oracle_pages))
    if comparable == 0:
        errors.append(f"{spec.id}: pdftotext não devolveu páginas")
    for index in range(comparable):
        score = bag_coverage(oracle_pages[index], reconstruct_page(pages[index]))
        worst = min(worst, score)
        if score < MIN_COVERAGE:
            weak.append({"page": index + 1, "coverage": round(score, 4)})
    if weak:
        errors.append(
            f"{spec.id}: cobertura abaixo de {MIN_COVERAGE} em {len(weak)} página(s); "
            f"pior={weak[0]}"
        )
    if len(oracle_pages) not in {spec.page_count, spec.page_count + 1} and spec.id != "computacao-2022":
        errors.append(f"{spec.id}: pdftotext {len(oracle_pages)} páginas, esperado {spec.page_count}")

    return {
        "documento_id": spec.id,
        "pages": len(pages),
        "oracle_pages": len(oracle_pages),
        "worst_coverage": round(worst, 4),
        "weak_pages": weak,
        "errors": errors,
        "ok": not errors,
        "normalized_oracle_sample": normalize(oracle_pages[0][:200]) if oracle_pages else "",
    }


def linked_catalog_coverage(
    pages: list[dict[str, Any]],
    expected_codes: set[str],
    allowlist: set[str],
) -> list[str]:
    seen = {
        block.get("item_codigo")
        for page in pages
        for block in page.get("blocks") or []
        if block.get("item_codigo")
    }
    missing = sorted(code for code in expected_codes if code not in seen and code not in allowlist)
    return missing
