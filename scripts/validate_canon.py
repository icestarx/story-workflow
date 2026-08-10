#!/usr/bin/env python3
"""Validate the small, machine-readable Canon registry used by story-workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_COLLECTIONS = ("entities", "facts", "foreshadows", "changes")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate 正典/正典索引.json.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = args.project_dir
    path = project / "正典/正典索引.json"
    errors: list[str] = []
    warnings: list[str] = []
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"registry not found: {path}")
        registry = {}
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON: {error}")
        registry = {}

    if registry:
        if registry.get("schema_version") != 1:
            errors.append("schema_version must be 1")
        if not isinstance(registry.get("canon_version"), str) or not registry["canon_version"].strip():
            errors.append("canon_version must be a non-empty string")
        for name in REQUIRED_COLLECTIONS:
            if not isinstance(registry.get(name), list):
                errors.append(f"{name} must be a list")

        ids: set[str] = set()
        required_fields = {
            "entities": ("type", "name", "status", "source_file"),
            "facts": ("statement", "status", "source_steps", "visibility", "source_file"),
            "foreshadows": ("setup_chapter", "status", "target_window", "responsible_chapter"),
        }
        for name in ("entities", "facts", "foreshadows"):
            for index, item in enumerate(registry.get(name, [])):
                if not isinstance(item, dict):
                    errors.append(f"{name}[{index}] must be an object")
                    continue
                item_id = item.get("id")
                if not isinstance(item_id, str) or not item_id.strip():
                    errors.append(f"{name}[{index}] needs a non-empty id")
                elif item_id in ids:
                    errors.append(f"duplicate Canon id: {item_id}")
                else:
                    ids.add(item_id)
                for field in required_fields[name]:
                    if field not in item or item[field] in (None, "", []):
                        errors.append(f"{name}[{index}] needs {field}")
                if name in ("entities", "facts") and item.get("status") not in {"candidate", "confirmed", "tbd", "deprecated"}:
                    errors.append(f"{name}[{index}] has invalid status")
                if name == "foreshadows" and item.get("status") not in {"open", "advanced", "resolved", "retired", "candidate", "tbd"}:
                    errors.append(f"foreshadows[{index}] has invalid status")
                source_file = item.get("source_file")
                if source_file:
                    source_relative = Path(source_file)
                    if source_relative.is_absolute() or ".." in source_relative.parts:
                        errors.append(f"{name}[{index}] source_file must stay inside the project")
                    elif not (project / source_relative).is_file():
                        warnings.append(f"{name}[{index}] source_file not found: {source_file}")
                if name == "facts" and not isinstance(item.get("source_steps"), list):
                    errors.append(f"facts[{index}].source_steps must be a list")
                if name == "facts" and item.get("visibility") not in {"public", "character-limited", "author-only"}:
                    errors.append(f"facts[{index}] has invalid visibility")
                if name == "foreshadows":
                    for field in ("setup_chapter", "responsible_chapter"):
                        if not isinstance(item.get(field), int) or item[field] <= 0:
                            errors.append(f"foreshadows[{index}].{field} must be a positive integer")

        for index, change in enumerate(registry.get("changes", [])):
            if not isinstance(change, dict):
                errors.append(f"changes[{index}] must be an object")
                continue
            for field in ("version", "reason", "approved_by"):
                if not isinstance(change.get(field), str) or not change[field].strip():
                    warnings.append(f"changes[{index}] should have {field}")
            affected = change.get("affected_ids", [])
            if not isinstance(affected, list):
                errors.append(f"changes[{index}].affected_ids must be a list")

    valid = not errors and not (args.strict and warnings)
    result = {"valid": valid, "registry": str(path), "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print("ERROR " + error)
        for warning in warnings:
            print("WARNING " + warning)
        if valid:
            print(f"OK {path}")
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
