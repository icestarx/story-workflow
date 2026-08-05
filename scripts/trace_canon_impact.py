#!/usr/bin/env python3
"""Trace files that reference proposed Canon changes before a revision is approved."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {".md", ".json", ".txt"}


def category(relative: str) -> str:
    if relative.startswith("01-canon/"):
        return "Canon"
    if relative.startswith("02-planning/"):
        return "规划"
    if relative.startswith("03-outlines/"):
        return "细纲"
    if relative.startswith("04-manuscript/"):
        return "正文"
    if relative.startswith("05-reviews/"):
        return "审校"
    return "项目资料"


def scan(project: Path, changed_id: str) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    needle = f"[[{changed_id}]]"
    for path in project.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if needle not in text and changed_id not in text:
            continue
        relative = str(path.relative_to(project)).replace("\\", "/")
        references.append({"file": relative, "category": category(relative), "explicit_reference": "yes" if needle in text else "no"})
    return references


def report_markdown(project: Path, change_ids: list[str], result: dict[str, Any]) -> str:
    lines = ["# Canon 改设影响分析", "", f"- 项目：{project}", f"- 变更 ID：{', '.join(change_ids)}", "", "## 受影响文件", ""]
    for changed_id in change_ids:
        lines.append(f"### {changed_id}")
        lines.append("")
        entries = result[changed_id]
        if not entries:
            lines.append("- 未发现显式引用；仍须人工检查隐含依赖。")
        else:
            for entry in entries:
                lines.append(f"- [{entry['category']}] {entry['file']}（显式引用：{entry['explicit_reference']}）")
        lines.append("")
    lines.extend([
        "## 迁移顺序",
        "",
        "1. 先修复/批准 Canon 与状态；2. 重基受影响细纲；3. 审核已写正文和发布文本；4. 重新运行相关回归检查；5. 记录未迁移项。",
        "",
        "本报告只追踪可检索的引用；逻辑、主题、读者预期等隐含影响必须由 canon-management 和 global-review 补充判断。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Trace impact before changing Canon facts.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--id", dest="ids", action="append", required=True, help="Canon ID; repeatable.")
    parser.add_argument("--output", type=Path, help="Default: 05-reviews/impact-<first-id>.md")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    project = args.project_dir
    if not project.is_dir():
        parser.error(f"project directory not found: {project}")
    results = {changed_id: scan(project, changed_id) for changed_id in args.ids}
    safe_name = args.ids[0].replace("/", "-").replace("\\", "-")
    output = args.output or project / "05-reviews" / f"impact-{safe_name}.md"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report_markdown(project, args.ids, results), encoding="utf-8")
    result = {"output": str(output.resolve()), "ids": args.ids, "affected": results}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"OK {output}")


if __name__ == "__main__":
    main()
