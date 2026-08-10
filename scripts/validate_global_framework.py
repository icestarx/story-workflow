#!/usr/bin/env python3
"""Validate the structural outputs required by story-workflow stages 0 and 1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_paths import chinese_number


REQUIRED_FILES = (
    "项目/项目简报.md",
    "项目/读者画像.md",
    "项目/题材定位.md",
    "项目/阶段零框架.md",
    "项目/全局框架检查清单.md",
    "项目/工作流配置.json",
    "项目/生产状态.json",
    "正典/核心设定总表.md",
    "正典/全局上下文.md",
    "正典/世界观.md",
    "正典/力量体系.md",
    "正典/谜案悬念.md",
    "正典/关系网络.md",
    "正典/读者体验.md",
    "正典/故事状态.md",
    "正典/时间线.md",
    "正典/伏笔台账.md",
    "正典/正典索引.json",
    "规划/全书总纲.md",
    "规划/长线系统.md",
    "规划/章节索引.md",
)
FRAMEWORK_HEADINGS = (
    "角色关系图谱框架",
    "伏笔系统架构",
    "情绪弧线总图",
    "力量体系框架",
    "世界观框架",
    "悬念系统架构",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate story-workflow initialization artifacts.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = args.project_dir
    errors: list[str] = []
    warnings: list[str] = []
    if not project.is_dir():
        errors.append(f"project directory not found: {project}")
    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            errors.append(f"missing required file: {relative}")

    framework_path = project / "项目/阶段零框架.md"
    if framework_path.is_file():
        text = framework_path.read_text(encoding="utf-8")
        for heading in FRAMEWORK_HEADINGS:
            if heading not in text:
                errors.append(f"frameworks.md missing heading: {heading}")

    config: dict[str, object] = {}
    config_path = project / "项目/工作流配置.json"
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"invalid workflow-config.json: {error}")
        if config and config.get("schema_version") != 1:
            errors.append("workflow-config.json schema_version must be 1")
        planning = config.get("planning", {}) if isinstance(config, dict) else {}
        automation = config.get("automation", {}) if isinstance(config, dict) else {}
        if not isinstance(planning, dict) or not isinstance(automation, dict):
            errors.append("workflow-config.json needs planning and automation objects")
        else:
            targets = planning.get("faction_targets")
            if not isinstance(targets, dict) or any(key not in targets for key in ("order", "neutral", "antagonistic")):
                errors.append("workflow-config.json needs faction_targets for order, neutral, antagonistic")
            if automation.get("max_contiguous_batch") != 100:
                warnings.append("max_contiguous_batch differs from the default 100; review batch safety")
            volume_count = planning.get("planned_volumes", 0)
            if isinstance(volume_count, int) and volume_count > 0:
                for volume in range(1, volume_count + 1):
                    path = project / "规划/分卷" / f"第{chinese_number(volume)}卷.md"
                    if not path.is_file():
                        errors.append(f"missing planned volume template: {path.relative_to(project)}")

    result = {"valid": not errors, "project": str(project), "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print("ERROR " + error)
        for warning in warnings:
            print("WARNING " + warning)
        if not errors:
            print(f"OK {project}")
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
