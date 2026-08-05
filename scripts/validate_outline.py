#!/usr/bin/env python3
"""Validate required fields and optional project-wide coverage for chapter outlines."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "章节信息",
    "入章状态",
    "核心事件与因果",
    "场景节拍",
    "情绪曲线",
    "章首钩子",
    "爽点与代价",
    "伏笔操作",
    "角色状态变化",
    "章尾钩子",
    "字数预算",
    "Canon 冲突检查",
)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
CHAPTER_RE = re.compile(r"chapter-(\d{4})\.md$", re.IGNORECASE)


def validate_file(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    headings = [match.group(1).strip() for match in HEADING_RE.finditer(text)]
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in headings]
    empty: list[str] = []
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        if heading not in REQUIRED_HEADINGS:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if not text[match.end() : end].strip():
            empty.append(heading)
    return {"path": str(path), "missing": missing, "empty": empty, "valid": not missing and not empty}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate story-workflow chapter outline contracts.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--outline", type=Path, help="One chapter outline Markdown file.")
    target.add_argument("--outline-dir", type=Path, help="Directory containing chapter-NNNN.md outlines.")
    parser.add_argument("--expected-chapters", type=int, help="Check coverage from chapter 0001 through this number.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human-readable output.")
    args = parser.parse_args()

    paths = [args.outline] if args.outline else sorted(args.outline_dir.glob("chapter-*.md"))
    errors: list[str] = []
    reports: list[dict[str, object]] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            errors.append(f"outline does not exist: {path}")
            continue
        reports.append(validate_file(path))

    coverage_missing: list[str] = []
    if args.expected_chapters is not None:
        if args.expected_chapters <= 0:
            parser.error("--expected-chapters must be positive")
        discovered = {int(match.group(1)) for path in paths if (match := CHAPTER_RE.search(path.name))}
        coverage_missing = [f"chapter-{number:04d}.md" for number in range(1, args.expected_chapters + 1) if number not in discovered]
        if coverage_missing:
            errors.append("missing expected chapter files")

    valid = not errors and bool(reports) and all(bool(report["valid"]) for report in reports)
    result = {"valid": valid, "reports": reports, "errors": errors, "coverage_missing": coverage_missing}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            label = "OK" if report["valid"] else "FAIL"
            print(f"{label} {report['path']}")
            if report["missing"]:
                print("  missing: " + ", ".join(report["missing"]))
            if report["empty"]:
                print("  empty: " + ", ".join(report["empty"]))
        for error in errors:
            print("ERROR " + error)
        if coverage_missing:
            print("  coverage missing: " + ", ".join(coverage_missing))
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
