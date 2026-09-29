# 代码与运行入口

[项目首页](README.md)

## 实际代码

| 文件 | 用途 |
|---|---|
| [src/titanic_pipeline.py](code/src/titanic_pipeline.py) | 特征工程、预处理、候选、Pipeline及校验 |
| [src/__init__.py](code/src/__init__.py) | 项目包 |
| [titanic_end_to_end.ipynb](code/notebooks/titanic_end_to_end.ipynb) | 当前家庭分组及三项特征实验 |
| [requirements.txt](code/requirements.txt) | 原项目固定依赖 |
| [数据说明](code/data/raw/README.md) | 自行提供文件的要求 |
| [来源说明](code/PROVENANCE.md) | 复制范围、哈希及排除内容 |

模块及依赖为原文件复制。Notebook单元格源码不变，只清除输出、执行计数、单元格元数据及附件，保留通用内核说明。没有改动算法、切分或特征规则。

## 自行运行

先进入本项目的code目录，以下说明本轮未执行：

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
~~~

原环境使用Python 3.12系列；本轮没有确认其他解释器或依赖安装情况。从[Kaggle Titanic数据页](https://www.kaggle.com/competitions/titanic/data)按要求取得以下文件，放入code/data/raw：

~~~text
train.csv
test.csv
gender_submission.csv
~~~

在JupyterLab打开notebooks/titanic_end_to_end.ipynb，使用新内核按顺序运行。缺少数据会报错，不会自动替换成模拟数据。运行包含训练、原Notebook已有检查和文件生成。

TITANIC_DATA_DIR、TITANIC_OUTPUT_DIR、TITANIC_MODEL_DIR环境变量可以覆盖数据、输出和模型目录。

## 源码定义的预期产物

- outputs/submission.csv：418行预测，列为PassengerId、Survived。
- models/titanic_pipeline.joblib：完整处理与模型Pipeline。
- Notebook中的本次模型比较、实验和评估输出。

这不是本轮已运行证明。重新运行应记录日期、环境和数据来源，不冒充原有历史结果。

## 未收录内容

- 原始CSV、压缩包、已训练模型、预测CSV、Notebook存储输出。
- 原项目测试；本次没有增加或执行测试。
- scripts/validate_official_run.py：仍按旧随机划分协议，当前包排除。
- scripts/build_notebook.py：旧生成器可能重新生成旧协议Notebook，当前包排除。
- 旧README中的0.849结果和个人机器路径。

未核实该项目已有独立远端源码仓库；当前包提供实际实现。保留原注释和已有署名，不为第三方数据或依赖追加授权。

