#!/usr/bin/env python3
"""Poll GitHub Releases for new dados-* tags. Halt on schema-major. Do not track main or PyPI."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

OWNER = os.environ.get("BNCC_DADOS_OWNER", "bncc-dev")
REPO = os.environ.get("BNCC_DADOS_REPO", "bncc-dados")
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
TAG_FILE = Path("vendor/bncc-dados/VERSION")
ETAG_FILE = Path(os.environ.get("GITHUB_ETAG_PATH", "vendor/bncc-dados/ETAG"))
PINNED = os.environ.get("BNCC_DADOS_TAG", TAG_FILE.read_text(encoding="utf-8").strip() if TAG_FILE.exists() else "dados-2026.07.1")


def parse_tag(tag: str) -> tuple[int, ...]:
    m = re.match(r"dados-(\d{4})\.(\d{2})(?:\.(\d+))?", tag)
    if not m:
        return (0, 0, 0)
    year, month, patch = m.groups()
    return (int(year), int(month), int(patch or 0))


def main() -> int:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "buscabase-release-watch"}
    etag = ETAG_FILE.read_text(encoding="utf-8").strip() if ETAG_FILE.exists() else ""
    if etag:
        headers["If-None-Match"] = etag
    req = urllib.request.Request(f"{API}/repos/{OWNER}/{REPO}/releases", headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode())
            new_etag = response.headers.get("ETag") or etag
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            print("sem mudanças (ETag)")
            return 0
        raise
    ETAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ETAG_FILE.write_text(new_etag, encoding="utf-8")
    dados = [rel["tag_name"] for rel in body if re.match(r"^dados-", rel.get("tag_name", ""))]
    if not dados:
        print("nenhum release dados-*")
        return 0
    newest = max(dados, key=parse_tag)
    if parse_tag(newest) <= parse_tag(PINNED):
        print(f"recorte atual {PINNED} está em dia (mais novo visto: {newest})")
        return 0
    print(f"NOVO_RECORTE={newest}")
    print(f"ATUAL={PINNED}")
    # schema-major halt is applied at ingest time from the tag tree
    return 10


if __name__ == "__main__":
    sys.exit(main())
