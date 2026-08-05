# 创作控制平面

控制平面让 Skill 从任意节点安全恢复，并将创作工作转化为可审计任务，而不替代创作本身。

## 四个组件

| 组件 | 命令 | 职责 |
|---|---|---|
| 项目诊断 | diagnose_project.py | 判断项目状态、缺口、推荐入口与恢复方案 |
| 批次编排 | orchestrate_batch.py | 把下一状态转成具体子 Skill、输入、输出与验收任务卡 |
| 影响追踪 | trace_canon_impact.py | 在改设前列出显式受影响的 Canon、细纲、正文与审校文件 |
| 回归检查 | run_regression_suite.py | 复验框架、Canon、细纲覆盖、生产状态和正文覆盖 |

## 正常入口

- 新项目：diagnose(create) → project-bootstrap。
- 续写：diagnose(continue) → serial-production / 编排器。
- 单章：diagnose(write, chapter) → 细纲/生产/编辑。
- 改设：diagnose(revise, changed-id) → 影响追踪 → Canon 提交 → 重基。
- 修复：diagnose(repair) → regression → 最小修复。
- 完结：diagnose(audit/publish) → 最终审计 → project-delivery。

## 不变量

1. 诊断只读；编排只给任务卡；状态转换仍由 batch_controller 守护。
2. 连续章节不并发起草；批次中的下一章只在上一章 locked 后开始。
3. 新 Canon delta、重大创作决定和 S1 会中断自动链路。
4. 改设先影响追踪，再修改；每次修复后重新诊断/回归。
