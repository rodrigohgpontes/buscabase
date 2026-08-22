"""PyMuPDF pass: every text span, filled drawings, and image XObjects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import fitz


@dataclass
class Span:
    text: str
    bbox: list[float]
    font_size: float
    font_name: str
    flags: int


def _rect_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]


def extract_page_raw(page: fitz.Page) -> dict[str, Any]:
    raw = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    spans: list[Span] = []
    for block in raw.get("blocks") or []:
        if block.get("type") != 0:
            continue
        for line in block.get("lines") or []:
            for span in line.get("spans") or []:
                text = span.get("text") or ""
                if text == "":
                    continue
                bbox = [round(float(v), 2) for v in span.get("bbox") or (0, 0, 0, 0)]
                spans.append(
                    Span(
                        text=text,
                        bbox=bbox,
                        font_size=round(float(span.get("size") or 0), 2),
                        font_name=str(span.get("font") or ""),
                        flags=int(span.get("flags") or 0),
                    )
                )

    filled: list[list[float]] = []
    for drawing in page.get_drawings():
        if drawing.get("fill") and drawing.get("rect") is not None:
            filled.append(_rect_list(fitz.Rect(drawing["rect"])))

    images: list[list[float]] = []
    for info in page.get_image_info():
        bbox = info.get("bbox")
        if bbox:
            images.append(_rect_list(fitz.Rect(bbox)))

    return {
        "width": round(float(page.rect.width), 2),
        "height": round(float(page.rect.height), 2),
        "spans": [asdict(span) for span in spans],
        "filled_rects": filled,
        "images": images,
    }


def extract_document(pdf_path: Path) -> list[dict[str, Any]]:
    document = fitz.open(pdf_path)
    try:
        pages = []
        for index, page in enumerate(document, start=1):
            raw = extract_page_raw(page)
            raw["page"] = index
            pages.append(raw)
        return pages
    finally:
        document.close()
