# LLM Prompt 回归评估平台

[返回作品集](../README.md) · [完整项目经历](../PROJECT_EXPERIENCE.md)

## 已发布的工程能力

- 40 条分层摘要案例：普通新闻15、数字密集10、因果与限制条件10、边界输入5。
- 配置驱动的批量生成、结构化评分、双向成对比较及 Markdown 报告。
- 请求重试与退避、任务哈希和断点恢复。
- 重复运行按案例聚合后进行 sign test，避免伪重复。
- 人工盲评、分层一致率、Cohen’s kappa 和分歧案例分析工具。

## 关键设计

双向比较交换候选顺序；只有两次选择一致时才计为该版本胜出，否则记为平局。多轮重复采样先在同一案例内汇总，再对案例结果统计。

这些机制减少特定评估偏差，但不能自动证明裁判正确。现有人工标注文件没有有效完成的标注记录，因此这里只报告复核工具的实现。

## 证据入口

固定源码提交：[9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4](https://github.com/TsingZYY/llm-eval-lab/tree/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4)

| 能力 | 已上传源码 |
|---|---|
| 双向比较 | [src/judge.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/judge.py#L255) |
| API 重试退避 | [src/llm.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/llm.py#L193) |
| 哈希与恢复 | [src/run_eval.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/run_eval.py#L63) |
| 案例级统计 | [src/report.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/report.py#L104) |
| 人工标注与一致性 | [src/annotate.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/annotate.py) / [src/agreement.py](https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/agreement.py) |

## 版本与结果

- 历史开发对话及本地开发说明记载真实运行240次生成、240条评分、120条pairwise记录；按40个案例聚合后，v2相对v1为33胜、3负、4平。
- 当前本地报告为 mock，不能将其当作真实模型实验。
- 当前工作区还有未提交扩展：数据集 registry、持久缓存、G-Eval、HTML viewer、过期标注过滤等。原仓库链接对应较早版本；本次作品集上传没有同步这些源码。
- 本轮仅核对文件、Git与历史记录，未重跑评测，未确认真实原始运行包已恢复。

## 可以怎样讲价值

把 prompt 修改变成有固定输入、可比较结果和可追查异常的工程流程。核心成果是可用的评测与复核机制，而性能结论需要匹配完整运行记录。
