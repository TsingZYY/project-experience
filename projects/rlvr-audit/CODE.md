# 代码入口与执行边界

[项目首页](README.md) · [时间线](TIMELINE.md) · [笔记](NOTES.md) · [复盘](REFLECTION.md)

## 固定代码快照

仓库：[TsingZYY/rlvr-verifier-error-transfer-evidence][repo]  
核查提交：**`dbb820ce53f6360a764eabdd829b98c9f392f866`**。本页所有链接固定到该提交；源码保留在原仓库，不在作品集中重复复制。

## 推荐阅读顺序

| 顺序 | 文件 | 用途 |
|---|---|---|
| 1 | [README][readme]／[EVIDENCE_STATUS][status] | 先确认纳入范围与科学状态 |
| 2 | [R10 诊断分析器][r10]／[诊断结果][r10result] | 查看潜在身份与表层解释的比较 |
| 3 | [R13 目标对齐协议][protocol] | 理解固定源更新、目标 codebook 对齐与结论范围 |
| 4 | [匹配面板生成器][generate]／[验证器][validate] | 面板构造与约束检查 |
| 5 | [R13 结果验证器][results] | 检查结果记录是否符合开发协议；文件存在不等于已有科学结果 |
| 6 | [批次 runner][runner]／[运行时 bootstrap][bootstrap] | 模型执行的编排、环境与许可边界 |
| 7 | [执行回执工具][receipt]／[来源范围检查器][scope] | 保存执行证据并检查交付变动范围 |

## 环境与入口

根目录 `run_with_receipt.py` 是 Python 命令包装工具：执行指定命令，保存 stdout、stderr、退出码与 SHA-256。`verify_p4_r1a_scope.py` 比较父 ZIP 与 staging tree，不能在缺少对应父归档时完成原始比较。

R13 原开发 bootstrap 明确依赖冻结的 **Python 3.10** 解释器和隔离参数 `-I -S -B`，检查运行时、依赖元数据及 GPU 条件。模型资产与环境分别由[模型清单][inventory]和[运行时参考][runtime]描述。仓库是经过整理的证据快照，没有统一的一键实验安装入口。

`r13_local_batch_runner.py` 包含 canary、worker 和批次协调接口；调用模型相关命令前需要对应完整清单、资产、环境与执行条件。仓库不附模型权重、完整生成资产、全部本地环境或第三方 PDF，因此克隆仓库本身不足以重建历史模型执行。

本页提供代码导航，不给出绕过前置条件的模型启动命令。本次整理没有调用 runner、下载模型或重新运行测试。

## 现有执行记录

[2026-08-06 canary 回执][canary]记录 1 次模型加载、16 次 forward、14 次 backward、1 次手动参数步及零科学单元。[开发执行清单][manifest]处于八进程计划就绪、模型科学批次未运行的状态。

请结合状态文档解读历史文件中的 `PASS`、`RESULT` 等局部标签；它们不自动构成 R13 科学结果。

[repo]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/tree/dbb820ce53f6360a764eabdd829b98c9f392f866
[readme]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/README.md
[status]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/EVIDENCE_STATUS_2026-08-09.md
[r10]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/analyze_r10_latent_vs_surface_r1.py
[r10result]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R10_LATENT_VS_SURFACE_DIAGNOSTIC_RESULT_R1.json
[protocol]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R13_TARGET_ALIGNMENT_PILOT_PROTOCOL_DRAFT_R1.json
[generate]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/r13_matched_panels_generate_r1.py
[validate]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/r13_matched_panels_validate_r1.py
[results]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/validate_r13_local_development_results_r1.py
[runner]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/mvp_same_source_v1/r13_local_batch_runner.py
[bootstrap]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/mvp_same_source_v1/r13_local_runtime_bootstrap.py
[receipt]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/run_with_receipt.py
[scope]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/verify_p4_r1a_scope.py
[inventory]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R13_MODEL_INVENTORY_R1.json
[runtime]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R13_RUNTIME_ENVIRONMENT_REFERENCE_R1.json
[canary]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R13_LOCAL_TECHNICAL_CANARY_RECEIPT_20260806T040040Z.json
[manifest]: https://github.com/TsingZYY/rlvr-verifier-error-transfer-evidence/blob/dbb820ce53f6360a764eabdd829b98c9f392f866/GPT_PRO_REVIEW_RLVR_V1/formal_g1_development_r1/R13_LOCAL_DEVELOPMENT_EXECUTION_MANIFEST_20260806T040334Z_39cc6d58.json

