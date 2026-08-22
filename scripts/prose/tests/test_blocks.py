from scripts.prose.blocks import classify_block, group_lines
from scripts.prose.link import codes_in_text


def _line(text: str, y: float = 100, size: float = 11, x0: float = 72, x1: float = 400) -> dict:
    return {
        "text": text,
        "bbox": [x0, y, x1, y + 12],
        "font_size": size,
        "font_name": "Times",
        "spans": [],
    }


def test_group_lines_same_row():
    spans = [
        {"text": "Hello", "bbox": [72, 100, 110, 112], "font_size": 11, "font_name": "T", "flags": 0},
        {"text": " world", "bbox": [110, 101, 160, 113], "font_size": 11, "font_name": "T", "flags": 0},
    ]
    lines = group_lines(spans)
    assert len(lines) == 1
    assert lines[0]["text"] == "Hello world"


def test_article_and_list_and_header():
    kwargs = dict(
        page_height=842,
        page_index=10,
        filled=[],
        repeated_top=set(),
        repeated_bottom=set(),
        heading_ranks=[16, 13],
        table_columns=False,
    )
    assert classify_block([_line("Art. 1º Esta Resolução…")], **kwargs) == "article"
    assert classify_block([_line("§ 2º Na Educação Básica…")], **kwargs) == "article"
    assert classify_block([_line("a) A Arte é um Campo…")], **kwargs) == "list_item"
    assert (
        classify_block([_line("PROCESSO Nº: 23001.000221/2022-97")], **kwargs)
        == "running_header"
    )


def test_page_number():
    kwargs = dict(
        page_height=842,
        page_index=2,
        filled=[],
        repeated_top=set(),
        repeated_bottom=set(),
        heading_ranks=[],
        table_columns=False,
    )
    assert classify_block([_line("54", y=810, x0=300, x1=320)], **kwargs) == "page_number"


def test_codes_in_text():
    assert codes_in_text("ver (EF05MA03) e também EM13LGG103.") == ["EF05MA03", "EM13LGG103"]
