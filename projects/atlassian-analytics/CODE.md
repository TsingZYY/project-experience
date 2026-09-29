# 代码与运行入口

[项目首页](README.md)

## 实际源码与固定版本

[公开原仓库](https://github.com/TsingZYY/atlassian-support-review-experiments)。本档案使用提交 **c6ece712402e7cba83cd2529cc7073deba8fb0d7**。

| 源码 | 用途 |
|---|---|
| [minimal_model/model.py](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/minimal_model/model.py) | 规则、批量输出及单工单证据卡 |
| [minimal_model/README.md](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/minimal_model/README.md) | 输入、阈值、运行及边界 |
| [integration_plan_v1/experiment.py](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/integration_plan_v1/experiment.py) | 客户级套餐与集成关联 |
| [integration_plan_v1/independent_verify.py](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/integration_plan_v1/independent_verify.py) | 来源、点估计及固定断言复核 |
| [ticket_bridge_v1/experiment.py](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/ticket_bridge_v1/experiment.py) | 12项工单比较与Holm校正 |
| [validation_results.json](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/validation_v1/validation_results.json) | 历史规则与月序负对照结果 |
| [reproduce.py](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/reproduce.py) | 固定快照的实验、检查与汇总 |
| [requirements.txt](https://github.com/TsingZYY/atlassian-support-review-experiments/blob/c6ece712402e7cba83cd2529cc7073deba8fb0d7/requirements.txt) | 分析依赖版本 |

## 自行运行

以下为说明，整理期间未执行：

~~~powershell
git clone https://github.com/TsingZYY/atlassian-support-review-experiments.git
cd atlassian-support-review-experiments
git checkout c6ece712402e7cba83cd2529cc7073deba8fb0d7
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe minimal_model/model.py
~~~

单条入口为 minimal_model/model.py --ticket-id 6545，这个ID是合成工单示例。批量运行写出minimal_model/outputs/predictions.json及summary.json，会创建或改写本地生成产物。

完整快照可自行执行python reproduce.py；它会运行原有实验和检查，不是只读查看。--include-scenarios另行纳入明示假设的条件模拟，不能把其输出当真实业务结果。

## 数据与发布范围

- 本目录不重复CSV、客户行、历史模型输出或演示文稿；数据定义和产物保留在原仓库。
- 上游data/README.md将数据标为比赛合成数据，没有将其描述为真实客户访谈。
- 保留原仓库的来源说明。没有给上游数据追加许可证，也没有将第三方材料重新宣称为本人原创；公开可读不等于本档案另行授予再分发许可。
- 结果引用固定快照的保存文件，本轮没有重跑实验、测试或业务试点。

