# 项目文件与 Canon 契约

项目目录将面向读者的正文、可修改的候选方案、已确认事实和审校记录分离。Markdown 便于创作阅读；01-canon/registry.json 便于脚本检索和校验。二者存在冲突时，以最后批准的 Canon 变更记录为准，并立即修复另一侧。

## 目录结构

    project/
    ├── 00-project/                 # 立项与人工决策
    │   ├── brief.md
    │   ├── reader-profile.md
    │   ├── genre-positioning.md
    │   ├── frameworks.md
    │   ├── global-framework-checklist.md
    │   ├── workflow-config.json
    │   ├── production-state.json
    │   ├── banned-terms.txt
    │   ├── style-patterns.txt
    │   ├── approvals.md
    │   └── style-card.md
    ├── 01-canon/                   # 已确认事实的唯一来源
    │   ├── world.md
    │   ├── power-system.md
    │   ├── core-settings.md
    │   ├── context.md
    │   ├── factions/
    │   ├── mysteries.md
    │   ├── characters/
    │   ├── relationships.md
    │   ├── reader-experience.md
    │   ├── state.md
    │   ├── timeline.md
    │   ├── foreshadow-ledger.md
    │   └── registry.json
    ├── 02-planning/                # 全书、长线、分卷与索引
    │   ├── series-map.md
    │   ├── long-arcs.md
    │   ├── volumes/
    │   └── chapter-index.md
    ├── 03-outlines/                # 每章细纲，chapter-0001.md …
    ├── 04-manuscript/              # 正文，chapter-0001.md …
    ├── 05-reviews/                 # 编辑报告、周期复盘、影响分析
    │   └── final/                  # 全书最终质量审计
    ├── 06-research/                # 带来源和适用边界的研究
    └── 07-release/                 # 简介、标签、发布清单等可选材料

## 文件职责和提交权

| 位置 | 内容 | 正常写入者 |
|---|---|---|
| 00-project | 定位、读者、框架、配置、批准记录、风格约束 | project-bootstrap / story-positioning / 用户 |
| 01-canon | 已确认、会影响后续因果的事实 | canon-management |
| 02-planning | 全书、长线、分卷和章节覆盖 | 规划子 Skill，经 Canon 检查 |
| 03-outlines | 已锁定或候选的章节执行计划 | chapter-outline |
| 04-manuscript | 面向读者的章节正文 | chapter-drafting |
| 05-reviews | 可定位的审校、全局/周期复盘与最终审计 | chapter-editing / global-review / manuscript-quality-audit |
| 06-research | 外部资料及创作转化 | story-research |
| 07-release | 可发布包装与项目交付总结 | publication-packaging / project-delivery |

## 控制文件

- workflow-config.json：可调整的项目参数、势力/配角默认数量、伏笔层级目标和自动化停机条件。配置不是 Canon，不能借它重写世界规则。
- production-state.json：batch_controller.py 的持久化检查点。记录每章状态、活动批次、授权范围、停止原因和最近历史；只能通过控制器做阶段转换。
- core-settings.md：给作者读取的设定总表；registry.json 是机器索引。二者由 canon-management 同步。
- context.md：全局创作位置与活跃约束；具体章节上下文包仍由 compile_chapter_context.py 生成。
- banned-terms.txt / style-patterns.txt：只放作者或平台明确指定的规则。扫描结果是人工复核清单，不自动改写正文。

## Canon 记录规则

每一条 Canon 事实应尽量具备稳定 ID、状态、来源步骤、可见范围和变更记录。推荐 ID：world.*, power.*, faction.*, mystery.*, char.*, relation.*, state.*, foreshadow.*。

registry.json 是机器可读索引，最低格式如下：

    {
      "schema_version": 1,
      "canon_version": "0.1.0",
      "entities": [],
      "facts": [],
      "foreshadows": [],
      "changes": []
    }

- entities：id、type、name、source_file、status；
- facts：id、statement、status、source_steps、visibility、source_file；
- foreshadows：id、setup_chapter、status、target_window、responsible_chapter；
- changes：version、date、reason、affected_ids、approved_by。

“作者知晓”只表示叙事可用的隐藏真相；角色的知识边界仍要单独登记。候选、TBD、废弃信息不可被正文当作事实使用。

## 章节文件约定

章节编号统一使用四位：chapter-0001.md。细纲的字段、锁定状态和检查方式见 [章节细纲契约](chapter-contract.md)。每篇正文的文件头至少保留章节号、标题、关联细纲版本和状态（草稿 / 修订 / 锁定）。正文不应嵌入提示词、评分表和审校意见。

需要由 batch_controller 自动推进的细纲还必须在“章节信息”内写入：`状态：锁定` 和 `Canon 版本：<版本号>`。详细状态机见 [自动化契约](automation-contract.md)。

## Canon 变更流程

1. 提出变更：记录旧事实、新事实、原因和意图。
2. 影响分析：列出受影响角色、知识边界、时间线、伏笔、细纲、正文与发布章节。
3. 决策：用户或明确授权者批准、拒绝或保留为候选。
4. 提交：canon-management 更新 Markdown、registry.json、状态与变更日志。
5. 迁移：修订受影响的计划/正文，并把未处理项登记进 05-reviews。

不得从正文自动反向提交 Canon。自动工具只可以提出 delta 候选，不能直接冻结事实。
