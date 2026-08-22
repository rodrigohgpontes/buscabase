"""Constants and small helpers for the official-PDF prose corpus."""

from __future__ import annotations

SKIP_EMBED_TYPES = frozenset(
    {
        "running_header",
        "running_footer",
        "page_number",
        "figure",
    }
)

SEARCHABLE_TYPES = frozenset(
    {
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "article",
        "card",
        "list_item",
        "title",
        "caption",
        "table_header",
        "table_cell",
    }
)

STRIP_TYPES = frozenset(
    {
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "article",
        "card",
    }
)


def is_embeddable_block(block_type: str, text: str) -> bool:
    if block_type in SKIP_EMBED_TYPES:
        return False
    if not (text or "").strip():
        return False
    return block_type in SEARCHABLE_TYPES


def prose_embed_text(documento_id: str, page: int, text: str) -> str:
    return f"{documento_id}, p. {page}. {text}"


def restored_embedding(
    previous: dict[str, tuple[str | None, object, str | None]],
    block_id: str,
    texto_hash: str,
) -> tuple[object | None, str | None]:
    prev = previous.get(block_id)
    if prev and prev[0] and prev[0] == texto_hash:
        return prev[1], prev[2]
    return None, None
