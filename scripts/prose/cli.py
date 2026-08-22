"""CLI: download, extract, classify, link, validate, write JSON."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.prose.blocks import build_pages
from scripts.prose.documents import DOCUMENTS, REPO_ROOT
from scripts.prose.download import default_pdf_dir, default_snapshot_dir, default_tag, prepare_all
from scripts.prose.extract import extract_document
from scripts.prose.link import default_catalog_path, link_document, load_catalog_codes, load_snapshot_items
from scripts.prose.validate import linked_catalog_coverage, validate_document


def default_out_dir() -> Path:
    return Path(os.environ.get("BNCC_PROSE_DIR") or REPO_ROOT / "data" / "prose")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_one(spec, readable: Path, canonical: Path, out_dir: Path, snapshot_dir: Path, catalog_path: Path | None) -> dict:
    raw_pages = extract_document(readable)
    pages = build_pages(spec.id, raw_pages)
    known = load_catalog_codes(catalog_path)
    items = load_snapshot_items(snapshot_dir)
    skip_gate = spec.id == "arte-2026"
    link_report = link_document(pages, known_codes=known, items=items, skip_catalog_gate=skip_gate)
    check = validate_document(spec, readable, pages)
    payload = {
        "documento_id": spec.id,
        "arquivo": spec.arquivo,
        "sha256": spec.sha256,
        "page_count": len(pages),
        "data_version": spec.data_version,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "canonical_pdf": str(canonical),
        "pages": pages,
        "link_report": link_report,
        "validation": {k: v for k, v in check.items() if k != "normalized_oracle_sample"},
    }
    write_json(out_dir / f"{spec.id}.json", payload)
    if not skip_gate and known:
        file_codes = {
            codigo
            for codigo, row in items.items()
            if spec.arquivo in (row.get("arquivo") or "") or (not row.get("arquivo") and spec.id in {"bncc-2018"} and not str(codigo).startswith("CO"))
        }
        # Only require codes we actually saw in this document's extract via page locators.
        expected = {
            codigo
            for codigo, row in items.items()
            if row.get("pagina") and any(page["page"] == row["pagina"] for page in pages)
        }
        if spec.id == "computacao-2022":
            expected = {codigo for codigo in expected if "CO" in codigo or str(codigo).startswith("computacao-")}
        elif spec.id == "bncc-2018":
            expected = {codigo for codigo in expected if "CO" not in codigo and not str(codigo).startswith("computacao-")}
        missing = linked_catalog_coverage(pages, expected, allowlist=set())
        if missing:
            check["errors"].append(
                f"{spec.id}: {len(missing)} códigos do snapshot sem bloco ligado (ex.: {missing[:8]})"
            )
            check["ok"] = False
        payload["validation"]["missing_codes"] = missing[:50]
        write_json(out_dir / f"{spec.id}.json", payload)
    return check


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extrai prosa oficial da BNCC para JSON.")
    parser.add_argument("--out", type=Path, default=default_out_dir())
    parser.add_argument("--pdf-dir", type=Path, default=default_pdf_dir())
    parser.add_argument("--snapshot-dir", type=Path, default=default_snapshot_dir())
    parser.add_argument("--tag", default=default_tag())
    parser.add_argument("--catalog", type=Path, default=default_catalog_path())
    parser.add_argument("--only", action="append", dest="only")
    args = parser.parse_args(argv)

    prepared = prepare_all(args.pdf_dir, args.snapshot_dir, args.tag)
    wanted = set(args.only or [spec.id for spec in DOCUMENTS])
    failures: list[str] = []
    for spec in DOCUMENTS:
        if spec.id not in wanted:
            continue
        _spec, canonical, readable = prepared[spec.id]
        print(f"extraindo {spec.id} ({spec.arquivo})…")
        check = extract_one(spec, readable, canonical, args.out, args.snapshot_dir, args.catalog)
        print(
            f"  {spec.id}: {check['pages']} págs, cobertura mínima {check['worst_coverage']}"
            + ("" if check["ok"] else " FALHOU")
        )
        failures.extend(check["errors"])
    if failures:
        print("\n".join(failures))
        return 1
    print(f"JSON em {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
