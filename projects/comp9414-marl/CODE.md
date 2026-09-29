# 代码入口：核心定义摘录

[项目首页](README.md) · [时间线](TIMELINE.md) · [笔记](NOTES.md) · [复盘](REFLECTION.md)

## 这份代码的范围

[marl_core.py](code/marl_core.py)与[marl_core.ipynb](notebooks/marl_core.ipynb)是**核心定义摘录，不是完整原作业 notebook**。函数和类的代码体按源文本保留；仅抽取配置、常量、环境、网络、训练／评估及指标定义，合并 NumPy import。

已省略原有 markdown、学生编号、所有输出、执行计数和元数据，以及自动实验、自动加载模型、绘图／render hook、演示和有限差分检查执行单元。Notebook 顶部的说明是本次新写的导读，不是课程题面。

| 文件 | 用途 |
|---|---|
| [code/marl_core.py](code/marl_core.py) | 可直接查看的NumPy核心源码；导入不会启动训练或评估 |
| [notebooks/marl_core.ipynb](notebooks/marl_core.ipynb) | 同一核心定义的分段阅读版，无存储输出 |
| [requirements.txt](requirements.txt) | 仅声明核心运行依赖NumPy |
| [historical_results.json](evidence/historical_results.json) | 从原文档／存储输出转录的历史指标，没有执行新评估 |
| [source_provenance.json](evidence/source_provenance.json) | 源文件哈希、单元编号、每段来源及发布文件哈希 |

## 源码映射

源单元编号按**零起点JSON cell index**，不是 notebook 的执行编号：

| 单元 | 保留内容 |
|---|---|
| 3 | 训练配置和计数常量；去掉自动运行／产物目录变量 |
| 6、7 | 环境常量、空间接口、`MultiAgentCleaningEnv` |
| 18、19 | MLP、Adam、策略／价值网络、GAE、PPO与价值损失梯度 |
| 32、33 | IPPO采样更新、`train()` |
| 34、35 | 参数处理、动作／value接口、`evaluate()`与汇总 |
| 51 | 共享actor、agent-ID、集中critic的MAPPO |
| 64 | RCR和JSD指标 |

源文件SHA-256为 `bf52eb1d4b43bed4dee7ef5f8321a38a7794442188d128220c04c3aa35f4f9ed`。

## 环境与阅读

建议Python 3.10+，在本项目目录安装NumPy：

```bash
python -m pip install -r requirements.txt
```

运行 `.py` 仅加载定义，不会输出历史结果。Notebook可直接在GitHub阅读；本地交互查看需另外准备支持`.ipynb`的编辑器或Jupyter，这不属于核心算法运行依赖。

环境的`render()`原本依赖单独注册的绘图hook，本摘录未附带它。使用`reset()`、`step()`和数组观测即可查看状态；此版不提供GIF和Matplotlib展示。

## 如需自行训练

未附带历史模型，所以不能从此目录直接加载历史权重重现表格。以下示例会实际训练一个配置；**本次整理没有执行**：

```python
# 从本项目目录启动Python后，显式选择训练。
import sys
sys.path.insert(0, "code")
from marl_core import CFG, train, set_weights, evaluate, summarize_eval

cfg = dict(CFG)
trained = train("ippo", "random", cfg, iterations=400, seed=0)
models = trained["agents"]
set_weights("ippo", models, trained["best_weights"])
evaluation = evaluate("ippo", models, "random", 400, cfg, seed=123)
print(summarize_eval(evaluation))
```

此示例说明接口，不是冻结的历史复现实验协议；它没有恢复原共同观测库或全部最终评估种子。重新训练会产生新结果，需要另存运行配置与输出，不应覆盖或冒充本目录的历史指标。

## 核查状态

本次仅阅读源定义、静态抽取并清理发布内容。没有执行摘录、测试、训练或评估，不能将原版本的历史检查结果当作新摘录的运行验收。

