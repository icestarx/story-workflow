---
name: chapter-outline
description: "Create, batch-plan, rebase, and lock chapter outlines for a serial novel while enforcing causal, emotional, hook, payoff, and Canon contracts."
---

# 全书细纲设计（步骤 109–118）

细纲是正文的执行契约。先覆盖全书，再在写作前按最新 Canon 重基并锁定目标章。

## 步骤 109–118

109. 创建 细纲 和章节索引；
110. 计算总章节、卷章范围、章节功能与批次；
111–113. 先制作第 1–30 章校准批次，检查首章承诺、节奏、人物声音和连续性；
114–117. 其余章节按最多 100 章的规划批次制作、审计、合并、修订、锁定；
118. 验证全书覆盖，登记缺口、TBD、锁定范围和未通过项。

## 单章操作

先读取对应卷纲、长线账本、前后章节索引和相关 Canon。依 [章节细纲契约](../../references/chapter-contract.md) 写入 `第…章.md` 的全部必填标题。随后运行：

    python scripts/validate_outline.py --outline path/to/第一章.md

每章必须让触发—行动—阻力—结果产生新状态；钩子和爽点均来自该因果链。章尾钩子要明确下一章的承接责任。

## 批量与并行

- 30 章校准批次必须先获得方向确认或记录为待确认；
- 同一 Canon 快照中，互不重叠的候选细纲可并行；合并、相邻承接和锁定必须串行；
- 单批最多 100 章，结束后检查章节功能重复、伏笔窗口、情绪密度和总字数；
- 写正文前，重基为最新 Canon；出现冲突时先修细纲。

## 完成标准

全书每章都有可验证的细纲字段，章节索引记录计划/候选/锁定状态，且 validate_outline 无必填字段缺失。详见 [并行规则](../../references/parallel-execution.md)。
