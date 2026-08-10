#!/usr/bin/env python3
"""Create the v2 story-workflow project layout without replacing existing work."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from project_paths import chinese_number


DIRECTORIES = (
    "项目",
    "正典/势力",
    "正典/人物",
    "规划/分卷",
    "细纲/上下文",
    "正文",
    "审校",
    "审校/最终",
    "调研",
    "发布",
)


def clean(value: str) -> str:
    return textwrap.dedent(value).strip() + chr(10)


def markdown_templates(title: str, genre: str, target_words: str) -> dict[str, str]:
    return {
        "项目/项目简报.md": f"""
            # 项目简报

            - 暂定书名：{title}
            - 题材：{genre}
            - 目标总字数：{target_words}
            - 目标平台 / 读者：
            - 叙事视角与时态：
            - 核心体验：
            - 必须保留：
            - 必须避免：

            ## 一句话故事

            ## 核心问题与终局方向

            ## 已确认决策

            ## 候选与待确认事项
        """,
        "项目/读者画像.md": """
            # 读者画像与承诺

            ## 目标读者

            ## 读者承诺

            ## 期待的情绪与爽点

            ## 不应承诺的内容
        """,
        "项目/题材定位.md": """
            # 题材定位

            ## 用户输入分析

            ## 目标情绪、题材与题材包

            ## 目标平台与已核验约束

            ## 目标读者与对标作品分析

            ## 核心梗三分法

            - 核心梗：
            - 核心冲突：
            - 爽点引擎：

            ## 微创新点

            ## 书名候选（3–5 个）

            ## 简介文案

            ## 确认状态
        """,
        "项目/阶段零框架.md": """
            # 阶段 0 候选框架

            ## 角色关系图谱框架

            ## 伏笔系统架构

            ## 情绪弧线总图

            ## 力量体系框架

            ## 世界观框架

            ## 悬念系统架构

            > 所有内容先标注候选 / 已确认 / TBD；冻结 Canon 前须经专项设计与 Canon 管理。
        """,
        "项目/全局框架检查清单.md": """
            # 全局框架一致性检查清单

            | 检查项 | 状态（通过 / 候选 / TBD / 不适用） | 证据或冲突 | 责任步骤 |
            |---|---|---|---|
            | 读者承诺与题材一致 | TBD | | 16–30 |
            | 世界规则与力量成本一致 | TBD | | 31–37 |
            | 势力、角色与谜案动机一致 | TBD | | 38–67 |
            | 情绪/爽点与主线承诺一致 | TBD | | 68–87 |
            | 伏笔窗口与卷纲一致 | TBD | | 79–108 |
            | 章节覆盖与状态可追踪 | TBD | | 109–118 |
        """,
        "项目/决策批准记录.md": """
            # 决策与批准记录

            | 日期 | 决策 | 状态 | 批准者 | 影响范围 | 备注 |
            |---|---|---|---|---|---|
        """,
        "项目/风格卡.md": """
            # 风格卡

            - 叙事视角：
            - 时态与距离：
            - 节奏：
            - 句法/用词倾向：
            - 对话特征：
            - 意象与感官：
            - 避免事项：
            - 样例只用于抽象特征，不用于直接模仿：
        """,
        "项目/禁用词.txt": """
            # 仅填写作者或平台明确要求避免的词/短语；# 开头为注释。
            # 格式：词或短语 [TAB] 严重级别（可选）
        """,
        "项目/风格模式.txt": """
            # 可选：填写需要审计的重复句首、套话或表达模式；# 开头为注释。
            # 每行一个纯文本模式，脚本只报告命中，不自动改写。
        """,
        "正典/核心设定总表.md": """
            # 核心设定总表

            | ID | 类别 | 已确认事实 / 候选 | 来源步骤 | 影响范围 | 状态 |
            |---|---|---|---|---|---|
        """,
        "正典/全局上下文.md": """
            # 全局上下文追踪

            ## 当前创作位置

            ## 下一章必须承接

            ## 活跃人物、地点、资源与知识边界

            ## 活跃伏笔与回收责任

            ## 硬约束与待确认项
        """,
        "正典/世界观.md": """
            # 世界观 Canon

            ## 已确认事实

            ## 候选 / 待确认

            ## 不可违背的因果与代价

            ## 公开、受限与作者秘密
        """,
        "正典/力量体系.md": """
            # 力量体系 Canon

            ## 已确认等级、能力与资源

            ## 限制、代价、反制与信息边界

            ## 候选 / 待确认
        """,
        "正典/谜案悬念.md": """
            # 谜案与悬念 Canon

            ## 已确认谜案

            ## 线索、误导与揭示窗口

            ## 作者秘密与角色知识边界

            ## 候选 / 待确认
        """,
        "正典/关系网络.md": """
            # 关系网络 Canon

            | 关系 ID | 双方 | 公开关系 | 实际冲突/依赖 | 知识差 | 变化条件 | 状态 |
            |---|---|---|---|---|---|---|
        """,
        "正典/人物/主角.md": """
            # 主角设定（候选）

            ## 基本信息

            ## 性格特点

            ## 核心机制 / 金手指与限制

            ## 核心动机与背景故事

            ## 成长弧线与价值选择

            ## 知识边界、关系与状态
        """,
        "正典/读者体验.md": """
            # 读者体验 Canon

            ## 核心体验句

            ## 情绪承诺与节奏

            ## 爽点—代价闭环

            ## 差异化与禁区

            ## 首卷验证问题
        """,
        "正典/故事状态.md": """
            # 当前故事状态

            ## 当前快照

            - 人物：
            - 地点与时间：
            - 资源 / 伤势 / 能力：
            - 关系：
            - 已知信息：
            - 未决冲突：

            ## 章节状态变更

            | 章节 | 变更 | 原因 | Canon ID |
            |---|---|---|---|
        """,
        "正典/时间线.md": """
            # 时间线

            | 章节 | 时间 | 地点 | 事件 | 参与者 | 信息/状态影响 |
            |---|---|---|---|---|---|
        """,
        "正典/伏笔台账.md": """
            # 伏笔台账

            | ID | 首次出现 | 当前状态 | 推进记录 | 计划回收窗口 | 责任章节 | 备注 |
            |---|---|---|---|---|---|---|
        """,
        "规划/全书总纲.md": """
            # 全书总纲

            ## 终局问题与全书承诺

            ## 卷级结构

            | 卷 | 章节范围 | 读者承诺 | 入卷状态 | 主线推进 | 卷末兑现 | 出卷新债 |
            |---|---|---|---|---|---|---|
        """,
        "规划/长线系统.md": """
            # 全书长线系统

            ## 情绪弧线

            ## 爽点与代价

            ## 角色弧线

            ## 伏笔与反转

            | ID | 类型 | 起点 | 推进节点 | 兑现窗口 | 代价/风险 | 责任章节 | 状态 |
            |---|---|---|---|---|---|---|---|
        """,
        "规划/章节索引.md": """
            # 章节索引

            | 章 | 卷 | 标题 | 章节功能 | 细纲状态 | 正文状态 | Canon 版本 | 备注 |
            |---:|---:|---|---|---|---|---|---|
        """,
}


def volume_template(volume: int) -> str:
    return f"""
        # 第 {volume} 卷卷纲

        - 步骤映射：
        - 状态：候选

        ## 入卷状态与读者承诺

        ## 详细因果规划

        ## 情绪弧线

        ## 爽点节奏与代价

        ## 角色、谜案与伏笔责任

        ## 卷末兑现与出卷新债

        ## TBD、变更记录与质量门禁
    """


def registry_template() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "canon_version": "0.1.0",
            "entities": [],
            "facts": [],
            "foreshadows": [],
            "changes": [],
        },
        ensure_ascii=False,
        indent=2,
    ) + chr(10)


def workflow_config_template(planned_chapters: int, planned_volumes: int) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "planning": {
                "planned_chapters": planned_chapters,
                "planned_volumes": planned_volumes,
                "supporting_cast_target": 7,
                "faction_targets": {"order": 3, "neutral": 2, "antagonistic": 2},
                "foreshadow_targets": {
                    "long": {"min": 30, "max": 50, "when_chapters_at_least": 300},
                    "medium": {"min": 12, "max": 30},
                    "short": {"min": 8, "max": 25},
                },
            },
            "automation": {
                "default_mode": "guarded",
                "max_contiguous_batch": 100,
                "require_locked_outline": True,
                "require_canon_match": True,
                "require_review_gate": True,
                "halt_on": [
                    "s1_open",
                    "unapproved_canon_delta",
                    "major_creative_decision",
                    "context_gap",
                    "canon_version_mismatch",
                ],
            },
        },
        ensure_ascii=False,
        indent=2,
    ) + chr(10)


def production_state_template() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "active_batch": None,
            "chapters": {},
            "history": [],
        },
        ensure_ascii=False,
        indent=2,
    ) + chr(10)


def create_directory(path: Path, dry_run: bool) -> str:
    if path.exists():
        return "skipped"
    if dry_run:
        return "planned"
    path.mkdir(parents=True, exist_ok=True)
    return "created"


def create_file(path: Path, content: str, dry_run: bool) -> str:
    if path.exists():
        return "skipped"
    if dry_run:
        return "planned"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    return "created"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a v2 story-workflow project without replacing existing files."
    )
    parser.add_argument("--project-dir", required=True, help="Directory for the novel project.")
    parser.add_argument("--title", default="未命名项目", help="Temporary project title.")
    parser.add_argument("--genre", default="通用", help="Project genre.")
    parser.add_argument("--target-words", default="待定", help="Target total word count.")
    parser.add_argument("--planned-chapters", type=int, default=0, help="Known planned chapter count; 0 means TBD.")
    parser.add_argument("--planned-volumes", type=int, default=5, help="Initial volume template count; default: 5.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned files without writing.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser()
    if project_dir.exists() and not project_dir.is_dir():
        parser.error("--project-dir must be a directory path")
    if args.planned_chapters < 0:
        parser.error("--planned-chapters must be non-negative")
    if args.planned_volumes <= 0:
        parser.error("--planned-volumes must be positive")

    actions: dict[str, str] = {}
    if not args.dry_run:
        project_dir.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        path = project_dir / directory
        actions[str(path)] = create_directory(path, args.dry_run)

    for relative, content in markdown_templates(args.title, args.genre, args.target_words).items():
        path = project_dir / relative
        actions[str(path)] = create_file(path, content, args.dry_run)
    registry_path = project_dir / "正典/正典索引.json"
    actions[str(registry_path)] = create_file(registry_path, registry_template(), args.dry_run)
    config_path = project_dir / "项目/工作流配置.json"
    actions[str(config_path)] = create_file(
        config_path, workflow_config_template(args.planned_chapters, args.planned_volumes), args.dry_run
    )
    state_path = project_dir / "项目/生产状态.json"
    actions[str(state_path)] = create_file(state_path, production_state_template(), args.dry_run)
    for volume in range(1, args.planned_volumes + 1):
        volume_path = project_dir / "规划/分卷" / f"第{chinese_number(volume)}卷.md"
        actions[str(volume_path)] = create_file(volume_path, volume_template(volume), args.dry_run)

    print(json.dumps({"project_dir": str(project_dir.resolve()), "dry_run": args.dry_run, "actions": actions}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
