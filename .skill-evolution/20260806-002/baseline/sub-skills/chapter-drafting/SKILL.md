---
name: chapter-drafting
description: "Draft or rewrite one serial-novel chapter from a locked outline and compiled Canon context, preserving causality, voice, state, and reader momentum."
---

# 单章正文起草

只在目标章节已具备锁定细纲、入章状态和字数预算后使用。正文是读者文本，不混入提示词、评分或审校清单。

## 写前

运行或读取上下文包：

    python scripts/compile_chapter_context.py --project-dir path/to/project --chapter 1

至少核对：锁定细纲、上章结尾/摘要、当前人物状态、时间地点资源、角色知识边界、可用伏笔、硬规则与风格卡。缺少关键资料时停下补细纲或标记 TBD，不凭空补设定。

## 起草法

1. 让章首钩子在第一场景形成可感知的异常、压力、期限或选择；
2. 用行动、阻力、决定和结果推进 4–8 个节拍；
3. 把设定信息放进人物目标和代价中，不以说明段替代戏；
4. 兑现本章的情绪/爽点承诺，并留下相应代价、余波或新欲望；
5. 用本章事实导出章尾钩子，交接给下一章责任。

## 约束

- 不让人物知道未获知的信息，不让能力绕过已定限制；
- 不以巧合、降智或新增规则替代因果；
- 不直接模仿在世作者或用户提供作品的可识别文风；提炼可描述的节奏、视角、句长、意象和禁忌即可；
- 任何新设定写进候选 delta，不自动写入 Canon。

起草后将正文保存至 `正文/第…章.md`，状态标为草稿，交 chapter-editing 审校。
