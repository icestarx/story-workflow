#!/usr/bin/env python3
"""Diagnose a story project and recommend a safe entry or recovery route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from project_paths import chapter_filename


CORE_FILES = (
    "项目/工作流配置.json",
    "项目/生产状态.json",
    "正典/正典索引.json",
    "正典/故事状态.md",
    "规划/章节索引.md",
)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def count_files(project: Path, relative: str, pattern: str) -> int:
    directory = project / relative
    return len(list(directory.glob(pattern))) if directory.is_dir() else 0


def find_references(project: Path, changed_id: str) -> list[str]:
    needle = f"[[{changed_id}]]"
    results: list[str] = []
    for path in project.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if needle in text or changed_id in text:
            results.append(str(path.relative_to(project)).replace("\\", "/"))
    return results


def route(intent: str, project: Path, chapter: int | None, active_batch: dict[str, Any] | None, missing: list[str], counts: dict[str, int]) -> dict[str, Any]:
    if not project.is_dir():
        return {"skill": "project-bootstrap", "action": "initialize-project", "reason": "项目目录不存在", "command": "init_story_project.py"}
    if missing:
        return {"skill": "project-bootstrap", "action": "repair-initialization", "reason": "缺少控制平面核心文件", "command": "validate_global_framework.py"}
    if intent == "create":
        return {"skill": "project-bootstrap", "action": "continue-initialization", "reason": "用户指定新建/初始化", "command": "validate_global_framework.py"}
    if intent == "revise":
        return {"skill": "canon-management", "action": "trace-impact-before-revision", "reason": "改设必须先影响追踪", "command": "trace_canon_impact.py"}
    if intent == "repair":
        return {"skill": "project-diagnosis", "action": "repair-from-blockers", "reason": "用户要求修复", "command": "run_regression_suite.py"}
    if intent == "audit":
        return {"skill": "manuscript-quality-audit", "action": "run-whole-project-audit", "reason": "用户要求审计", "command": "run_regression_suite.py"}
    if intent == "publish":
        return {"skill": "project-delivery", "action": "prepare-delivery", "reason": "用户要求输出/发布", "command": "generate_project_report.py"}
    if active_batch:
        return {"skill": "serial-production", "action": "resume-active-batch", "reason": "检测到可恢复的活动批次", "command": "orchestrate_batch.py next"}
    if intent == "write" and chapter:
        outline = project / "细纲" / chapter_filename(chapter)
        manuscript = project / "正文" / chapter_filename(chapter)
        if not outline.is_file():
            return {"skill": "chapter-outline", "action": "create-or-recover-outline", "reason": "目标章缺细纲", "command": "validate_outline.py"}
        if not manuscript.is_file():
            return {"skill": "serial-production", "action": "start-guarded-chapter-production", "reason": "目标章有细纲但无正文", "command": "batch_controller.py start"}
        return {"skill": "chapter-editing", "action": "review-or-revise-existing-chapter", "reason": "目标章已有正文", "command": "audit_manuscript.py"}
    if intent == "continue":
        if counts["outlines"] == 0:
            return {"skill": "chapter-outline", "action": "build-next-outline-batch", "reason": "尚无章节细纲", "command": "validate_outline.py"}
        if counts["outlines"] > counts["manuscripts"]:
            return {"skill": "serial-production", "action": "start-next-guarded-batch", "reason": "存在细纲但正文尚未覆盖", "command": "batch_controller.py start"}
        if counts["manuscripts"] > 0:
            return {"skill": "serial-review", "action": "review-and-plan-next-cycle", "reason": "现有正文已覆盖当前细纲", "command": "run_regression_suite.py"}
    return {"skill": "story-positioning", "action": "clarify-current-goal", "reason": "未提供可执行意图或章节", "command": "diagnose_project.py"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose a story-workflow project from any workflow node.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--intent", choices=("auto", "create", "continue", "write", "revise", "repair", "audit", "publish"), default="auto")
    parser.add_argument("--chapter", type=int, help="Target chapter for write/revision diagnosis.")
    parser.add_argument("--changed-id", action="append", default=[], help="Canon ID to trace before a revision; repeatable.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.chapter is not None and args.chapter <= 0:
        parser.error("--chapter must be positive")

    project = args.project_dir
    missing = [relative for relative in CORE_FILES if not (project / relative).is_file()] if project.is_dir() else list(CORE_FILES)
    registry = read_json(project / "正典/正典索引.json") if project.is_dir() else None
    state = read_json(project / "项目/生产状态.json") if project.is_dir() else None
    active_batch = state.get("active_batch") if state else None
    if not isinstance(active_batch, dict):
        active_batch = None
    intent = "continue" if args.intent == "auto" and active_batch else args.intent
    counts = {
        "volumes": count_files(project, "规划/分卷", "第*卷.md") if project.is_dir() else 0,
        "outlines": count_files(project, "细纲", "第*章.md") if project.is_dir() else 0,
        "manuscripts": count_files(project, "正文", "第*章.md") if project.is_dir() else 0,
        "reviews": count_files(project, "审校", "*.md") if project.is_dir() else 0,
    }
    recommendation = route(intent, project, args.chapter, active_batch, missing, counts)
    affected = {changed_id: find_references(project, changed_id) for changed_id in args.changed_id} if project.is_dir() else {}
    recovery_plan = [
        "先处理 blockers，禁止直接写正文绕过缺失前置。",
        f"调用 {recommendation['skill']} 执行 {recommendation['action']}。",
        "完成后重新运行 diagnose_project.py，确认状态已转移。",
    ]
    result = {
        "project": str(project),
        "intent": args.intent,
        "canon_version": registry.get("canon_version") if registry else None,
        "active_batch": active_batch,
        "artifact_counts": counts,
        "blockers": missing,
        "recommendation": recommendation,
        "affected_files": affected,
        "recovery_plan": recovery_plan,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
