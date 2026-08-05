#!/usr/bin/env python3
"""Persist and guard sequential production batches for story-workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_outline import validate_file


STAGES = ("candidate-outline", "outline-locked", "drafted", "review-passed", "canon-committed", "locked")
LOCKED_RE = re.compile(r"(?:细纲)?状态\s*[：:]\s*锁定")
CANON_VERSION_RE = re.compile(r"Canon\s*版本\s*[：:]\s*([^\s]+)", re.IGNORECASE)


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def state_path(project: Path) -> Path:
    return project / "00-project/production-state.json"


def load_state(project: Path) -> dict[str, Any]:
    path = state_path(project)
    if not path.is_file():
        raise ValueError("production state not found; run batch_controller.py init")
    state = load_json(path)
    if state.get("schema_version") != 1 or not isinstance(state.get("chapters"), dict):
        raise ValueError("invalid production-state.json")
    state.setdefault("history", [])
    return state


def save_state(project: Path, state: dict[str, Any]) -> None:
    state_path(project).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canon_version(project: Path) -> str:
    registry = load_json(project / "01-canon/registry.json")
    version = registry.get("canon_version")
    if not isinstance(version, str) or not version:
        raise ValueError("registry.json has no canon_version")
    return version


def config(project: Path) -> dict[str, Any]:
    path = project / "00-project/workflow-config.json"
    if not path.is_file():
        raise ValueError("workflow-config.json not found")
    value = load_json(path)
    if not isinstance(value.get("automation"), dict):
        raise ValueError("workflow-config.json has no automation configuration")
    return value


def outline_path(project: Path, chapter: int) -> Path:
    return project / "03-outlines" / f"chapter-{chapter:04d}.md"


def manuscript_path(project: Path, chapter: int) -> Path:
    return project / "04-manuscript" / f"chapter-{chapter:04d}.md"


def review_path(project: Path, chapter: int) -> Path:
    return project / "05-reviews" / f"chapter-{chapter:04d}-edit.md"


def outline_lock_status(project: Path, chapter: int, expected_version: str) -> tuple[bool, str]:
    path = outline_path(project, chapter)
    if not path.is_file():
        return False, "outline_missing"
    report = validate_file(path)
    if not report["valid"]:
        return False, "outline_contract_invalid"
    text = path.read_text(encoding="utf-8")
    if not LOCKED_RE.search(text):
        return False, "outline_not_locked"
    version = CANON_VERSION_RE.search(text)
    if not version:
        return False, "outline_missing_canon_version"
    if version.group(1) != expected_version:
        return False, "outline_canon_version_mismatch"
    return True, "ready"


def run_canon_validation(project: Path) -> tuple[bool, str]:
    command = [sys.executable, str(Path(__file__).with_name("validate_canon.py")), "--project-dir", str(project)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def append_history(state: dict[str, Any], event: str, **data: Any) -> None:
    state["history"].append({"at": now(), "event": event, **data})


def require_project(project: Path) -> None:
    if not project.is_dir():
        raise ValueError(f"project directory not found: {project}")


def range_preflight(project: Path, start: int, end: int) -> dict[str, Any]:
    errors: list[str] = []
    if start <= 0 or end < start:
        errors.append("chapter range must be positive and ascending")
    try:
        settings = config(project)
        max_size = settings["automation"].get("max_contiguous_batch", 100)
        if end - start + 1 > max_size:
            errors.append(f"range exceeds max_contiguous_batch ({max_size})")
    except (ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    valid_canon, canon_output = run_canon_validation(project)
    if not valid_canon:
        errors.append("Canon validation failed: " + canon_output)
    outlines: dict[str, str] = {}
    for chapter in range(start, end + 1):
        path = outline_path(project, chapter)
        if not path.is_file():
            outlines[str(chapter)] = "missing"
            errors.append(f"outline missing: {path}")
        else:
            report = validate_file(path)
            outlines[str(chapter)] = "valid" if report["valid"] else "invalid"
            if not report["valid"]:
                errors.append(f"outline contract invalid: {path}")
    return {"valid": not errors, "from": start, "to": end, "outlines": outlines, "errors": errors}


def command_init(args: argparse.Namespace) -> None:
    project = args.project_dir
    require_project(project)
    path = state_path(project)
    if path.exists() and not args.force:
        emit({"ok": True, "state": str(path), "action": "existing"})
        return
    state = {"schema_version": 1, "active_batch": None, "chapters": {}, "history": []}
    append_history(state, "controller_initialized")
    save_state(project, state)
    emit({"ok": True, "state": str(path), "action": "created"})


def command_preflight(args: argparse.Namespace) -> None:
    require_project(args.project_dir)
    emit(range_preflight(args.project_dir, args.start, args.end))


def command_start(args: argparse.Namespace) -> None:
    project = args.project_dir
    require_project(project)
    state = load_state(project)
    if state.get("active_batch"):
        raise ValueError("an active batch already exists; halt or finish it before starting another")
    report = range_preflight(project, args.start, args.end)
    if not report["valid"]:
        emit(report)
        raise SystemExit(1)
    if args.start > 1:
        prior = state["chapters"].get(str(args.start - 1), {})
        if prior.get("status") != "locked":
            raise ValueError("the chapter immediately before this batch must be locked")
    version = canon_version(project)
    for chapter in range(args.start, args.end + 1):
        state["chapters"].setdefault(str(chapter), {"status": "candidate-outline", "canon_version": None})
    state["active_batch"] = {
        "from": args.start,
        "to": args.end,
        "authorization": args.authorization,
        "started_canon_version": version,
        "status": "active",
    }
    append_history(state, "batch_started", **state["active_batch"])
    save_state(project, state)
    emit({"ok": True, "active_batch": state["active_batch"], "next": "run next to receive the first action"})


def command_next(args: argparse.Namespace) -> None:
    project = args.project_dir
    state = load_state(project)
    batch = state.get("active_batch")
    if not batch:
        raise ValueError("no active batch")
    if batch.get("status") != "active":
        emit({"ok": False, "action": "halted", "active_batch": batch})
        raise SystemExit(2)
    current_version = canon_version(project)
    for chapter in range(batch["from"], batch["to"] + 1):
        entry = state["chapters"].setdefault(str(chapter), {"status": "candidate-outline", "canon_version": None})
        status = entry.get("status")
        if status == "locked":
            continue
        if chapter > batch["from"] and state["chapters"].get(str(chapter - 1), {}).get("status") != "locked":
            emit({"ok": False, "action": "halt", "chapter": chapter, "reason": "previous_chapter_not_locked"})
            raise SystemExit(2)
        if status == "candidate-outline":
            ready, reason = outline_lock_status(project, chapter, current_version)
            emit({"ok": True, "action": "mark-outline-locked" if ready else "rebase-outline", "chapter": chapter, "reason": reason, "canon_version": current_version})
            return
        actions = {
            "outline-locked": "draft",
            "drafted": "review",
            "review-passed": "canon-commit",
            "canon-committed": "lock",
        }
        action = actions.get(status)
        if action:
            emit({"ok": True, "action": action, "chapter": chapter, "canon_version": current_version})
            return
        raise ValueError(f"unknown chapter state: {status}")
    state["active_batch"] = None
    append_history(state, "batch_completed", **batch)
    save_state(project, state)
    emit({"ok": True, "action": "batch-complete", "completed": {"from": batch["from"], "to": batch["to"]}})


def command_mark(args: argparse.Namespace) -> None:
    project = args.project_dir
    state = load_state(project)
    batch = state.get("active_batch")
    if not batch or not batch.get("from") <= args.chapter <= batch.get("to"):
        raise ValueError("chapter is not within the active batch")
    entry = state["chapters"].get(str(args.chapter))
    if not entry:
        raise ValueError("chapter is not initialized in production state")
    current = entry.get("status")
    target = args.stage
    if target not in STAGES or STAGES.index(target) != STAGES.index(current) + 1:
        raise ValueError(f"invalid transition: {current} -> {target}")
    current_version = canon_version(project)
    if target == "outline-locked":
        ready, reason = outline_lock_status(project, args.chapter, current_version)
        if not ready:
            raise ValueError(f"cannot lock outline: {reason}")
        entry["canon_version"] = current_version
    elif target == "drafted":
        path = manuscript_path(project, args.chapter)
        if not path.is_file() or len(path.read_text(encoding="utf-8").strip()) < 100:
            raise ValueError("draft file is missing or too short")
    elif target == "review-passed":
        path = review_path(project, args.chapter)
        if not path.is_file():
            raise ValueError("review report is missing")
        review = path.read_text(encoding="utf-8")
        if "S1 未解决：0" not in review or "锁定结论：可锁定" not in review:
            raise ValueError("review report does not contain a passing machine-readable conclusion")
    elif target == "canon-committed":
        if args.canon_version != current_version:
            raise ValueError("--canon-version must match the current registry canon_version")
        valid, details = run_canon_validation(project)
        if not valid:
            raise ValueError("Canon validation failed: " + details)
        entry["canon_version"] = current_version
    elif target == "locked":
        if entry.get("canon_version") != current_version:
            raise ValueError("chapter must be rebased after its Canon commit before locking")
    entry["status"] = target
    append_history(state, "chapter_marked", chapter=args.chapter, stage=target, canon_version=current_version)
    save_state(project, state)
    emit({"ok": True, "chapter": args.chapter, "status": target, "canon_version": current_version})


def command_halt(args: argparse.Namespace) -> None:
    state = load_state(args.project_dir)
    if not state.get("active_batch"):
        raise ValueError("no active batch")
    state["active_batch"]["status"] = "halted"
    state["active_batch"]["reason"] = args.reason
    append_history(state, "batch_halted", reason=args.reason)
    save_state(args.project_dir, state)
    emit({"ok": True, "action": "halted", "reason": args.reason})


def command_resume(args: argparse.Namespace) -> None:
    state = load_state(args.project_dir)
    if not state.get("active_batch") or state["active_batch"].get("status") != "halted":
        raise ValueError("no halted batch to resume")
    state["active_batch"]["status"] = "active"
    state["active_batch"].pop("reason", None)
    append_history(state, "batch_resumed")
    save_state(args.project_dir, state)
    emit({"ok": True, "action": "resumed", "active_batch": state["active_batch"]})


def command_status(args: argparse.Namespace) -> None:
    state = load_state(args.project_dir)
    emit({"ok": True, "active_batch": state.get("active_batch"), "chapters": state.get("chapters"), "history": state.get("history", [])[-20:]})


def main() -> None:
    parser = argparse.ArgumentParser(description="Control resumable sequential story production batches.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def project_argument(target: argparse.ArgumentParser) -> None:
        target.add_argument("--project-dir", type=Path, required=True)

    init_parser = subparsers.add_parser("init")
    project_argument(init_parser)
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(handler=command_init)

    preflight = subparsers.add_parser("preflight")
    project_argument(preflight)
    preflight.add_argument("--from", dest="start", type=int, required=True)
    preflight.add_argument("--to", dest="end", type=int, required=True)
    preflight.set_defaults(handler=command_preflight)

    start = subparsers.add_parser("start")
    project_argument(start)
    start.add_argument("--from", dest="start", type=int, required=True)
    start.add_argument("--to", dest="end", type=int, required=True)
    start.add_argument("--authorization", default="guarded", help="e.g. guarded or user-first-10")
    start.set_defaults(handler=command_start)

    next_parser = subparsers.add_parser("next")
    project_argument(next_parser)
    next_parser.set_defaults(handler=command_next)

    mark = subparsers.add_parser("mark")
    project_argument(mark)
    mark.add_argument("--chapter", type=int, required=True)
    mark.add_argument("--stage", choices=STAGES[1:], required=True)
    mark.add_argument("--canon-version", default="", help="Required when marking canon-committed")
    mark.set_defaults(handler=command_mark)

    halt = subparsers.add_parser("halt")
    project_argument(halt)
    halt.add_argument("--reason", required=True)
    halt.set_defaults(handler=command_halt)

    resume = subparsers.add_parser("resume")
    project_argument(resume)
    resume.set_defaults(handler=command_resume)

    status = subparsers.add_parser("status")
    project_argument(status)
    status.set_defaults(handler=command_status)

    args = parser.parse_args()
    try:
        args.handler(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
