"""Chinese-first project filenames shared by story-workflow scripts."""

from __future__ import annotations

import re

_DIGITS = "零一二三四五六七八九"
_UNIT_VALUES = {"十": 10, "百": 100, "千": 1000}


def chinese_number(value: int) -> str:
    if not 0 <= value <= 9999:
        raise ValueError("Chinese project filenames support 0–9999")
    if value < 10:
        return _DIGITS[value]
    parts: list[str] = []
    remaining = value
    for divisor, unit in ((1000, "千"), (100, "百"), (10, "十")):
        digit, remaining = divmod(remaining, divisor)
        if digit:
            parts.append(_DIGITS[digit] + unit)
        elif parts and remaining:
            parts.append("零")
    if remaining:
        parts.append(_DIGITS[remaining])
    result = "".join(parts).replace("零零", "零").rstrip("零")
    return result[1:] if result.startswith("一十") else result


def chinese_to_int(value: str) -> int:
    if value == "零":
        return 0
    if not value:
        raise ValueError("empty Chinese number")
    total = 0
    section = 0
    digit = 0
    for char in value:
        if char in _DIGITS:
            digit = _DIGITS.index(char)
        elif char in _UNIT_VALUES:
            section += (digit or 1) * _UNIT_VALUES[char]
            digit = 0
        else:
            raise ValueError(f"unsupported Chinese numeral: {value}")
    total += section + digit
    return total


def chapter_filename(chapter: int) -> str:
    return f"第{chinese_number(chapter)}章.md"


def context_filename(chapter: int) -> str:
    return f"第{chinese_number(chapter)}章-上下文.md"


def review_filename(chapter: int) -> str:
    return f"第{chinese_number(chapter)}章-编辑审校.md"


CHAPTER_FILENAME_RE = re.compile(r"^第([零一二三四五六七八九十百千]+)章\.md$")


def chapter_from_filename(filename: str) -> int | None:
    match = CHAPTER_FILENAME_RE.match(filename)
    return chinese_to_int(match.group(1)) if match else None
