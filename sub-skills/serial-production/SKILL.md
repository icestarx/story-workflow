---
name: serial-production
description: "Run a resumable, controlled serial-novel production batch such as 自动写1到10章, with sequential drafting, checkpoints, review gates, Canon commits, and safe halts."
---

# 受控批次正文生产（步骤 126–135）

实现“自动推进 1–10 章”等批量创作，但连续剧情永远串行。脚本只管理状态和门禁；它不生成文学文本，也不会替作者批准新世界规则或重大改设。

## 批次结构

- 126：创建/验证正文目录和生产控制文件；
- 127–128：第 1 章示范起草与审校；
- 129–130：第 2–10 章逐章推进，随后做批次 Review；
- 131–132：第 11–50 章逐章推进，随后做批次 Review；
- 133–134：第 51–100 章逐章推进，随后做批次 Review；
- 135：后续按不超过 100 章的连续批次重复。

## 启动、恢复与自动推进

先从任意现有状态诊断，再创建/恢复控制状态并对范围预检：

    python scripts/diagnose_project.py --project-dir path/to/project --intent continue
    python scripts/batch_controller.py init --project-dir path/to/project
    python scripts/batch_controller.py start --project-dir path/to/project --from 1 --to 10 --authorization user-first-10
    python scripts/orchestrate_batch.py next --project-dir path/to/project

编排器返回“当前席位、所需输入、允许写入位置、验证命令、停止条件”的任务卡。按卡调用 chapter-outline（重基/锁定）、chapter-drafting、chapter-editing、canon-management，并用 mark 记录完成。中断后再次运行 orchestrate_batch.py next 即可从最后一个持久化检查点恢复。

## 每章状态机

candidate-outline → outline-locked → drafted → review-passed → canon-committed → locked。

不得跳步。每次 Canon 变更后，下一章必须重新获取上下文并重基细纲。批次结束时调用 serial-review；不要把“1–10”当作十章并行起草。

## 自动化授权与停机

用户明确发出“自动写第 1–10 章”可授权该范围内、已锁定细纲所表达的常规状态变化。以下任一情况必须 halt：S1、缺失细纲/上下文、Canon 版本不匹配、未批准的新事实、改写世界/结局/重大关系、需要风格或价值选择、审校结论不是“可锁定”。

使用 batch_controller.py status/halt 查看或记录原因。改设先运行 trace_canon_impact.py；批次修复后运行 run_regression_suite.py。详见 [自动化契约](../../references/automation-contract.md) 与 [控制平面](../../references/control-plane.md)。
