"""Locate or download pinned PDFs and verify SHA-256."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen

from scripts.prose.documents import DOCUMENTS, DocumentSpec, REPO_ROOT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_pdf_dir() -> Path:
    env = os.environ.get("BNCC_PROSE_PDF_DIR")
    if env:
        return Path(env)
    return REPO_ROOT / "data" / "prose" / "pdfs"


def default_snapshot_dir() -> Path:
    return Path(os.environ.get("BNCC_SNAPSHOT_DIR") or REPO_ROOT / "data" / "snapshots")


def default_tag() -> str:
    return os.environ.get("BNCC_DADOS_TAG") or "dados-2026.07.1"


def github_raw_url(spec: DocumentSpec, tag: str) -> str:
    owner = os.environ.get("BNCC_DADOS_OWNER") or "bncc-dev"
    repo = os.environ.get("BNCC_DADOS_REPO") or "bncc-dados"
    return f"https://github.com/{owner}/{repo}/raw/refs/tags/{tag}/fontes/{spec.arquivo}"


def find_in_snapshot(spec: DocumentSpec, snapshot_dir: Path) -> Path | None:
    if not snapshot_dir.exists():
        return None
    matches = list(snapshot_dir.rglob(spec.arquivo))
    return matches[0] if matches else None


def copy_verified(src: Path, dest: Path, spec: DocumentSpec) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    digest = sha256_file(dest)
    if digest != spec.sha256:
        dest.unlink(missing_ok=True)
        raise SystemExit(
            f"{spec.arquivo}: SHA-256 {digest} ≠ pin {spec.sha256}"
        )
    return dest


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url) as response, dest.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def ghostscript_normalize(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "gs",
            "-dNOPAUSE",
            "-dBATCH",
            "-dSAFER",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={dest}",
            str(src),
        ],
        check=True,
        capture_output=True,
    )
    return dest


def prepare_pdf(
    spec: DocumentSpec,
    pdf_dir: Path | None = None,
    snapshot_dir: Path | None = None,
    tag: str | None = None,
) -> tuple[Path, Path]:
    """Return (canonical_bytes, extractable_path). The second may be Ghostscript-rewritten."""
    pdf_dir = pdf_dir or default_pdf_dir()
    snapshot_dir = snapshot_dir or default_snapshot_dir()
    tag = tag or default_tag()
    dest = pdf_dir / spec.arquivo

    if spec.source == "local":
        if spec.local_path is None or not spec.local_path.is_file():
            raise SystemExit(f"{spec.id}: arquivo local ausente ({spec.local_path})")
        canonical = copy_verified(spec.local_path, dest, spec)
    elif dest.is_file() and sha256_file(dest) == spec.sha256:
        canonical = dest
    else:
        found = find_in_snapshot(spec, snapshot_dir)
        if found:
            canonical = copy_verified(found, dest, spec)
        else:
            download_url(github_raw_url(spec, tag), dest)
            canonical = copy_verified(dest, dest, spec)

    if spec.needs_ghostscript:
        rewritten = pdf_dir / f"{spec.id}.gs.pdf"
        if not rewritten.is_file() or rewritten.stat().st_mtime < canonical.stat().st_mtime:
            ghostscript_normalize(canonical, rewritten)
        return canonical, rewritten
    return canonical, canonical


def prepare_all(
    pdf_dir: Path | None = None,
    snapshot_dir: Path | None = None,
    tag: str | None = None,
) -> dict[str, tuple[DocumentSpec, Path, Path]]:
    prepared: dict[str, tuple[DocumentSpec, Path, Path]] = {}
    for spec in DOCUMENTS:
        canonical, readable = prepare_pdf(spec, pdf_dir, snapshot_dir, tag)
        prepared[spec.id] = (spec, canonical, readable)
    return prepared
