#!/usr/bin/env python3
"""Create a conservative, machine-readable baseline for a serial novel."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


WORDS_PER_CHAPTER_BY_GENRE = {
    "仙侠": 4000,
    "玄幻": 4000,
    "奇幻": 4000,
    "fantasy": 4000,
    "悬疑": 3500,
    "都市": 3500,
    "科幻": 3500,
    "mystery": 3500,
    "urban": 3500,
    "sci-fi": 3500,
    "言情": 3000,
    "romance": 3000,
}


def build_plan(
    total_words: int, genre: str, words_per_chapter: int | None, chapters_per_volume: int
) -> dict[str, Any]:
    if total_words <= 0:
        raise ValueError("total_words must be a positive integer")
    if not 20 <= chapters_per_volume <= 100:
        raise ValueError("chapters_per_volume must be between 20 and 100")

    normalized_genre = genre.strip().lower()
    chapter_words = words_per_chapter or WORDS_PER_CHAPTER_BY_GENRE.get(normalized_genre, 3500)
    if not 1000 <= chapter_words <= 10000:
        raise ValueError("words_per_chapter must be between 1000 and 10000")

    chapters = math.ceil(total_words / chapter_words)
    volume_count = math.ceil(chapters / chapters_per_volume)
    ranges = []
    start = 1
    for volume in range(1, volume_count + 1):
        end = min(chapters, start + chapters_per_volume - 1)
        ranges.append(
            {
                "volume": volume,
                "start_chapter": start,
                "end_chapter": end,
                "chapter_count": end - start + 1,
            }
        )
        start = end + 1

    return {
        "total_words_target": total_words,
        "genre": genre,
        "words_per_chapter_target": chapter_words,
        "planned_chapters": chapters,
        "planned_words": chapters * chapter_words,
        "volume_count": volume_count,
        "volume_ranges": ranges,
        "suggested_controls": {
            "core_cast_size": max(2, min(8, math.ceil(chapters / 75) + 1)),
            "active_foreshadow_cap": max(3, min(8, math.ceil(chapters / 60))),
            "review_every_chapters": min(20, max(5, chapters_per_volume // 3)),
            "note": "These are planning baselines, not mandatory creative quotas.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate a serial-novel planning baseline as UTF-8 JSON."
    )
    parser.add_argument("--total-words", required=True, type=int, help="Target total word count.")
    parser.add_argument("--genre", default="通用", help="Genre used only for the default chapter length.")
    parser.add_argument(
        "--words-per-chapter",
        type=int,
        help="Override the genre default chapter target.",
    )
    parser.add_argument(
        "--chapters-per-volume",
        type=int,
        default=60,
        help="Average chapters per volume; default: 60.",
    )
    args = parser.parse_args()

    try:
        plan = build_plan(
            args.total_words,
            args.genre,
            args.words_per_chapter,
            args.chapters_per_volume,
        )
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
