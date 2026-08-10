#!/usr/bin/env python3
"""Create evidence-based whole-manuscript technical and pattern audit reports."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from project_paths import chapter_filename, chapter_from_filename


SENTENCE_RE = re.compile(r"[^。！？!?\n]+[。！？!?]?")


def load_patterns(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        term, _, severity = line.partition("\t")
        rows.append((term.strip(), severity.strip() or "review"))
    return rows


def chapter_number(path: Path) -> int | None:
    return chapter_from_filename(path.name)


def find_line_hits(text: str, term: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        count = line.count(term)
        if count:
            hits.append({"line": number, "count": count, "excerpt": line.strip()[:160]})
    return hits


def repeated_paragraphs(text: str) -> list[dict[str, object]]:
    seen: dict[str, list[int]] = defaultdict(list)
    for number, paragraph in enumerate(re.split(r"\n\s*\n", text), start=1):
        normalized = re.sub(r"\s+", "", paragraph)
        if len(normalized) >= 30 and not normalized.startswith("#"):
            seen[normalized].append(number)
    return [{"paragraphs": positions, "excerpt": value[:120]} for value, positions in seen.items() if len(positions) > 1]


def repeated_sentence_starts(text: str, threshold: int) -> list[dict[str, object]]:
    starts: dict[str, int] = defaultdict(int)
    for sentence in SENTENCE_RE.findall(text):
        normalized = re.sub(r"^[\s\"“‘（(]+", "", sentence.strip())
        if len(normalized) >= 8:
            starts[normalized[:8]] += 1
    return [{"start": start, "count": count} for start, count in starts.items() if count >= threshold]


def markdown_report(result: dict[str, object]) -> str:
    lines = ["# 全书技术与表达模式审计", "", f"- 扫描章节数：{result['chapter_count']}", f"- 需要人工复核的项目：{result['review_count']}", ""]
    if result["missing_chapters"]:
        lines.extend(["## 缺失章节", "", *[f"- {item}" for item in result["missing_chapters"]], ""])
    if result["technical_issues"]:
        lines.extend(["## 技术问题", ""])
        for item in result["technical_issues"]:
            lines.append(f"- 第 {item['chapter']} 章：{item['issue']}")
        lines.append("")
    for title, key in (("禁用项命中", "term_hits"), ("自定义表达模式", "pattern_hits"), ("重复段落", "duplicate_paragraphs"), ("高频句首信号", "repeated_starts")):
        rows = result[key]
        lines.extend([f"## {title}", ""])
        if not rows:
            lines.append("- 无")
        else:
            for row in rows:
                lines.append("- " + json.dumps(row, ensure_ascii=False))
        lines.append("")
    lines.extend(["## 解释", "", "本报告列出可定位的规则命中和重复信号，不判定文本是否由 AI 创作，也不自动修改正文。由编辑结合场景功能、人物声音和项目风格卡作最终判断。", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit all manuscript chapters for deterministic issues and review signals.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--expected-chapters", type=int, help="Check coverage from 1 through N.")
    parser.add_argument("--terms-file", type=Path, help="Default: 项目/禁用词.txt")
    parser.add_argument("--style-patterns", type=Path, help="Default: 项目/风格模式.txt")
    parser.add_argument("--repeat-threshold", type=int, default=5)
    parser.add_argument("--min-nonspace-chars", type=int, default=100, help="Flag chapters shorter than this; default: 100.")
    parser.add_argument("--output", type=Path, help="Default: 审校/最终/技术审计.md")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.expected_chapters is not None and args.expected_chapters <= 0:
        parser.error("--expected-chapters must be positive")
    if args.repeat_threshold < 2:
        parser.error("--repeat-threshold must be at least 2")
    if args.min_nonspace_chars < 1:
        parser.error("--min-nonspace-chars must be positive")

    project = args.project_dir
    manuscript_dir = project / "正文"
    if not manuscript_dir.is_dir():
        parser.error(f"manuscript directory not found: {manuscript_dir}")
    term_rules = load_patterns(args.terms_file or project / "项目/禁用词.txt")
    style_rules = load_patterns(args.style_patterns or project / "项目/风格模式.txt")
    paths = sorted(manuscript_dir.glob("第*章.md"))
    discovered = {chapter_number(path) for path in paths if chapter_number(path) is not None}

    result: dict[str, object] = {
        "chapter_count": len(paths),
        "missing_chapters": [chapter_filename(number) for number in range(1, (args.expected_chapters or 0) + 1) if number not in discovered],
        "technical_issues": [],
        "term_hits": [],
        "pattern_hits": [],
        "duplicate_paragraphs": [],
        "repeated_starts": [],
    }
    for path in paths:
        chapter = chapter_number(path)
        text = path.read_text(encoding="utf-8")
        non_space_length = len(re.sub(r"\s+", "", text))
        if not text.lstrip().startswith("#"):
            result["technical_issues"].append({"chapter": chapter, "issue": "缺少 Markdown 章节标题"})
        if non_space_length < args.min_nonspace_chars:
            result["technical_issues"].append({"chapter": chapter, "issue": f"正文少于 {args.min_nonspace_chars} 个非空白字符"})
        for term, severity in term_rules:
            hits = find_line_hits(text, term)
            if hits:
                result["term_hits"].append({"chapter": chapter, "term": term, "severity": severity, "hits": hits})
        for pattern, severity in style_rules:
            hits = find_line_hits(text, pattern)
            if hits:
                result["pattern_hits"].append({"chapter": chapter, "pattern": pattern, "severity": severity, "hits": hits})
        for duplicate in repeated_paragraphs(text):
            result["duplicate_paragraphs"].append({"chapter": chapter, **duplicate})
        for repeated in repeated_sentence_starts(text, args.repeat_threshold):
            result["repeated_starts"].append({"chapter": chapter, **repeated})

    result["review_count"] = sum(len(result[key]) for key in ("missing_chapters", "technical_issues", "term_hits", "pattern_hits", "duplicate_paragraphs", "repeated_starts"))
    output = args.output or project / "审校/最终/技术审计.md"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown_report(result), encoding="utf-8")
    result["output"] = str(output.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"OK {output} ({result['review_count']} review items)")


if __name__ == "__main__":
    main()
