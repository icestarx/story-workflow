---
name: project-bootstrap
description: "Initialize a controlled Chinese web-novel project with parameters, core references, framework skeletons, tracking templates, and a global consistency gate. Use for 新建小说项目、项目初始化、建立设定表、追踪文件、框架检查, or preparing a project before topic confirmation."
---

# 项目初始化（步骤 1–15）

建立可持续创作的初始状态，不替用户决定题材、结局或重大设定。阅读 [步骤总表](../../references/step-map.md) 与 [核心参考资料包](../../references/core-reference-kit.md)。

## 执行步骤

1. 收集并计算总字数、题材、平台、更新目标、目标章数/卷数；用“承诺清晰度、冲突续航、兑现引擎、差异化、生产风险”评估潜力，不预测爆款。
2. 运行初始化工具；它仅创建缺失文件：

       python scripts/init_story_project.py --project-dir path/to/project --title 暂定书名 --genre 题材 --target-words 目标字数

3. 在同一快照下读取 10 份核心参考资料，记录哪些适用；旧的 story-long-write 请求路由到 chapter-drafting、chapter-editing、canon-management 与 serial-production。
4. 创建候选框架：角色关系、伏笔、情绪、力量、世界、悬念；再创建核心设定总表、追踪模板、大纲/卷纲模板和全局一致性清单。
5. 运行：

       python scripts/validate_global_framework.py --project-dir path/to/project

## 并行边界

可并行填写六个候选框架或阅读独立参考资料；不得并行提交同一 Canon 文件。由 canon-management 统一合并后才进入阶段 1。

## 门禁

- workflow-config.json 含篇幅、势力/角色默认数量、伏笔层级和自动化停机条件；
- 所有框架明确候选、已确认或 TBD；
- 一致性清单逐项有状态；
- 验证工具无结构性错误。
