---
name: manuscript-quality-audit
description: "Run final whole-manuscript quality audits for emotional delivery, technical integrity, custom prohibited terms, mechanical-expression signals, tracking updates, and quality reports."
---

# 最终质量检查（步骤 136–145）

对锁定正文执行全书级审计。不要把“去 AI 味”当成不可验证的判断；报告必须展示重复结构、套话、同声对话或解释堆积的可定位证据。

## 覆盖步骤

136. 创建最终检查目录；137. 并行审读章节情绪交付；138. 并行检查技术质量；139. 扫描用户/平台配置的禁用项；140. 诊断机械化表达；141. 更新追踪文件；142. 创建全书质量报告；143. 创建全书总结报告；144. 展示文件清单；145. 等待项目完成确认。

## 执行

运行：

    python scripts/audit_manuscript.py --project-dir path/to/project --expected-chapters N
    python scripts/build_story_docs.py --project-dir path/to/project --force

由多个独立审读任务分别检查情绪兑现与叙事体验；自动脚本检查缺章、标题、用户词表命中、重复段落和高频句首。将结果合并至 05-reviews/final/quality-report.md。

禁用词表只使用 00-project/banned-terms.txt 中作者/平台明确要求；结果是命中清单而非自动删改。所有 S1、未解决 S2、例外批准和开放项必须进入总结报告。
