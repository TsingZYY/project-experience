# V10-O2 代码使用说明

[项目首页](../README.md) · [来源与哈希](../CODE.md)

## 环境

历史运行报告记录 Python 3.13.9、NumPy 2.3.5。源码额外只使用标准库 `hashlib`；依赖文件按该记录固定 NumPy 版本。本次没有安装环境或运行以下命令。

在本目录执行：

```sh
python -m venv .venv
# 激活虚拟环境后
python -m pip install -r requirements.txt
```

## 接口示例

在 Python 中由调用方传入已经取得使用许可的价格历史：

```python
import numpy as np
from strategy_v10_o2 import getMyPosition

# prices 必须按策略中的 NAMES 顺序排列，形状为 (51, T)。
# 每一列代表一个时间点，不能包含当前决策时尚不可见的价格。
positions = getMyPosition(np.asarray(prices, dtype=float))
```

`prices` 是调用方提供的数据变量，本仓库不附比赛数据。`positions` 是目标股数向量，不是收益率。价格历史少于 130 天时返回空仓；达到最小历史长度后执行策略。

该文件只定义策略函数，没有命令行回测入口。若在其他程序中重复使用，可调用 `reset()` 清理内部缓存；缓存只应影响运行时间。

## 注意

- 本文件与已审阅历史候选字节一致，保留原始注释和全部参数。
- 历史源码头部提及 hidden days 是设计目标，不表示已验证隐藏窗口表现。
- 完全非数值或 ragged 输入可能抛出 `ValueError`；应按比赛接口传入规则数值矩阵。
- 仓库没有添加新的开源许可证；来源与条款说明见 [CODE.md](../CODE.md)。
