# Atlassian 客服数据分析与证据复核原型

[返回作品集](../README.md)

**记录区间：** 2026年9月  
**技术：** Python、pandas、NumPy、bootstrap、置换检验、Holm多重检验校正

## 问题与实现

项目探索如何从客户、产品使用和支持工单中找出可复核的跟进线索。数据来自比赛提供的三张合成CSV。

1. 关联8,320名客户、8,469张工单和42,210条使用记录。
2. 检查身份一致性、重复键、时间字段和五个月历史覆盖；识别139名跨表身份冲突客户、85条活跃天数异常记录。
3. 将产品月行聚合为客户级指标，避免把同一个客户多个月的记录当作独立客户。
4. 实现最小规则模型及来源证据卡，输出数据待核对、复核候选和常规支持三类结果。
5. 形成分析报告及10页英文展示材料。

## 代表性结果

| 结果 | 正确解释 |
|---|---|
| 客户级套餐—集成使用 η²约0.8793，95% bootstrap区间约87.56%—88.31% | 套餐类别解释集成使用量的样本方差比例，不是分类准确率 |
| 1,666名留出客户上R²约87.26% | 对相同数据来源的留出检查，不是真实升级干预 |
| 独立审核文件记录459项检查通过 | 点估计、来源和固定断言得到复核；并非全部随机推断独立重生成 |
| 12项工单／集成比较经Holm校正后0项获得清晰支持 | 本轮证据未支持相应假设，不能反向断言所有业务关系都不存在 |
| 最小模型输出347张工单待核对、43张复核候选、8,079张常规支持 | 实现按规则运行，不等于预测准确率或客服效果 |

负对照也改变了研究判断：4月下降规则对5月低使用的命中倍数为2.70，但打乱月份后约2.69，未支持将该规则解释为动态恶化预测。

## 已有产物与复现入口

[原仓库](https://github.com/TsingZYY/atlassian-support-review-experiments) · [固定快照 c6ece712](https://github.com/TsingZYY/atlassian-support-review-experiments/tree/c6ece712402e7cba83cd2529cc7073deba8fb0d7)

- [integration_plan_v1](https://github.com/TsingZYY/atlassian-support-review-experiments/tree/c6ece712402e7cba83cd2529cc7073deba8fb0d7/integration_plan_v1)：客户级关联及独立审核。
- [ticket_bridge_v1](https://github.com/TsingZYY/atlassian-support-review-experiments/tree/c6ece712402e7cba83cd2529cc7073deba8fb0d7/ticket_bridge_v1)：工单比较与多重检验。
- [minimal_model](https://github.com/TsingZYY/atlassian-support-review-experiments/tree/c6ece712402e7cba83cd2529cc7073deba8fb0d7/minimal_model)：可追溯规则实现。
- 原项目的 `reproduce.py` 提供复现入口；本轮未执行。

## 成果边界

比赛合成数据不能证明真实客户行为。项目尚无真实试点、已验证付费转化、流失降低或利润增量。部分情景模拟明确使用假设参数，不纳入实证效果。

英文演示文稿有结构验证记录，但仍有文字密度提示，未确认原生PowerPoint渲染。作品集本次仅整理经历，不重新上传数据和演示文件。
