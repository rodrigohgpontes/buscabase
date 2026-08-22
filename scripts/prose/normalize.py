"""Text normalization aligned with bncc-dados pipeline/verificar.py."""

from __future__ import annotations

import re
import unicodedata

SOFT_HYPHEN = "\u00ad"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace(SOFT_HYPHEN, "")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"[\s\u00a0]+", " ", text)
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"(?<=[A-Za-zÀ-ú])- (?=[A-Za-zà-ú])", "-", text)
    return text.strip()


def join_hyphenated(lines: list[str]) -> str:
    if not lines:
        return ""
    parts: list[str] = []
    for raw in lines:
        line = (raw or "").strip()
        if not line:
            continue
        if parts and parts[-1].endswith("-") and line[:1].islower():
            parts[-1] = parts[-1][:-1] + line
        else:
            parts.append(line)
    return " ".join(parts)


def alphabetic_bag(text: str) -> dict[str, int]:
    bag: dict[str, int] = {}
    for char in unicodedata.normalize("NFC", text or "").lower():
        if char.isalpha():
            bag[char] = bag.get(char, 0) + 1
    return bag


def bag_coverage(oracle: str, observed: str) -> float:
    want = alphabetic_bag(normalize(oracle))
    got = alphabetic_bag(normalize(observed))
    total = sum(want.values())
    if total == 0:
        return 1.0
    matched = sum(min(count, got.get(char, 0)) for char, count in want.items())
    return matched / total
