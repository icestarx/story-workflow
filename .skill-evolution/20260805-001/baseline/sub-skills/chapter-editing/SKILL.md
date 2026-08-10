---
name: chapter-editing
description: "Edit a Chinese web-novel chapter with evidence-based checks for Canon, causality, reader experience, pacing, and prose; produce actionable revisions."
---

# 章节编辑与审校

审校的目标是帮作者作出清晰取舍，不是用一个总分掩盖问题。只给可定位、可修改、能说明影响的意见。

涉及追读、章节功能、人物主动性、爽点代价和卷级兑现时，读取 [流行长篇编辑标准](../../references/editorial-standards.md)。按题材定位判断，不能机械要求每章都战斗、反转或高爽。

## 四层检查

1. Canon：人物、时间、地点、资源、知识、能力、伏笔是否一致；
2. 叙事：触发—行动—阻力—结果是否完整，动机和选择是否成立；
3. 读者体验：章首钩子、压力、情绪变化、爽点兑现、章尾承接是否有效；
4. 语言：视角漂移、重复、解释堆积、句式单调、对话同声与不必要的修辞。

## 输出

写入 05-reviews/chapter-NNNN-edit.md：

- 通过项和证据；
- S1 阻断问题：冲突事实、因果断裂、角色越知、无法兑现承诺；
- S2 重要问题：节奏、动机、体验、伏笔责任；
- S3 润色项：语言和局部表现；
- 最小修订建议、影响范围、修订后需要复查的项目；
- 明确的“可锁定 / 需修订 / 需要作者决定”结论。

报告末尾追加机器可读结论行：`- S1 未解决：0` 与 `- 锁定结论：可锁定`。只有两项同时成立，生产控制器才可把章节推进为 review-passed。

引用段落位置或事件，不凭“读起来不够爽”给笼统结论。不得自行改写 Canon；发现冲突转交 canon-management。
