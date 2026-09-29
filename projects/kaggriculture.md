# Kaggriculture：决策智能体与本地评估工程

[返回作品集](../README.md)

**记录区间：** 2026年8月24—25日  
**技术：** Python、kaggle-environments、规则调度、种子对照、打包验证

## 实现内容

围绕生产调度与市场需求建立观察驱动的策略，对特定游戏状态启用候选分支，其余情况回退到基线。评估工具覆盖6类本地对手、双座位、固定种子、约束检查与源码指纹。

交付物包括无需本地模块依赖的单文件agent、比赛提交包、manifest与QA记录。

## 已保存的本地结果

| 项目 | 记录 |
|---|---|
| 总对局 | 100个种子 × 6类对手 × 候选／控制2策略 × 2座位 = 2,400场 |
| 触发座位 | 53个；53/53相对匹配基线的margin增加 |
| 未触发座位 | 1,147个；全部与基线精确一致 |
| 打包一致性 | 10局共7,190个动作与参考实现一致 |
| 按文件路径加载 | 2个官方SDK加载案例通过 |

候选与控制策略在各对手的seed级记录中均为100/100获胜，因此不能把该记录解释为“胜率提高”。策略改动带来的margin增量集中在少数触发场景，中位数增量为零。

## 实验限制

引擎随机数调用受土地占用影响，同一个seed不保证后续需求路径完全固定，因而不是纯粹隔离需求的因果实验。分析器在发现座位触发差异后有留痕修订，策略与原评估数据未改变；不能称为完全无修改的预注册确认。

对手为本地控制策略，不能外推对排行榜高手的胜率。现有状态为 `built-and-tested-not-submitted`，没有已核实的官方提交或线上排名。此agent使用规则与调度决策，没有训练强化学习模型。

## 本地证据索引

以下原项目相对路径已读取；2026-09-30新增[完整项目档案](kaggriculture/README.md)与[单文件Agent源码](kaggriculture/CODE.md)，完整比赛包仍保留在原项目：

- `work/RESEARCH_LOG.md`
- `work/tournament_matrix.py`
- `work/adaptive_experiments.py`
- `outputs/adaptive_day9_three_shop_cross_family_blind_8000_100seeds_summary_v2.json`
- `artifacts/kaggriculture_day9_three_shop/qa_report.json`
- `artifacts/kaggriculture_day9_three_shop/manifest.json`
- `artifacts/kaggriculture_day9_three_shop/submission.py`

本次读取时submission源码哈希与QA报告一致；没有重新运行对局。

## 可以展示的工程能力

把策略改动限制在明确场景，保留未触发场景的基线行为；通过种子、座位、对手和打包一致性检查减少评估与交付偏差。
