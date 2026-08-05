#!/usr/bin/env python3
"""Build a non-Canon manifest of project planning, outline, manuscript, and review files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def sorted_files(path: Path, pattern: str) -> list[str]:
    if not path.is_dir():
        return []
    return [str(item.relative_to(path.parent.parent)).replace("\\", "/") for item in sorted(path.rglob(pattern)) if item.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a story-workflow document manifest.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Default: 02-planning/build-manifest.json")
    parser.add_argument("--force", action="store_true", help="Replace an existing manifest.")
    args = parser.parse_args()

    project = args.project_dir
    if not project.is_dir():
        parser.error(f"project directory not found: {project}")
    output = args.output or project / "02-planning/build-manifest.json"
    if output.exists() and not args.force:
        parser.error(f"output exists: {output}; use --force to replace it")

    manifest = {
        "project": str(project.resolve()),
        "canon_version": None,
        "volumes": sorted_files(project / "02-planning/volumes", "volume-*.md"),
        "outlines": sorted_files(project / "03-outlines", "chapter-*.md"),
        "manuscripts": sorted_files(project / "04-manuscript", "chapter-*.md"),
        "reviews": sorted_files(project / "05-reviews", "*.md"),
    }
    registry = project / "01-canon/registry.json"
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
