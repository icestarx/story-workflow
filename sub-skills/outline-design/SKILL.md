# 细纲设计子Skill

## 触发方式
- `/outline-design`
- 「设计第X章细纲」
- 「创建章节细纲」

## 功能
为单章设计完整细纲，输出统一格式的文件。

## 输入参数
```
chapter_number: 章节编号（如：1, 2, 3...）
chapter_title: 章节标题（可选，不提供则自动生成）
volume_number: 所属卷号（如：1, 2, 3...）
project_path: 项目根目录路径
```

## 输出文件
```
{project_path}/大纲/细纲/第{chapter_number}章_细纲.md
```

## 执行步骤

### 步骤1：加载全局框架
读取以下文件获取全局上下文：
- `{project_path}/设定/核心设定表.md` - 核心设定
- `{project_path}/大纲/大纲.md` - 全书大纲
- `{project_path}/大纲/卷纲_第{volume_number}卷.md` - 当前卷纲
- `{project_path}/追踪/伏笔.md` - 伏笔系统
- `{project_path}/追踪/角色状态.md` - 角色状态

### 步骤2：确定章节位置
- 计算本章在全书中的位置（前中后）
- 确定本章在当前卷中的位置
- 识别本章需要推进的主线/支线

### 步骤3：设计核心事件
- 本章核心事件是什么？
- 事件如何推进剧情？
- 事件如何影响角色？

### 步骤4：设计目标情绪
- 本章目标情绪是什么？
- 情绪强度（1-10）？
- 情绪如何变化？

### 步骤5：设计章首钩子
- 开篇如何抓住读者？
- 设置什么悬念？
- 如何引导读者继续阅读？

### 步骤6：设计爽点
- 本章爽点是什么？
- 爽点位置（章首/章中/章尾）？
- 爽点如何设计？

### 步骤7：设计章尾钩子
- 结尾如何设置悬念？
- 如何引导读者看下一章？
- 留下什么疑问？

### 步骤8：设计字数目标
- 本章目标字数（基于总字数和章数计算）
- 各部分字数分配

### 步骤9：设计伏笔操作
- 本章需要埋下什么伏笔？
- 本章需要回收什么伏笔？
- 本章需要推进什么伏笔？

### 步骤10：设计角色出场
- 本章出场角色列表
- 每个角色的状态变化
- 角色关系变化

### 步骤11：创建细纲文件
创建 `{project_path}/大纲/细纲/第{chapter_number}章_细纲.md`

## 细纲文件模板

```markdown
# 第{chapter_number}章 {chapter_title}

## 基本信息
- **章节编号**：第{chapter_number}章
- **所属卷号**：第{volume_number}卷
- **目标字数**：{word_count}字
- **目标情绪**：{target_emotion}
- **情绪强度**：{emotion_intensity}/10

## 核心事件
{core_event_description}

## 情绪曲线
- **开篇情绪**：{opening_emotion}
- **高潮情绪**：{climax_emotion}
- **结尾情绪**：{ending_emotion}

## 章首钩子
{opening_hook}

## 爽点设计
- **爽点类型**：{cool_point_type}
- **爽点位置**：{cool_point_position}
- **爽点描述**：{cool_point_description}

## 章尾钩子
{ending_hook}

## 伏笔操作
### 需要埋下的伏笔
- {foreshadow_to_plant}

### 需要回收的伏笔
- {foreshadow_to_resolve}

### 需要推进的伏笔
- {foreshadow_to_advance}

## 角色出场
| 角色 | 出场方式 | 状态变化 | 关系变化 |
|------|----------|----------|----------|
| {character_name} | {appearance_method} | {status_change} | {relationship_change} |

## 场景设定
- **主要场景**：{main_scene}
- **时间**：{time_setting}
- **环境描述**：{environment_description}

## 剧情大纲
1. {plot_point_1}
2. {plot_point_2}
3. {plot_point_3}
...

## 写作要点
- {writing_tip_1}
- {writing_tip_2}
- {writing_tip_3}

## 需要避免
- {avoid_1}
- {avoid_2}
```

## 调用方式

主workflow调用此子skill时：
```
调用story-long-write技能，使用outline-design子skill
参数：chapter_number={N}, volume_number={V}, project_path={path}
```

## 并行支持
- 多章细纲设计可以并行执行
- 每章独立读取全局框架，互不影响
- 建议并行批次：5-10章/批

## 全局一致性检查
- 每章细纲完成后，检查是否符合全局框架
- 检查伏笔操作是否与伏笔系统一致
- 检查情绪设计是否与情绪弧线总图一致
- 检查角色状态是否与角色关系图谱一致
