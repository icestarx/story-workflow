---
name: project-delivery
description: "Prepare the final controlled delivery of a long-form novel project by updating tracking records, generating a summary, showing the project manifest, and recording completion confirmation."
---

# 输出与展示（步骤 146–150）

在最终审计通过后交付项目。交付不是“文件存在”而是让下一次续写、修订或发布能够立刻恢复上下文。

## 覆盖步骤

146. 更新上下文；147. 更新伏笔；148. 更新时间线；149. 更新角色状态；150. 创建总结报告。

## 执行

调用 canon-management 核对并更新 正典/全局上下文.md、正典/伏笔台账.md、正典/时间线.md、正典/故事状态.md。运行：

    python scripts/generate_project_report.py --project-dir path/to/project --force

将项目摘要、Canon 版本、锁定章节、未决项、开放伏笔、审计结论和文件清单写入 发布/项目总结.md。展示生成的 manifest 与报告，再记录用户的项目完成确认或保留项。

不得为了“项目完成”关闭应当保留的开放结局或未收伏笔；必须标注保留理由。
