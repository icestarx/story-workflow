#!/usr/bin/env python3
"""Run side-effect-free structural regression checks for a story-workflow project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from project_paths import chapter_filename, review_filename


def run(script: str, arguments: list[str]) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).with_name(script)), *arguments, "--json"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"raw": (result.stdout + result.stderr).strip()}
    return {"ok": result.returncode == 0, "payload": payload}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run story-workflow regression checks without modifying project files.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--expected-chapters", type=int, help="Override planned chapter count for outline coverage.")
    parser.add_argument("--strict", action="store_true", help="Require manuscript coverage as well as outline coverage.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    project = args.project_dir
    if not project.is_dir():
        parser.error(f"project directory not found: {project}")

    config_path = project / "项目/工作流配置.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    planning = config.get("planning", {}) if isinstance(config, dict) else {}
    expected = args.expected_chapters if args.expected_chapters is not None else planning.get("planned_chapters", 0)
    checks: dict[str, Any] = {
        "framework": run("validate_global_framework.py", ["--project-dir", str(project)]),
        "canon": run("validate_canon.py", ["--project-dir", str(project)]),
    }
    outline_dir = project / "细纲"
    if isinstance(expected, int) and expected > 0 and outline_dir.is_dir():
        checks["outlines"] = run("validate_outline.py", ["--outline-dir", str(outline_dir), "--expected-chapters", str(expected)])
    else:
        checks["outlines"] = {"ok": True, "payload": {"skipped": "planned chapter count is TBD or no outline directory"}}

    production_path = project / "项目/生产状态.json"
    production = json.loads(production_path.read_text(encoding="utf-8")) if production_path.is_file() else {}
    state_errors: list[str] = []
    for number, entry in production.get("chapters", {}).items() if isinstance(production, dict) else []:
        status = entry.get("status") if isinstance(entry, dict) else None
        if status == "locked":
            chapter = int(number)
            if not (project / "正文" / chapter_filename(chapter)).is_file():
                state_errors.append(f"locked chapter {chapter} is missing manuscript")
            if not (project / "审校" / review_filename(chapter)).is_file():
                state_errors.append(f"locked chapter {chapter} is missing review")
            if not entry.get("canon_version"):
                state_errors.append(f"locked chapter {chapter} has no recorded Canon version")
    checks["production_state"] = {"ok": not state_errors, "payload": {"errors": state_errors}}

    manuscript_count = len(list((project / "正文").glob("第*章.md"))) if (project / "正文").is_dir() else 0
    if args.strict and isinstance(expected, int) and expected > manuscript_count:
        checks["manuscript_coverage"] = {"ok": False, "payload": {"error": f"expected {expected} manuscripts, found {manuscript_count}"}}
    else:
        checks["manuscript_coverage"] = {"ok": True, "payload": {"manuscript_count": manuscript_count}}

    valid = all(check["ok"] for check in checks.values())
    result = {"valid": valid, "project": str(project), "checks": checks}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
