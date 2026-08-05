#!/usr/bin/env python3
"""Turn the batch controller's next state into a bounded task card for an AI writing workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ACTION_CARDS = {
    "rebase-outline": {
        "skill": "chapter-outline",
        "write_targets": ["03-outlines/chapter-NNNN.md"],
        "verify": "batch_controller.py mark --stage outline-locked",
        "instruction": "读取最新 Canon，重基目标章细纲；解决冲突后标记锁定。",
    },
    "mark-outline-locked": {
        "skill": "chapter-outline",
        "write_targets": [],
        "verify": "batch_controller.py mark --stage outline-locked",
        "instruction": "细纲已符合锁定条件；只记录状态转换。",
    },
    "draft": {
        "skill": "chapter-drafting",
        "write_targets": ["04-manuscript/chapter-NNNN.md", "03-outlines/context/chapter-NNNN-context.md"],
        "verify": "batch_controller.py mark --stage drafted",
        "instruction": "编译最小上下文后起草正文；只执行锁定细纲承诺，不自行冻结新事实。",
    },
    "review": {
        "skill": "chapter-editing",
        "write_targets": ["05-reviews/chapter-NNNN-edit.md"],
        "verify": "batch_controller.py mark --stage review-passed",
        "instruction": "执行 Canon、因果、体验、语言四层审校；报告必须给出机器可读锁定结论。",
    },
    "canon-commit": {
        "skill": "canon-management",
        "write_targets": ["01-canon/*.md", "01-canon/registry.json", "02-planning/chapter-index.md"],
        "verify": "batch_controller.py mark --stage canon-committed --canon-version VERSION",
        "instruction": "只提交授权范围内、锁定细纲已表达的常规状态变化；否则 halt 并生成待决策包。",
    },
    "lock": {
        "skill": "canon-management",
        "write_targets": ["02-planning/chapter-index.md"],
        "verify": "batch_controller.py mark --stage locked",
        "instruction": "核对审校、Canon 提交和章节索引后锁定章节。",
    },
    "batch-complete": {
        "skill": "serial-review",
        "write_targets": ["05-reviews/period-<range>.md"],
        "verify": "diagnose_project.py --intent continue",
        "instruction": "对已完成范围复盘承诺、节奏、伏笔、状态与下一批次风险。",
    },
    "halted": {
        "skill": "project-diagnosis",
        "write_targets": ["05-reviews/"],
        "verify": "batch_controller.py resume",
        "instruction": "阅读停止原因，修复前置或请求作者决策；不得跳过状态。",
    },
    "halt": {
        "skill": "project-diagnosis",
        "write_targets": ["05-reviews/"],
        "verify": "batch_controller.py resume",
        "instruction": "记录阻断原因、影响范围和恢复前提。",
    },
}


def controller_next(project: Path) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).with_name("batch_controller.py")), "next", "--project-dir", str(project)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError((result.stdout + result.stderr).strip() or str(error)) from error
    if result.returncode not in (0, 2):
        raise RuntimeError((result.stdout + result.stderr).strip())
    return payload


def replace_tokens(value: Any, chapter: int | None, canon_version: str | None) -> Any:
    if isinstance(value, str):
        if chapter:
            value = value.replace("NNNN", f"{chapter:04d}")
        return value.replace("VERSION", canon_version or "<current-version>")
    if isinstance(value, list):
        return [replace_tokens(item, chapter, canon_version) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce the next bounded AI task card for an active story batch.")
    parser.add_argument("next", nargs="?", default="next")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    state = controller_next(args.project_dir)
    action = state.get("action")
    card = ACTION_CARDS.get(action)
    if not card:
        raise SystemExit(f"Unsupported controller action: {action}")
    chapter = state.get("chapter")
    task = {key: replace_tokens(value, chapter, state.get("canon_version")) for key, value in card.items()}
    if action == "draft" and chapter:
        task["context_command"] = (
            f"python scripts/compile_chapter_context.py --project-dir {args.project_dir} --chapter {chapter} "
            "--purpose draft --fail-on-warning --force"
        )
    task["preconditions"] = [
        "不得越过 batch_controller 状态机。",
        "重大创作决策、未批准 Canon delta 或 S1 必须 halt。",
    ]
    result = {"controller": state, "task": task}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
