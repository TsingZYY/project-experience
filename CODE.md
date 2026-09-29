# 代码入口与交付范围

[返回作品集](README.md)

六个研究与比赛项目均提供真实代码入口。已公开的原仓库使用固定提交链接；原来仅保留在本地的三个实现，整理为本作品集中的源码快照。

| 项目 | 代码位置 | 说明 |
|---|---|---|
| LLM评测 | [代码与运行说明](projects/llm-evaluation/CODE.md) | 原仓库已发布版本；未提交扩展另列 |
| Atlassian | [代码与运行说明](projects/atlassian-analytics/CODE.md) | 原仓库分析脚本、规则模型与复现入口 |
| Algothon | [代码与运行说明](projects/algothon/CODE.md) | 本作品集保存最终候选策略快照 |
| Kaggriculture | [代码与运行说明](projects/kaggriculture/CODE.md) | 本作品集保存单文件Agent |
| Titanic | [代码与运行说明](projects/titanic/CODE.md) | 本作品集保存源码、依赖和清理输出的Notebook |
| RLVR | [代码与状态说明](projects/rlvr-audit/CODE.md) | 原仓库的协议、验证与研究代码；正式实验未完成 |

## 课程代码与公开范围

| 项目 | 技术与能力 | 代码范围 |
|---|---|---|
| [COMP9414 多智能体强化学习](projects/comp9414-marl/README.md) | NumPy · IPPO/MAPPO · 训练与评估 | 核心源码与Notebook摘录；历史结果单列 |
| [COMP9414 搜索与规划](projects/comp9414-search-planning/README.md) | DFS/BFS/UCS/A* · STRIPS | 公开经历、笔记与反思；课程禁止公开解答，源码保留本地 |
| [COMP9820 TaskTracker](projects/comp9820-tasktracker/README.md) | Flask · SQLite · API · 团队协作 | 个人贡献经历与复盘；课程禁止公开仓库，源码保留本地 |
| [COMP9311 数据库查询](projects/comp9311-database/README.md) | SQL · PostgreSQL · PL/pgSQL | 本人SQL实现；不含课程数据库与检查脚本 |
| [COMP9021 文本差异分析器](projects/comp9021-text-diff/README.md) | Python · LCS · 动态规划 · 回溯 | 本人Python源码 |
| [COMP9021 纸牌模拟器](projects/comp9021-card-simulation/README.md) | Python · 状态建模 · 随机模拟 | 两套游戏的本人Python源码 |
| [COMP9024 FlyNet 图算法](projects/comp9024-flynet/README.md) | C · 图结构 · Dijkstra · 割点 | 公开经历、笔记与反思；课程禁止公开解答，源码保留本地 |

每项具体公开范围、依赖、源文件来源、整理改动和未运行状态见项目的`CODE.md`；带源码的课程项目另有`PROVENANCE.md`。公开目录不包含课程提供的数据库、原题或完整团队应用。

## 本次交付

- 保留算法逻辑；源文件来源、固定提交或哈希见每个项目的代码页。
- 新增快照不包含API凭据、原始聊天、模型权重、比赛价格数据和个人电脑路径。
- Titanic的Notebook输出及执行计数已清理；原有实验数字记录在项目说明，下载后需自行提供数据并运行。
- 本次整理没有运行模型、测试、回测或比赛对局。复制源码与检查上传一致性不等于重新验证运行结果。
- 未擅自为上游代码或比赛数据增加开源许可证；使用条件以原项目和相关来源为准。

