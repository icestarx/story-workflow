#!/usr/bin/env python3
"""Create reversible evidence folders for bounded Agent Skill evolution."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


RUN_DIRECTORY = ".skill-evolution"
SELF_SKILL_DIRECTORY = Path(__file__).resolve().parents[1]
RESULT_COLUMNS = (
    "timestamp",
    "round",
    "status",
    "hypothesis",
    "vote",
    "mode",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def target_root(target: Path) -> Path:
    resolved = target.resolve()
    if resolved.is_file():
        if resolved.name != "SKILL.md":
            raise ValueError("target file must be named SKILL.md")
        return resolved.parent
    if not resolved.is_dir():
        raise ValueError(f"target does not exist: {resolved}")
    return resolved


def skill_files(root: Path) -> list[Path]:
    files = sorted(
        path
        for path in root.rglob("SKILL.md")
        if RUN_DIRECTORY not in path.parts and path.parent.resolve() != SELF_SKILL_DIRECTORY
    )
    if not files:
        raise ValueError(f"no SKILL.md files found below: {root}")
    return files


def test_prompt_files(files: list[Path]) -> list[Path]:
    return [path.parent / "test-prompts.json" for path in files if (path.parent / "test-prompts.json").is_file()]


def run_dir(root: Path, run_id: str) -> Path:
    return root / RUN_DIRECTORY / run_id


def valid_relative(root: Path, value: str) -> Path:
    result = (root / value).resolve()
    try:
        result.relative_to(root)
    except ValueError as exc:
        raise ValueError("file must stay inside the target root") from exc
    return result


def cmd_inspect(args: argparse.Namespace) -> None:
    root = target_root(Path(args.target))
    files = skill_files(root)
    tests = test_prompt_files(files)
    data = {
        "target_root": str(root),
        "skill_count": len(files),
        "skills": [str(path.relative_to(root)) for path in files],
        "test_prompt_count": len(tests),
        "test_prompts": [str(path.relative_to(root)) for path in tests],
        "missing_test_prompts": [
            str(path.parent.relative_to(root)) for path in files if (path.parent / "test-prompts.json") not in tests
        ],
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def copy_into_snapshot(root: Path, destination: Path, source: Path) -> dict[str, str]:
    relative = source.relative_to(root)
    copied = destination / relative
    copied.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, copied)
    return {"path": str(relative), "sha256": sha256(source)}


def cmd_prepare(args: argparse.Namespace) -> None:
    root = target_root(Path(args.target))
    destination = run_dir(root, args.run_id)
    if destination.exists():
        raise ValueError(f"run already exists: {destination}")
    files = skill_files(root)
    destination.mkdir(parents=True, exist_ok=False)
    baseline = destination / "baseline"
    manifest = {
        "run_id": args.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_root": str(root),
        "files": [copy_into_snapshot(root, baseline, path) for path in files],
        "test_prompts": [copy_into_snapshot(root, baseline, path) for path in test_prompt_files(files)],
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (destination / "results.tsv").open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=RESULT_COLUMNS, delimiter="\t").writeheader()
    print(json.dumps({"run_dir": str(destination), "snapshot_files": len(manifest["files"])}, ensure_ascii=False))


def cmd_checkpoint(args: argparse.Namespace) -> None:
    root = target_root(Path(args.target))
    source = valid_relative(root, args.file)
    if not source.is_file():
        raise ValueError(f"file is missing: {source}")
    round_root = run_dir(root, args.run_id) / f"round-{args.round}"
    destination = round_root / "before"
    relative = source.relative_to(root)
    if (destination / relative).is_file():
        raise ValueError(f"file already has a round checkpoint: {relative}")
    record = copy_into_snapshot(root, destination, source)
    manifest_path = round_root / "manifest.json"
    records = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else []
    records.append(record)
    manifest_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))


def cmd_record(args: argparse.Namespace) -> None:
    root = target_root(Path(args.target))
    results = run_dir(root, args.run_id) / "results.tsv"
    if not results.is_file():
        raise ValueError(f"results log is missing: {results}")
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "round": str(args.round),
        "status": args.status,
        "hypothesis": args.hypothesis,
        "vote": args.vote,
        "mode": args.mode,
    }
    with results.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=RESULT_COLUMNS, delimiter="\t").writerow(row)
    print(json.dumps(row, ensure_ascii=False))


def cmd_hash(args: argparse.Namespace) -> None:
    path = Path(args.path).resolve()
    if not path.is_file():
        raise ValueError(f"file is missing: {path}")
    print(sha256(path))


def cmd_restore(args: argparse.Namespace) -> None:
    root = target_root(Path(args.target))
    destination = valid_relative(root, args.file)
    relative = destination.relative_to(root)
    source = run_dir(root, args.run_id) / f"round-{args.round}" / "before" / relative
    if not source.is_file():
        raise ValueError(f"round snapshot is missing: {source}")
    if not destination.is_file():
        raise ValueError(f"destination is missing: {destination}")
    actual_hash = sha256(destination)
    if actual_hash != args.expected_current_hash:
        raise ValueError("current file hash differs; refusing to overwrite a possible external edit")
    shutil.copy2(source, destination)
    print(json.dumps({"restored": str(destination), "sha256": sha256(destination)}, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    inspect = commands.add_parser("inspect", help="inventory skill and test-prompt files")
    inspect.add_argument("--target", required=True)
    inspect.set_defaults(func=cmd_inspect)

    prepare = commands.add_parser("prepare", help="snapshot a baseline and create results.tsv")
    prepare.add_argument("--target", required=True)
    prepare.add_argument("--run-id", required=True)
    prepare.set_defaults(func=cmd_prepare)

    checkpoint = commands.add_parser("checkpoint", help="copy a pre-round file snapshot")
    checkpoint.add_argument("--target", required=True)
    checkpoint.add_argument("--run-id", required=True)
    checkpoint.add_argument("--round", required=True, type=int, choices=range(1, 4))
    checkpoint.add_argument("--file", required=True)
    checkpoint.set_defaults(func=cmd_checkpoint)

    record = commands.add_parser("record", help="append an evolution decision")
    record.add_argument("--target", required=True)
    record.add_argument("--run-id", required=True)
    record.add_argument("--round", required=True, type=int, choices=range(0, 4))
    record.add_argument("--status", required=True, choices=("kept", "restored", "skipped", "baseline"))
    record.add_argument("--hypothesis", required=True)
    record.add_argument("--vote", required=True)
    record.add_argument("--mode", required=True, choices=("paired", "full-test", "dry-run", "generated-unconfirmed"))
    record.set_defaults(func=cmd_record)

    digest = commands.add_parser("hash", help="print SHA-256 for a file")
    digest.add_argument("--path", required=True)
    digest.set_defaults(func=cmd_hash)

    restore = commands.add_parser("restore", help="restore one rejected candidate if it is unchanged")
    restore.add_argument("--target", required=True)
    restore.add_argument("--run-id", required=True)
    restore.add_argument("--round", required=True, type=int, choices=range(1, 4))
    restore.add_argument("--file", required=True)
    restore.add_argument("--expected-current-hash", required=True)
    restore.set_defaults(func=cmd_restore)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error


if __name__ == "__main__":
    main()
