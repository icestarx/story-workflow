# 质量检查子Skill

## 触发方式
- `/quality-check`
- 「检查第X章质量」
- 「质量检查」

## 功能
对单章进行质量检查，输出检查报告。

## 输入参数
```
chapter_number: 章节编号（如：1, 2, 3...）
project_path: 项目根目录路径
```

## 输出文件
```
{project_path}/追踪/质量检查/第{chapter_number}章_质量报告.md
```

## 执行步骤

### 步骤1：加载检查上下文
**操作**：读取以下文件获取检查上下文（可选快捷路径：如果项目已部署consistency-checker agent，可spawn Agent一次获取上下文）
**输出**：完整的检查上下文
**关键文件**：
- `{project_path}/正文/第{chapter_number:03d}章_{chapter_title}.md` - 本章正文
- `{project_path}/大纲/细纲/第{chapter_number:03d}章_细纲.md` - 本章细纲
- `{project_path}/设定/核心设定表.md` - 核心设定
- `{project_path}/追踪/伏笔.md` - 伏笔系统
- `{project_path}/追踪/角色状态.md` - 角色状态
- `{project_path}/设定/角色/{相关角色}.md` - 本章涉及角色
- `{project_path}/设定/关系.md` - 角色关系
**Agent调用**：
```
# 如果项目已部署consistency-checker agent
Agent(subagent_type: "consistency-checker", prompt: "项目目录：{project_path}\n检查范围：第{chapter_number}章\n检查类型：事实冲突+伏笔断线+角色属性不一致")
```

### 步骤2：情绪交付检查
**操作**：检查本章情绪是否符合细纲设计
**输出**：情绪交付检查结果
**检查项**：
- 目标情绪是否达成？
- 情绪强度是否符合预期？
- 情绪曲线是否合理？
- 情绪节点是否有效？
- 情绪过渡是否自然？
**评分**：1-10分
**Agent调用**：
```
# 如果项目已部署narrative-writer agent
Agent(subagent_type: "narrative-writer", prompt: "项目目录：{project_path}\n任务描述：审查+去AI味\n检查范围：第{chapter_number}章")
```

### 步骤3：技术质量检查
**操作**：检查本章技术质量
**输出**：技术质量检查结果
**检查项**：
- 事实一致性（时间、地点、人物关系）
- 伏笔回收是否完整
- 角色行为是否符合设定
- 世界观是否一致
- 力量体系是否一致
- 势力关系是否一致
**评分**：1-10分
**S1-S4分级**：
- S1：严重事实冲突（必须修改）
- S2：中度不一致（建议修改）
- S3：轻微问题（可选修改）
- S4：风格偏好（不强制修改）

### 步骤4：禁用词扫描
**操作**：扫描本章是否包含禁用词
**输出**：禁用词扫描结果
**检查项**：
- AI写作痕迹词汇（一级词：高频AI腔，命中即替换）
- 不符合时代背景的词汇
- 不符合角色身份的词汇
- 低频/语境相关词汇（二级词：高频出现时替换，偶发可参考anti-ai-writing.md定性裁定）
**评分**：1-10分（10分=无禁用词）
**关键文件**：
- `{project_path}/参考资料/banned-words.md` - 禁用词列表
- `{project_path}/参考资料/anti-ai-writing.md` - 去AI味参考

### 步骤5：去AI味检查
**操作**：检查本章是否有AI写作痕迹
**输出**：去AI味检查结果
**检查项**：
- 句式是否单调？
- 用词是否重复？
- 描写是否模板化？
- 是否有人味？
- 是否有自然的口语化表达？
- 是否有个性化的语言风格？
**评分**：1-10分
**Agent调用**：
```
# 如果项目已部署narrative-writer agent
Agent(subagent_type: "narrative-writer", prompt: "项目目录：{project_path}\n任务描述：审查+去AI味\n检查范围：第{chapter_number}章")
```

### 步骤6：爽点检查
检查本章爽点是否有效：
- 爽点是否突出？
- 爽点是否符合读者期待？
- 爽点是否推动剧情？

**评分**：1-10分

### 步骤7：钩子检查
检查本章钩子是否有效：
- 章首钩子是否抓住读者？
- 章尾钩子是否引导继续阅读？

**评分**：1-10分

### 步骤8：字数检查
检查本章字数是否达标：
- 实际字数 vs 目标字数
- 各部分字数分配是否合理

**评分**：1-10分

### 步骤9：计算综合评分
计算本章综合评分：
```
综合评分 = (情绪交付×0.2 + 技术质量×0.2 + 禁用词×0.15 + 去AI味×0.15 + 爽点×0.15 + 钩子×0.1 + 字数×0.05)
```

### 步骤10：创建质量报告
**操作**：创建质量报告，包含S1-S4分级和详细检查结果
**输出**：`{project_path}/追踪/质量检查/第{chapter_number:03d}章_质量报告.md`
**关键内容**：
- S1-S4分级报告
- 详细检查结果
- 问题汇总
- 改进建议
- 是否需要修改

## 质量报告模板

```markdown
# 第{chapter_number}章 质量检查报告

## 基本信息
- **章节编号**：第{chapter_number}章
- **章节标题**：{chapter_title}
- **检查时间**：{check_time}
- **综合评分**：{overall_score}/10

## 检查结果

### 1. 情绪交付
- **评分**：{emotion_score}/10
- **目标情绪**：{target_emotion}
- **实际情绪**：{actual_emotion}
- **情绪强度**：{emotion_intensity}/10
- **情绪节点**：{emotion_nodes}
- **情绪过渡**：{emotion_transition}
- **问题描述**：{emotion_issue}

### 2. 技术质量
- **评分**：{technical_score}/10
- **事实一致性**：{fact_consistency}
- **伏笔回收**：{foreshadow_resolution}
- **角色一致性**：{character_consistency}
- **世界观一致性**：{world_consistency}
- **力量体系一致性**：{power_system_consistency}
- **势力关系一致性**：{faction_consistency}
- **问题描述**：{technical_issue}

### 3. 禁用词扫描
- **评分**：{banned_words_score}/10
- **禁用词数量**：{banned_words_count}
- **禁用词列表**：{banned_words_list}
- **一级词（高频AI腔）**：{primary_banned_words}
- **二级词（低频/语境相关）**：{secondary_banned_words}
- **问题描述**：{banned_words_issue}

### 4. 去AI味
- **评分**：{ai_taste_score}/10
- **句式单调性**：{sentence_monotony}
- **用词重复性**：{word_repetition}
- **描写模板化**：{description_template}
- **人味程度**：{human_taste}
- **口语化表达**：{colloquial_expression}
- **个性化语言风格**：{personalized_style}
- **问题描述**：{ai_taste_issue}

### 5. 爽点
- **评分**：{cool_point_score}/10
- **爽点类型**：{cool_point_type}
- **爽点位置**：{cool_point_position}
- **爽点效果**：{cool_point_effect}
- **问题描述**：{cool_point_issue}

### 6. 钩子
- **评分**：{hook_score}/10
- **章首钩子**：{opening_hook}
- **章尾钩子**：{ending_hook}
- **钩子效果**：{hook_effect}
- **问题描述**：{hook_issue}

### 7. 字数
- **评分**：{word_count_score}/10
- **目标字数**：{target_word_count}字
- **实际字数**：{actual_word_count}字
- **字数差异**：{word_count_diff}字
- **字数达标**：{word_count达标}
- **问题描述**：{word_count_issue}

## S1-S4分级报告
| 级别 | 问题类型 | 数量 | 严重程度 | 处理建议 |
|------|----------|------|----------|----------|
| S1 | 严重事实冲突 | {s1_count} | 必须修改 | {s1_suggestion} |
| S2 | 中度不一致 | {s2_count} | 建议修改 | {s2_suggestion} |
| S3 | 轻微问题 | {s3_count} | 可选修改 | {s3_suggestion} |
| S4 | 风格偏好 | {s4_count} | 不强制修改 | {s4_suggestion} |

## 综合评分
| 检查项 | 权重 | 得分 | 加权得分 |
|--------|------|------|----------|
| 情绪交付 | 20% | {emotion_score} | {emotion_weighted} |
| 技术质量 | 20% | {technical_score} | {technical_weighted} |
| 禁用词 | 15% | {banned_words_score} | {banned_words_weighted} |
| 去AI味 | 15% | {ai_taste_score} | {ai_taste_weighted} |
| 爽点 | 15% | {cool_point_score} | {cool_point_weighted} |
| 钩子 | 10% | {hook_score} | {hook_weighted} |
| 字数 | 5% | {word_count_score} | {word_count_weighted} |
| **总计** | 100% | - | **{overall_score}** |

## 问题汇总
1. {issue_1}
2. {issue_2}
3. {issue_3}

## 改进建议
1. {improvement_1}
2. {improvement_2}
3. {improvement_3}

## 是否需要修改
- **需要修改**：{need_revision}
- **修改优先级**：{revision_priority}
- **修改建议**：{revision_suggestion}
```

## 调用方式

主workflow调用此子skill时：
```
调用story-long-write技能，使用quality-check子skill
参数：chapter_number={N}, project_path={path}
```

## 并行支持
- 多章质量检查可以并行执行
- 每章独立检查，互不影响
- 建议并行批次：10-20章/批

## 全局一致性检查
- 检查本章是否符合全局框架
- 检查伏笔操作是否与伏笔系统一致
- 检查情绪设计是否与情绪弧线总图一致
- 检查角色状态是否与角色关系图谱一致
