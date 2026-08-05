#!/usr/bin/env python3
"""Validate the structural outputs required by story-workflow stages 0 and 1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = (
    "00-project/brief.md",
    "00-project/reader-profile.md",
    "00-project/genre-positioning.md",
    "00-project/frameworks.md",
    "00-project/global-framework-checklist.md",
    "00-project/workflow-config.json",
    "00-project/production-state.json",
    "01-canon/core-settings.md",
    "01-canon/context.md",
    "01-canon/world.md",
    "01-canon/power-system.md",
    "01-canon/mysteries.md",
    "01-canon/relationships.md",
    "01-canon/reader-experience.md",
    "01-canon/state.md",
    "01-canon/timeline.md",
    "01-canon/foreshadow-ledger.md",
    "01-canon/registry.json",
    "02-planning/series-map.md",
    "02-planning/long-arcs.md",
    "02-planning/chapter-index.md",
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

    framework_path = project / "00-project/frameworks.md"
    if framework_path.is_file():
        text = framework_path.read_text(encoding="utf-8")
        for heading in FRAMEWORK_HEADINGS:
            if heading not in text:
                errors.append(f"frameworks.md missing heading: {heading}")

    config: dict[str, object] = {}
    config_path = project / "00-project/workflow-config.json"
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
                    path = project / "02-planning/volumes" / f"volume-{volume:02d}.md"
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
