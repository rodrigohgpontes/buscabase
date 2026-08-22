"""Cluster spans into reading-order typed blocks."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from scripts.prose.normalize import join_hyphenated

BLOCK_TYPES = {
    "running_header",
    "running_footer",
    "page_number",
    "title",
    "heading_1",
    "heading_2",
    "heading_3",
    "paragraph",
    "list_item",
    "table_header",
    "table_cell",
    "card",
    "article",
    "caption",
    "figure",
}

ARTICLE_RE = re.compile(
    r"^(Art\.?\s*\d+|Artigo\s+\d+|§\s*\d+|CAPÍTULO\s+[IVXLCDM]+|TÍTULO\s+[IVXLCDM]+)",
    re.I,
)
LIST_RE = re.compile(r"^(?:[-•–—▪]|[a-z]\)|[ivxlcdm]+\)|\d+[.)])\s+", re.I)
PAGE_NUM_RE = re.compile(r"^\d{1,3}(?:\s*/\s*\d{1,3})?$")
CAPTION_RE = re.compile(r"^(tabela|quadro|figura|gráfico)\s+\d", re.I)
ARTE_CHROME = (
    "PROCESSO Nº: 23001.000221/2022-97",
    "Cesar Callegari",
)


def _mid_y(bbox: list[float]) -> float:
    return (bbox[1] + bbox[3]) / 2


def _height(bbox: list[float]) -> float:
    return max(0.1, bbox[3] - bbox[1])


def _inside(inner: list[float], outer: list[float], pad: float = 2.0) -> bool:
    return (
        inner[0] >= outer[0] - pad
        and inner[1] >= outer[1] - pad
        and inner[2] <= outer[2] + pad
        and inner[3] <= outer[3] + pad
    )


def group_lines(spans: list[dict[str, Any]], y_tol: float = 3.2) -> list[dict[str, Any]]:
    ordered = sorted(spans, key=lambda span: (_mid_y(span["bbox"]), span["bbox"][0]))
    lines: list[list[dict[str, Any]]] = []
    for span in ordered:
        if lines and abs(_mid_y(span["bbox"]) - _mid_y(lines[-1][0]["bbox"])) <= y_tol:
            lines[-1].append(span)
        else:
            lines.append([span])
    result = []
    for items in lines:
        items.sort(key=lambda span: span["bbox"][0])
        text = "".join(span["text"] for span in items)
        bbox = [
            min(span["bbox"][0] for span in items),
            min(span["bbox"][1] for span in items),
            max(span["bbox"][2] for span in items),
            max(span["bbox"][3] for span in items),
        ]
        size = max(span["font_size"] for span in items)
        font = items[0]["font_name"]
        result.append({"text": text, "bbox": bbox, "font_size": size, "font_name": font, "spans": items})
    return result


def _column_split(lines: list[dict[str, Any]], page_width: float) -> list[list[dict[str, Any]]]:
    if len(lines) < 8:
        return [lines]
    mids = [((line["bbox"][0] + line["bbox"][2]) / 2) for line in lines]
    left, right, middle = [], [], []
    for line, mid in zip(lines, mids, strict=True):
        if mid < page_width * 0.48:
            left.append(line)
        elif mid >= page_width * 0.52:
            right.append(line)
        else:
            middle.append(line)
    if len(left) >= 4 and len(right) >= 4:
        leftover = middle
        columns = [left, right]
        if leftover:
            columns.append(leftover)
        return columns
    return [lines]


def cluster_blocks(lines: list[dict[str, Any]], page_width: float) -> list[list[dict[str, Any]]]:
    columns = _column_split(lines, page_width)
    blocks: list[list[dict[str, Any]]] = []
    for column in columns:
        column = sorted(column, key=lambda line: (line["bbox"][1], line["bbox"][0]))
        current: list[dict[str, Any]] = []
        for line in column:
            if not current:
                current = [line]
                continue
            prev = current[-1]
            gap = line["bbox"][1] - prev["bbox"][3]
            typical = max(_height(prev["bbox"]), _height(line["bbox"]))
            size_jump = abs(line["font_size"] - prev["font_size"]) > 1.6
            x_overlap = min(prev["bbox"][2], line["bbox"][2]) - max(prev["bbox"][0], line["bbox"][0])
            narrow = x_overlap < min(prev["bbox"][2] - prev["bbox"][0], line["bbox"][2] - line["bbox"][0]) * 0.2
            if gap > typical * 1.55 or size_jump or (narrow and gap > typical * 0.4):
                blocks.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append(current)
    blocks.sort(key=lambda group: (group[0]["bbox"][1], group[0]["bbox"][0]))
    return blocks


def _bbox_of(lines: list[dict[str, Any]]) -> list[float]:
    return [
        min(line["bbox"][0] for line in lines),
        min(line["bbox"][1] for line in lines),
        max(line["bbox"][2] for line in lines),
        max(line["bbox"][3] for line in lines),
    ]


def _repeated_edge_text(pages: list[dict[str, Any]], edge: str) -> set[str]:
    samples: list[str] = []
    for page in pages:
        height = page["height"]
        lines = page.get("lines") or []
        if edge == "top":
            candidates = [line for line in lines if line["bbox"][1] < height * 0.09]
        else:
            candidates = [line for line in lines if line["bbox"][3] > height * 0.91]
        if candidates:
            text = candidates[0]["text"].strip() if edge == "top" else candidates[-1]["text"].strip()
            if text:
                samples.append(re.sub(r"\s+", " ", text))
    counts = Counter(samples)
    threshold = max(3, int(len(pages) * 0.25))
    return {text for text, count in counts.items() if count >= threshold and len(text) > 3}


def _in_card(bbox: list[float], filled: list[list[float]]) -> bool:
    for rect in filled:
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        if width < 40 or height < 24:
            continue
        if _inside(bbox, rect, pad=4):
            return True
    return False


def _heading_rank(size: float, ranks: list[float]) -> str | None:
    if not ranks:
        return None
    if size >= ranks[0] - 0.2:
        return "heading_1"
    if len(ranks) > 1 and size >= ranks[1] - 0.2:
        return "heading_2"
    if len(ranks) > 2 and size >= ranks[2] - 0.2:
        return "heading_3"
    return None


def _font_ranks(lines: list[dict[str, Any]]) -> list[float]:
    sizes = sorted({round(line["font_size"], 1) for line in lines}, reverse=True)
    body = sizes[len(sizes) // 2] if sizes else 10
    return [size for size in sizes if size >= body + 1.2][:3]


def classify_block(
    lines: list[dict[str, Any]],
    *,
    page_height: float,
    page_index: int,
    filled: list[list[float]],
    repeated_top: set[str],
    repeated_bottom: set[str],
    heading_ranks: list[float],
    table_columns: bool,
) -> str:
    text = join_hyphenated([line["text"] for line in lines])
    compact = re.sub(r"\s+", " ", text).strip()
    bbox = _bbox_of(lines)
    size = max(line["font_size"] for line in lines)

    if any(marker.lower() in compact.lower() for marker in ARTE_CHROME):
        return "running_header"
    if compact in repeated_top or (bbox[1] < page_height * 0.07 and compact in repeated_top):
        return "running_header"
    if compact in repeated_bottom or (bbox[3] > page_height * 0.93 and compact in repeated_bottom):
        return "running_footer"
    if bbox[3] > page_height * 0.90 and PAGE_NUM_RE.match(compact):
        return "page_number"
    if bbox[1] < page_height * 0.08 and PAGE_NUM_RE.match(compact):
        return "page_number"
    if CAPTION_RE.match(compact):
        return "caption"
    if ARTICLE_RE.match(compact):
        return "article"
    if _in_card(bbox, filled):
        return "card"
    if page_index == 1 and size >= (heading_ranks[0] if heading_ranks else size) and len(compact) < 80:
        return "title"
    heading = _heading_rank(size, heading_ranks)
    if heading and len(compact) < 160:
        return heading
    if LIST_RE.match(compact):
        return "list_item"
    if table_columns and size <= 9.5:
        if compact.isupper() or len(compact) < 40:
            return "table_header"
        return "table_cell"
    return "paragraph"


def _looks_like_table(lines: list[dict[str, Any]], page_width: float) -> bool:
    if len(lines) < 10:
        return False
    xs = [round(line["bbox"][0] / 12) * 12 for line in lines]
    counts = Counter(xs)
    strong = [count for count in counts.values() if count >= 4]
    return len(strong) >= 2 and page_width > 400


def blocks_for_page(
    page: dict[str, Any],
    *,
    documento_id: str,
    repeated_top: set[str],
    repeated_bottom: set[str],
) -> list[dict[str, Any]]:
    lines = group_lines(page["spans"])
    heading_ranks = _font_ranks(lines)
    table_columns = _looks_like_table(lines, page["width"])
    groups = cluster_blocks(lines, page["width"])
    used: set[int] = set()
    for group in groups:
        for line in group:
            used.add(id(line))
    leftovers = [line for line in lines if id(line) not in used]
    if leftovers:
        groups.append(leftovers)
    blocks: list[dict[str, Any]] = []
    seq = 0
    for group in groups:
        raw_lines = [line["text"] for line in group]
        text = join_hyphenated(raw_lines)
        if text.strip() == "" and not any(line["text"] for line in group):
            continue
        seq += 1
        block_type = classify_block(
            group,
            page_height=page["height"],
            page_index=page["page"],
            filled=page.get("filled_rects") or [],
            repeated_top=repeated_top,
            repeated_bottom=repeated_bottom,
            heading_ranks=heading_ranks,
            table_columns=table_columns,
        )
        font_sizes = [line["font_size"] for line in group]
        blocks.append(
            {
                "id": f"{documento_id}-p{page['page']}-b{seq}",
                "type": block_type,
                "text": text,
                "raw_lines": raw_lines,
                "bbox": [round(v, 2) for v in _bbox_of(group)],
                "font_size": max(font_sizes),
                "font_name": group[0]["font_name"],
                "item_codigo": None,
            }
        )
    for index, image_bbox in enumerate(page.get("images") or [], start=1):
        seq += 1
        blocks.append(
            {
                "id": f"{documento_id}-p{page['page']}-f{index}",
                "type": "figure",
                "text": "",
                "raw_lines": [],
                "bbox": image_bbox,
                "font_size": None,
                "font_name": None,
                "item_codigo": None,
            }
        )
    blocks.sort(key=lambda block: (block["bbox"][1], block["bbox"][0]))
    return blocks


def build_pages(documento_id: str, raw_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for raw in raw_pages:
        prepared.append({**raw, "lines": group_lines(raw["spans"])})
    repeated_top = _repeated_edge_text(prepared, "top")
    repeated_bottom = _repeated_edge_text(prepared, "bottom")
    pages = []
    for raw in prepared:
        pages.append(
            {
                "page": raw["page"],
                "width": raw["width"],
                "height": raw["height"],
                "blocks": blocks_for_page(
                    raw,
                    documento_id=documento_id,
                    repeated_top=repeated_top,
                    repeated_bottom=repeated_bottom,
                ),
            }
        )
    return pages
