# 代码入口与复现状态

[项目首页](README.md) · [时间线](TIMELINE.md) · [笔记](NOTES.md) · [复盘](REFLECTION.md)

## 固定版本

源码仓库：[TsingZYY/llm-eval-lab](https://github.com/TsingZYY/llm-eval-lab)  
本页链接统一固定到已核查提交 **`9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4`**。源码保留在原仓库，本作品集不重复复制。

| 入口 | 作用 |
|---|---|
| [config.yaml][config]／[测试案例][cases] | 配置模型、prompt 与轮次；40 条分层数据 |
| [src/run_eval.py][run] | 批量生成、prompt 哈希、恢复已有进度 |
| [src/llm.py][llm] | 模型客户端、环境变量凭证、mock、请求退避 |
| [src/judge.py][judge] | 结构化校验、双向比较、评分续跑 |
| [src/io_utils.py][io] | JSONL 与进度文件处理 |
| [src/report.py][report] | 案例聚合、sign test、Markdown 报告 |
| [src/annotate.py][annotate]／[src/agreement.py][agreement] | 人工盲评及一致性分析 |
| [run_pipeline.ps1][pipeline] | Windows 流程封装，包含单元测试调用 |

## 环境与运行顺序

使用支持源码类型标注语法的 Python 3.10+；依赖清单为 [`requirements.txt`][requirements]，其中声明 `pyyaml>=6.0`。Claude 分支还需可选 `anthropic` 依赖；默认生成端／裁判端通过 HTTP 接口调用。

以下是使用顺序说明，**本次整理没有执行这些命令**。建议在独立 checkout 中运行，以免覆盖现存 `results/`：

```bash
python -m pip install -r requirements.txt
python src/run_eval.py
python src/judge.py
python src/report.py
```

缺少对应凭证时，客户端会进入 mock；要进行真实实验，需要按 `config.yaml` 配置可用模型与服务地址，并通过环境变量提供对应凭证。配置中的本地裁判服务需要自行准备，克隆代码不会自动提供该服务。仅传 `-AllowMock` 是允许缺少凭证，并不强制所有调用转为 mock。

人工复核使用 `src/annotate.py` 和 `src/agreement.py`。当前未提供完成的人评数据，不能从空标注文件重建一致率结果。

## 本地扩展与已发布版本

registry、持久请求缓存、可配置 assertions、G-Eval、HTML viewer、输出哈希过期标注过滤，以及 mock 输出目录隔离，均属于后续本地改动。**以上固定源码链接不包含这些扩展，本次整理也未发布它们。**

## 证据状态

历史记录报告过 26/26 测试通过；这是历史执行记录，不是本次重新验证。当前本地报告是 mock。真实模型历史运行的完整原始包尚未恢复，本文不承诺当前环境一键重现历史得分。

[config]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/config.yaml
[cases]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/data/testcases.jsonl
[run]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/run_eval.py
[llm]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/llm.py
[judge]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/judge.py
[io]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/io_utils.py
[report]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/report.py
[annotate]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/annotate.py
[agreement]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/src/agreement.py
[pipeline]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/run_pipeline.ps1
[requirements]: https://github.com/TsingZYY/llm-eval-lab/blob/9bc889478c80e10dc6a38e2d4fbc75b0c48a20d4/requirements.txt

