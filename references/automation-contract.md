# 受控自动化契约

自动化的目标是减少重复协调和遗漏，不是取消作者控制。它不能代替模型写作、编辑判断或用户对重大创作选择的授权。

## 状态机

    candidate-outline → outline-locked → drafted → review-passed → canon-committed → locked

batch_controller.py 保存每章状态、当前批次、停止原因和 Canon 版本。仅允许相邻状态转换；控制器不依据自然语言猜测是否通过。

## 自动推进循环

1. 查询 next；
2. 若动作为 rebase-outline，读取最新 Canon，重基并锁定本章细纲；
3. 若动作为 draft，编译上下文并调用 chapter-drafting；
4. 若动作为 review，调用 chapter-editing；
5. 若动作为 canon-commit，调用 canon-management；
6. 若动作为 lock，更新章节索引/控制器状态；
7. 重复，直到 batch-complete 或 halt。

每章完成后再开始下一章。重新进入循环时从控制器记录恢复，不能根据目录中文件数量推断状态。

## 授权档位

| 档位 | 可自动做 | 必须停止 |
|---|---|---|
| guarded（默认） | 规划、草稿、审校建议、常规状态候选 | 首章锁定、所有 Canon 提交、S1/S2 决策 |
| user-range | 用户明确指定范围内的例行状态提交 | 新世界事实、重大关系、结局、改设、作者决策 |
| manual | 仅生成下一步计划 | 一切写入 |

“自动写 1–10 章”是 user-range 授权，不是无限授权。授权范围、日期和停止条件必须写入 production-state.json。

## 强制停止条件

- 细纲不存在、不是锁定状态或 Canon 版本不匹配；
- 上一章没有 locked；
- 审校存在 S1、结论不是“可锁定”，或有未解决 S2；
- 正文引入未批准的新事实、改动世界规则/结局/重大关系；
- 上下文包出现未解析 Canon ID；
- 用户要求、资源异常或控制器状态异常。

停止后写明原因、影响章节和恢复前提。修复完成后，通过 next 恢复，而不是手工跳过状态。
