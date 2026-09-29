# 代码、环境与来源

[返回项目](README.md) · [运行说明](code/README.md)

## 已交付代码

- [submission.py](code/submission.py)：历史最终打包的完整独立 Agent。
- [requirements-local.txt](code/requirements-local.txt)：原本地项目的轻量 SDK 环境版本清单，供可选本地模拟使用。

入口为 `agent(obs)`，接收游戏 observation 字典，返回包含 `farmer`、`hands` 和 `market` 动作的字典。Agent 本身只有 Python 标准库依赖；Kaggle SDK 是外部模拟器，未内嵌在策略中。

## 来源身份

| 项目 | 值 |
|---|---|
| 原相对路径 | `artifacts/kaggriculture_day9_three_shop/submission.py` |
| 本目录路径 | `code/submission.py` |
| 字节数 | 19,876 |
| SHA-256 | `22770F3FA4EDD927BBC20362EC0E54FAB81DD5A5205E636FECD76ADF22774A31` |
| 标准库导入 | `math`、`collections.abc`，及 `__future__` 注解设置 |
| 原模拟环境 | Python 3.12、kaggle-environments 1.32.7 |
| 依赖清单 SHA-256 | `2F7696C36FADC1A7F9A99850A5E4D457C167566CE606C1355B7A64E99D8D976C` |

源码和依赖清单逐字复制，未裁剪参数、重写算法或重新打包。保留了原工厂函数及其导出；最终 `agent` 只选择 8 牛或 9 牛分支。

## 检查状态

本次复制后源码哈希与原文件和历史 QA 报告一致，依赖清单哈希与原文件一致。文本检查未发现凭据、私人绝对路径或文件／网络访问逻辑。原 QA 记录中的 7,190 动作一致性属于历史实验，本次没有重跑。

## 来源与使用条款

策略来自本地 Kaggriculture 项目的生产调度和门控候选；环境与 observation／action 接口来自 [Kaggle Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)。本目录不复制官方游戏引擎、对手源码、比赛输出或价格／回放数据。

所选本地源文件未附许可证头，项目根目录未发现独立许可证。本次完整保留其头部说明，不擅自添加新的开源许可证；游戏 SDK 和其他依赖仍按各自许可证使用。公开可见本身不等同于已授予所有用途的再许可。
