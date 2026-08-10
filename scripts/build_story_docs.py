#!/usr/bin/env python3
"""Build a non-Canon manifest of project planning, outline, manuscript, and review files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def sorted_files(project: Path, directory: Path, pattern: str) -> list[str]:
    if not directory.is_dir():
        return []
    return [str(item.relative_to(project)).replace("\\", "/") for item in sorted(directory.rglob(pattern)) if item.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a story-workflow document manifest.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Default: 规划/项目清单.json")
    parser.add_argument("--force", action="store_true", help="Replace an existing manifest.")
    args = parser.parse_args()

    project = args.project_dir
    if not project.is_dir():
        parser.error(f"project directory not found: {project}")
    output = args.output or project / "规划/项目清单.json"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")

    manifest = {
        "project": str(project.resolve()),
        "canon_version": None,
        "volumes": sorted_files(project, project / "规划/分卷", "第*卷.md"),
        "outlines": sorted_files(project, project / "细纲", "第*章.md"),
        "manuscripts": sorted_files(project, project / "正文", "第*章.md"),
        "reviews": sorted_files(project, project / "审校", "*.md"),
    }
    registry = project / "正典/正典索引.json"
    if registry.is_file():
        try:
            manifest["canon_version"] = json.loads(registry.read_text(encoding="utf-8")).get("canon_version")
        except json.JSONDecodeError:
            manifest["canon_version"] = "invalid-registry"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.resolve()), "manifest": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
