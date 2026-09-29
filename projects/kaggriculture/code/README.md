# 独立 Agent 使用说明

[项目首页](../README.md) · [来源与哈希](../CODE.md)

## 策略接口

`submission.py` 的最后一个顶层函数是 `agent(obs)`。它接收官方环境 observation，返回动作字典；需要真实游戏状态，不能用空字典调用。

```python
from submission import agent

# observation 由 Kaggriculture 环境提供。
action = agent(observation)
```

Agent 仅依赖标准库；原项目使用 Python 3.12。直接运行 `python submission.py` 只定义函数，不会自动开始比赛。

## 可选：原本地 SDK 环境

在本目录创建并激活 Python 3.12 虚拟环境后，可按原项目记录安装轻量依赖：

```sh
python -m pip install --no-cache-dir --no-deps -r requirements-local.txt
```

依赖清单是原文件快照，其中 SDK 固定为 `kaggle-environments==1.32.7`。本次没有重新安装，其他系统上的依赖可用性和兼容性未重新验证。

安装后，下例在 Python 中按文件路径加载 Agent，对战该 SDK 内置的 `starter`：

```python
from kaggle_environments import make

env = make(
    "kaggriculture",
    configuration={"episodeSteps": 720},
    debug=True,
)
env.run(["submission.py", "starter"])
for player, state in enumerate(env.steps[-1]):
    print(player, state.reward, state.status)
```

工作目录应为当前 `code/` 目录。示例只运行一场本地比赛，不等于历史 2,400 场评估，也不会提交 Kaggle。上例依据原 `run_local.py` 的调用方式整理，本次未执行。

## 快照与打包

原包支持独立 Python 文件，备用 ZIP 的根文件名为 `main.py`。本目录提供可检查的独立源码，不额外保存重复 ZIP。若实际提交，应核对届时比赛入口和格式要求。

源码完整保留历史参数、辅助函数和头部说明；许可证及第三方环境归属见 [CODE.md](../CODE.md)。
