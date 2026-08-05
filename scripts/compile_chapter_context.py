#!/usr/bin/env python3
"""Compile a bounded, traceable context packet for one chapter draft."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CANON_ID_RE = re.compile(r"\[\[([A-Za-z][A-Za-z0-9_.-]*)\]\]")


def read_clipped(path: Path, limit: int, tail: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    if len(text) <= limit:
        return text.strip()
    if tail:
        return "[前文已截断]\n" + text[-limit:].strip()
    return text[:limit].strip() + "\n[内容已截断]"


def section(label: str, path: Path, limit: int, tail: bool = False) -> str:
    return f"## {label}\n\n来源：{path}\n\n{read_clipped(path, limit, tail)}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile the minimum context needed to draft one chapter.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--output", type=Path, help="Output packet; default is 03-outlines/context/chapter-NNNN-context.md")
    parser.add_argument("--purpose", choices=("draft", "revise", "audit"), default="draft")
    parser.add_argument("--previous-chapters", type=int, default=2, help="Number of previous chapter endings to include; default: 2.")
    parser.add_argument("--include-id", action="append", default=[], help="Additional Canon ID to include; repeatable.")
    parser.add_argument("--max-chars-per-file", type=int, default=6000)
    parser.add_argument("--fail-on-warning", action="store_true", help="Return nonzero if an explicit Canon reference cannot be resolved.")
    parser.add_argument("--force", action="store_true", help="Replace an existing context packet.")
    args = parser.parse_args()

    if args.chapter <= 0:
        parser.error("--chapter must be positive")
    if args.max_chars_per_file < 500:
        parser.error("--max-chars-per-file must be at least 500")
    if args.previous_chapters < 0:
        parser.error("--previous-chapters must be non-negative")
    project = args.project_dir
    outline = project / "03-outlines" / f"chapter-{args.chapter:04d}.md"
    if not outline.is_file():
        parser.error(f"locked outline not found: {outline}")

    output = args.output or project / "03-outlines/context" / f"chapter-{args.chapter:04d}-context.md"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")

    sources: list[tuple[str, Path, bool]] = []
    base_sources = (
        ("项目简报", project / "00-project/brief.md", False),
        ("风格卡", project / "00-project/style-card.md", False),
        ("锁定细纲", outline, False),
        ("当前状态", project / "01-canon/state.md", True),
        ("全局上下文追踪", project / "01-canon/context.md", True),
        ("时间线（末段）", project / "01-canon/timeline.md", True),
        ("活跃伏笔", project / "01-canon/foreshadow-ledger.md", True),
        ("世界硬规则", project / "01-canon/world.md", False),
        ("力量限制", project / "01-canon/power-system.md", False),
        ("章节索引", project / "02-planning/chapter-index.md", True),
    )
    sources.extend((label, path, tail) for label, path, tail in base_sources if path.is_file())
    for prior_chapter in range(max(1, args.chapter - args.previous_chapters), args.chapter):
        previous = project / "04-manuscript" / f"chapter-{prior_chapter:04d}.md"
        if previous.is_file():
            sources.append((f"第 {prior_chapter} 章正文末段", previous, True))
    if args.purpose in {"revise", "audit"}:
        manuscript = project / "04-manuscript" / f"chapter-{args.chapter:04d}.md"
        review = project / "05-reviews" / f"chapter-{args.chapter:04d}-edit.md"
        if manuscript.is_file():
            sources.append(("目标章正文", manuscript, False))
        if review.is_file():
            sources.append(("目标章既有审校", review, False))

    warnings: list[str] = []
    registry_path = project / "01-canon/registry.json"
    referenced_ids = sorted(set(CANON_ID_RE.findall(outline.read_text(encoding="utf-8"))).union(args.include_id))
    resolved_paths: set[Path] = {path for _, path, _ in sources}
    if referenced_ids and registry_path.is_file():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            records = registry.get("entities", []) + registry.get("facts", []) + registry.get("foreshadows", [])
            by_id = {record.get("id"): record for record in records if isinstance(record, dict)}
            for canon_id in referenced_ids:
                record = by_id.get(canon_id)
                if not record:
                    warnings.append(f"未在 registry.json 找到 Canon ID：{canon_id}")
                    continue
                source_file = record.get("source_file")
                source_candidate = Path(source_file) if isinstance(source_file, str) else None
                path = project / source_candidate if source_candidate else None
                if source_candidate and (source_candidate.is_absolute() or ".." in source_candidate.parts):
                    warnings.append(f"Canon ID 的源文件越出项目目录：{canon_id}")
                elif not path or not path.is_file():
                    warnings.append(f"Canon ID 缺少可读取源文件：{canon_id}")
                elif path not in resolved_paths:
                    sources.append((f"关联 Canon：{canon_id}", path, False))
                    resolved_paths.add(path)
        except json.JSONDecodeError:
            warnings.append("registry.json 无法解析；未加载显式关联 Canon")
    elif referenced_ids:
        warnings.append("细纲引用了 Canon ID，但 registry.json 不存在")

    canon_version = "未知"
    if registry_path.is_file():
        try:
            canon_version = str(json.loads(registry_path.read_text(encoding="utf-8")).get("canon_version", "未知"))
        except json.JSONDecodeError:
            pass
    parts = [
        f"# 第 {args.chapter} 章上下文包\n",
        f"- 用途：{args.purpose}\n",
        f"- Canon 版本：{canon_version}\n",
        f"- Canon 显式引用：{', '.join(referenced_ids) or '无'}\n",
    ]
    if warnings:
        parts.append("## 写前警告\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n")
    for label, path, tail in sources:
        parts.append(section(label, path, args.max_chars_per_file, tail))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.resolve()), "chapter": args.chapter, "sources": [str(path) for _, path, _ in sources], "warnings": warnings}, ensure_ascii=False, indent=2))
    if warnings and args.fail_on_warning:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
