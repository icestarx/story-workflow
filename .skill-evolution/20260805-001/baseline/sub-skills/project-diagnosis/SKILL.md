---
name: project-diagnosis
description: "Diagnose, resume, repair, revise, audit, or publish a long-form novel project from any workflow node by inspecting project state, Canon, outlines, production checkpoints, and impact."
---

# 项目诊断与任意节点恢复

把项目当前文件和状态视为事实，而不是假设它一定从步骤 1 顺序完成。适用于“从第 N 章继续”“补设定”“重写一卷”“批次中断”“全书审计”“准备发布”等请求。

## 先诊断，不盲目写

运行：

    python scripts/diagnose_project.py --project-dir path/to/project --intent continue

可选 intent：create、continue、write、revise、repair、audit、publish。对目标章附加 `--chapter N`；改 Canon 前附加一个或多个 `--changed-id canon.id`。

诊断报告给出阻断项、Canon 版本、活动批次、文件覆盖、受影响文件、推荐子 Skill 和三步恢复方案。若它建议 repair-initialization，先补文件/迁移，不得直接起草正文。

## 改设与恢复

改设先运行：

    python scripts/trace_canon_impact.py --project-dir path/to/project --id canon.id

按“Canon → 细纲 → 正文 → 发布文本”顺序迁移，并在完成后运行 regression suite。任何活动批次中断后通过 serial-production 恢复；不得手工猜测下一章状态。

## 质量门

诊断是只读操作。它不冻结事实、不重写正文、不自动清除 blocker。推荐路线与用户意图冲突时，解释风险并由用户决定。
