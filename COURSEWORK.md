# 课程项目精选

[返回作品集](README.md) · [中文项目经历](EXPERIENCE.zh-CN.md) · [总时间线](TIMELINE.md)

整理日期：2026-09-30。依据本人课程目录、现存源码、Git记录和历史对话，选择7项能体现算法、AI、数据库与软件工程能力的项目。每项均有时间线、笔记、代码说明和最终反思。

## 推荐阅读顺序

1. **AI／机器学习岗位：** 多智能体强化学习，重点讲清NumPy实现、训练设计与泛化评估。
2. **后端／应用工程岗位：** TaskTracker与数据库查询，重点讲清个人贡献、输入校验、数据访问和查询规则。
3. **算法／编程能力：** 文本差异分析器与纸牌模拟器，说明状态、动态规划、回溯和复杂度。
4. **学习经历补充：** 搜索与规划、FlyNet；公开材料限于高层经历和复盘。

## 收录范围

| 项目 | 技术与能力 | 代码范围 |
|---|---|---|
| [COMP9414 多智能体强化学习](projects/comp9414-marl/README.md) | NumPy · IPPO/MAPPO · 训练与评估 | 核心源码与Notebook摘录；历史结果单列 |
| [COMP9414 搜索与规划](projects/comp9414-search-planning/README.md) | DFS/BFS/UCS/A* · STRIPS | 公开经历、笔记与反思；课程禁止公开解答，源码保留本地 |
| [COMP9820 TaskTracker](projects/comp9820-tasktracker/README.md) | Flask · SQLite · API · 团队协作 | 个人贡献经历与复盘；课程禁止公开仓库，源码保留本地 |
| [COMP9311 数据库查询](projects/comp9311-database/README.md) | SQL · PostgreSQL · PL/pgSQL | 本人SQL实现；不含课程数据库与检查脚本 |
| [COMP9021 文本差异分析器](projects/comp9021-text-diff/README.md) | Python · LCS · 动态规划 · 回溯 | 本人Python源码 |
| [COMP9021 纸牌模拟器](projects/comp9021-card-simulation/README.md) | Python · 状态建模 · 随机模拟 | 两套游戏的本人Python源码 |
| [COMP9024 FlyNet 图算法](projects/comp9024-flynet/README.md) | C · 图结构 · Dijkstra · 割点 | 公开经历、笔记与反思；课程禁止公开解答，源码保留本地 |

其中4项附本人源码或注明范围的摘录；另外3项的原题明确禁止公开代码／完整解答，只公开经历说明。所有课程项目均不包含原题PDF、官方答案、他人往届解答、学号、私人路径或账号凭据。

## 完整档案导航

| 项目 | 时间线 | 笔记 | 代码说明 | 反思 |
|---|---|---|---|---|
| [COMP9414 多智能体强化学习](projects/comp9414-marl/README.md) | [时间线](projects/comp9414-marl/TIMELINE.md) | [笔记](projects/comp9414-marl/NOTES.md) | [代码](projects/comp9414-marl/CODE.md) | [反思](projects/comp9414-marl/REFLECTION.md) |
| [COMP9414 搜索与规划](projects/comp9414-search-planning/README.md) | [时间线](projects/comp9414-search-planning/TIMELINE.md) | [笔记](projects/comp9414-search-planning/NOTES.md) | [代码](projects/comp9414-search-planning/CODE.md) | [反思](projects/comp9414-search-planning/REFLECTION.md) |
| [COMP9820 TaskTracker](projects/comp9820-tasktracker/README.md) | [时间线](projects/comp9820-tasktracker/TIMELINE.md) | [笔记](projects/comp9820-tasktracker/NOTES.md) | [代码](projects/comp9820-tasktracker/CODE.md) | [反思](projects/comp9820-tasktracker/REFLECTION.md) |
| [COMP9311 数据库查询](projects/comp9311-database/README.md) | [时间线](projects/comp9311-database/TIMELINE.md) | [笔记](projects/comp9311-database/NOTES.md) | [代码](projects/comp9311-database/CODE.md) | [反思](projects/comp9311-database/REFLECTION.md) |
| [COMP9021 文本差异分析器](projects/comp9021-text-diff/README.md) | [时间线](projects/comp9021-text-diff/TIMELINE.md) | [笔记](projects/comp9021-text-diff/NOTES.md) | [代码](projects/comp9021-text-diff/CODE.md) | [反思](projects/comp9021-text-diff/REFLECTION.md) |
| [COMP9021 纸牌模拟器](projects/comp9021-card-simulation/README.md) | [时间线](projects/comp9021-card-simulation/TIMELINE.md) | [笔记](projects/comp9021-card-simulation/NOTES.md) | [代码](projects/comp9021-card-simulation/CODE.md) | [反思](projects/comp9021-card-simulation/REFLECTION.md) |
| [COMP9024 FlyNet 图算法](projects/comp9024-flynet/README.md) | [时间线](projects/comp9024-flynet/TIMELINE.md) | [笔记](projects/comp9024-flynet/NOTES.md) | [代码](projects/comp9024-flynet/CODE.md) | [反思](projects/comp9024-flynet/REFLECTION.md) |

## 如何理解这些材料

- **日期：** 提交日期、文件保存日期与对话日期分别标注；文件时间不冒充项目起始时间，回顾性笔记不冒充当年的逐日记录。
- **结果：** 强化学习数值来自原有保存输出；本轮没有训练、运行作业或执行测试，也没有补造课程分数。
- **代码：** 部分项目可直接阅读本人源码；TaskTracker提供个人贡献与提交记录说明，源码保留本地，数据库项目仍需相应关系模式，强化学习摘录没有训练权重。
- **归属：** 课程任务背景与本人实现分开说明；TaskTracker有多位贡献者，不把完整团队成果归为个人独立开发。现有记录含AI辅助工作。
- **公开范围：** COMP9414搜索作业题面第10页、COMP9024对应作业页面，以及TaskTracker的Sprint 3指南第7页明确限制公开代码。其他选中文件所核查材料未发现同类明确条款，这不代表课程材料获准转载，因此仅选本人实现并排除大学提供的素材。

## 本轮未收录

课堂讲义、题面、考试材料、下载的往届他人代码、零散入门练习和只有题目而没有可核实实现的材料，没有作为个人项目上传。已有COMP9020入门字符串练习和COMP9331网络实验文档暂不单列项目，优先展示上述完整实现与技术复盘。
