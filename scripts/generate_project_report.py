#!/usr/bin/env python3
"""Generate a concise delivery summary and file inventory for a novel project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def files(project: Path, relative: str, pattern: str) -> list[str]:
    directory = project / relative
    if not directory.is_dir():
        return []
    return [str(path.relative_to(project)).replace("\\", "/") for path in sorted(directory.glob(pattern)) if path.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a story-workflow project delivery report.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Default: 发布/项目总结.md")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = args.project_dir
    if not project.is_dir():
        parser.error(f"project directory not found: {project}")
    output = args.output or project / "发布/项目总结.md"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")

    registry_path = project / "正典/正典索引.json"
    production_path = project / "项目/生产状态.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.is_file() else {}
    production = json.loads(production_path.read_text(encoding="utf-8")) if production_path.is_file() else {}
    chapter_states = production.get("chapters", {}) if isinstance(production, dict) else {}
    locked = sorted(int(number) for number, entry in chapter_states.items() if entry.get("status") == "locked")
    inventory = {
        "volumes": files(project, "规划/分卷", "第*卷.md"),
        "outlines": files(project, "细纲", "第*章.md"),
        "manuscripts": files(project, "正文", "第*章.md"),
        "reviews": files(project, "审校", "*.md") + files(project, "审校/最终", "*.md"),
    }
    lines = [
        "# 项目交付总结",
        "",
        f"- Canon 版本：{registry.get('canon_version', '未知')}",
        f"- 已锁定章节：{', '.join(str(number) for number in locked) or '无'}",
        f"- 活动批次：{json.dumps(production.get('active_batch'), ensure_ascii=False) if production.get('active_batch') else '无'}",
        "",
        "## 文件清单",
        "",
    ]
    for label, entries in inventory.items():
        lines.append(f"### {label}")
        lines.append("")
        lines.extend([f"- {entry}" for entry in entries] or ["- 无"])
        lines.append("")
    lines.extend(["## 未决项与开放伏笔", "", "- 请从 正典/全局上下文.md、正典/伏笔台账.md 和最终审计报告补充。", ""])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    result = {"output": str(output.resolve()), "canon_version": registry.get("canon_version"), "locked_chapters": locked, "inventory": inventory}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"OK {output}")


if __name__ == "__main__":
    main()
