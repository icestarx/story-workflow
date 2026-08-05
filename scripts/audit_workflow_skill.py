#!/usr/bin/env python3
"""Audit the skill package for required routes, resources, and 1–150 step coverage."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_SUBSKILLS = (
    "project-bootstrap",
    "project-diagnosis",
    "story-positioning",
    "story-research",
    "world-design",
    "power-system-design",
    "faction-design",
    "mystery-design",
    "character-arc-design",
    "reader-experience-design",
    "series-architecture",
    "long-arc-planning",
    "volume-planning",
    "chapter-outline",
    "chapter-drafting",
    "chapter-editing",
    "canon-management",
    "global-review",
    "serial-production",
    "manuscript-quality-audit",
    "project-delivery",
    "serial-review",
    "publication-packaging",
)
REQUIRED_RESOURCES = (
    "references/step-map.md",
    "references/core-reference-kit.md",
    "references/automation-contract.md",
    "references/final-audit-contract.md",
    "references/workflow-maintenance.md",
    "references/editorial-board.md",
    "references/editorial-standards.md",
    "references/control-plane.md",
    "scripts/init_story_project.py",
    "scripts/validate_global_framework.py",
    "scripts/validate_canon.py",
    "scripts/validate_outline.py",
    "scripts/diagnose_project.py",
    "scripts/orchestrate_batch.py",
    "scripts/trace_canon_impact.py",
    "scripts/run_regression_suite.py",
    "scripts/batch_controller.py",
    "scripts/audit_manuscript.py",
    "scripts/generate_project_report.py",
)
STEP_RANGE_RE = re.compile(r"(?<!\d)(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?(?!\d)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit story-workflow package completeness.")
    parser.add_argument("--skill-dir", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.skill_dir
    errors: list[str] = []
    warnings: list[str] = []
    root_skill = root / "SKILL.md"
    if not root_skill.is_file():
        errors.append("root SKILL.md is missing")
        text = ""
    else:
        text = root_skill.read_text(encoding="utf-8")
        for stage in range(9):
            if f"阶段 {stage}" not in text:
                errors.append(f"root SKILL.md does not mention 阶段 {stage}")
        if "references/step-map.md" not in text:
            errors.append("root SKILL.md does not route to step-map.md")
        if "batch_controller.py" not in text:
            errors.append("root SKILL.md does not route to batch_controller.py")

    for name in REQUIRED_SUBSKILLS:
        if not (root / "sub-skills" / name / "SKILL.md").is_file():
            errors.append(f"missing sub-skill: {name}")
    for relative in REQUIRED_RESOURCES:
        if not (root / relative).is_file():
            errors.append(f"missing resource: {relative}")

    covered: set[int] = set()
    step_map = root / "references/step-map.md"
    if step_map.is_file():
        for match in STEP_RANGE_RE.finditer(step_map.read_text(encoding="utf-8")):
            start = int(match.group(1))
            end = int(match.group(2) or start)
            if start <= end:
                covered.update(range(start, end + 1))
    missing_steps = [number for number in range(1, 151) if number not in covered]
    if missing_steps:
        errors.append("step map does not cover: " + ", ".join(map(str, missing_steps)))
    if text and len(text.splitlines()) > 500:
        warnings.append("root SKILL.md exceeds 500 lines; move details to references")

    result = {"valid": not errors, "skill_dir": str(root), "errors": errors, "warnings": warnings, "covered_steps": len(covered.intersection(range(1, 151)))}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print("ERROR " + error)
        for warning in warnings:
            print("WARNING " + warning)
        if not errors:
            print(f"OK {root} (1–150 coverage: {result['covered_steps']}/150)")
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
