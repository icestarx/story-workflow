---
name: canon-management
description: "Govern a long-form novel's Canon: validate facts, manage proposals and approvals, track state/timeline/foreshadows, and assess retcon impact."
---

# Canon 管理与连续性治理

Canon 是后续故事能够被审计的事实源。本 Skill 是唯一可在获得批准后提交 Canon 的子 Skill。

## 读取与校验

读取 正典/正典索引.json 及相关 Markdown，运行：

    python scripts/validate_canon.py --project-dir path/to/project

检查实体 ID、事实状态、伏笔窗口、变更记录和引用文件。对正文/细纲提出的新增内容，只形成 delta 候选：新事实、依据、影响、建议状态。

## 提交流程

1. 分类：新事实、状态变化、伏笔新设/推进/回收、修订、废弃；
2. 影响分析：角色知识、时间线、能力、关系、细纲、正文、发布章节；
3. 取得用户批准或核对已有明确授权；
4. 同步更新 核心设定总表.md、正典索引.json、全局上下文.md、故事状态.md、时间线.md、伏笔台账.md、章节索引.md 与相关 Markdown；
5. 记录版本、原因、影响 ID、批准者和待迁移项。

## 章节锁定

仅当正文已通过 S1、重要取舍有结论、状态和伏笔变更已提交，才把章节索引标为锁定。受 batch_controller 管理时，还要核对生产状态机、审校报告的机器可读结论与 Canon 版本。不要从正文自动抽取并冻结事实。

## 受控自动提交

在用户明确授权某个章节范围的自动推进时，只有“锁定细纲已明确的常规状态变化”可由本 Skill 直接提交；新增世界规则、未铺垫的秘密、重大关系/结局变化和任何改设仍须停下请求确认。提交后把新 Canon 版本传给 batch_controller 的 canon-committed 标记。

## 改设（retcon）

先运行：

    python scripts/trace_canon_impact.py --project-dir path/to/project --id canon.id

它生成 `审校/影响-<id>.md`，列出显式受影响事实、已发布文本、未来细纲和审校文件。补充逻辑/主题/读者预期的隐含影响、替换办法、读者可见风险和回退方案。批准前不可覆盖旧事实；批准后保留历史版本与迁移状态，并运行 run_regression_suite.py。
