# Yiyang Zheng · 项目经历与工程作品集

[中文项目经历](EXPERIENCE.zh-CN.md) · [English résumé bullets](EXPERIENCE.en.md) · [主项目完整介绍](PROJECT_EXPERIENCE.md) · [证据与版本说明](EVIDENCE.md)

这份作品集根据跨对话开发记录、当前本地文件及已有 GitHub 仓库整理，整理日期为 **2026-09-30**。主线是 **AI 应用工程、评估可靠性与数据驱动决策**。

## 推荐先读

### LLM Prompt 回归评估平台

用固定分层测试集比较 prompt 版本，将批量生成、结构化评分、双向 A/B 比较、案例级统计及人工复核工作流连接起来。

**重点能力：** Python 数据管道、模型服务接入、实验设计、失败恢复、评估偏差控制。

→ [完整项目经历与面试讲述](PROJECT_EXPERIENCE.md)  
→ [源码仓库：llm-eval-lab](https://github.com/TsingZYY/llm-eval-lab)

## 项目目录

| 项目 | 可展示内容 | 当前成果范围 |
|---|---|---|
| [LLM Prompt 回归评估](projects/llm-evaluation.md) | 配置驱动评测、双向比较、案例级统计、人工盲评工具 | 工程已实现；当前保存报告为 mock |
| [Atlassian 客服数据分析](projects/atlassian-analytics.md) | 多表质量检查、关联分析、可追溯规则原型、负对照 | 比赛合成数据上的离线结果 |
| [Algothon 量化策略研究](projects/algothon.md) | 策略迭代、评测口径、回放与发布检查 | 本地回放；已有研究笔记仓库 |
| [Kaggriculture 决策智能体](projects/kaggriculture.md) | 状态决策、基线回退、种子与座位对照、提交一致性 | 本地比赛环境评估及打包 |
| [Titanic 表格机器学习](projects/titanic.md) | Pipeline、家庭分组切分、特征对照、提交生成 | 教学型机器学习实现 |
| [RLVR 验证器风险研究](projects/rlvr-audit.md) | 冻结协议、机制审计、回放和证据管理 | 研究工程；正式科学实验未完成 |

这些是独立项目，分别保留数据、评测口径和状态。

## 如何用于求职

- **AI 应用／LLM 工程：** 先选 LLM 评测，再选 Kaggriculture 与 Atlassian。
- **数据分析：** 先选 Atlassian，再选 Titanic；重点解释数据质量与统计结论。
- **量化／算法：** 先选 Algothon，再选 Kaggriculture；说明公开窗口与独立评估的区别。
- **研究工程：** 可补充 RLVR 的协议与审计工作，明确尚未得到科学结论。

[中文简历版本](EXPERIENCE.zh-CN.md)提供可直接使用的项目条目；[英文版本](EXPERIENCE.en.md)保留相同证据口径。

## 整理原则

开发记录中包含 AI 辅助开发与研究。本作品集总结已有工作产物，不将所有代码描述为独立手写，不推断未记录的团队职位、贡献比例、获奖或商业部署。

本仓库存放项目介绍与证据索引。已有实现通过原仓库链接访问；未额外上传原始对话、个人联系方式、客户级数据、模型凭据或其他项目的完整代码。部分源仓库是私有仓库，需要账号权限。

整理时读取了代码、已保存结果与历史记录，**未重新运行实验或测试**。各项目页面说明了可核实成果及版本限制。
