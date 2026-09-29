# 代码、环境与来源

[返回项目](README.md) · [运行说明](code/README.md)

## 已交付代码

- [strategy_v10_o2.py](code/strategy_v10_o2.py)：完整 V10-O2 候选。
- [requirements.txt](code/requirements.txt)：记录所选历史验证环境中的 NumPy 版本。

入口为 `getMyPosition(prcSoFar)`。输入是按比赛资产顺序排列的 `51 × T` 正价格矩阵，输出为 51 维整数目标仓位。直接运行该文件不会自动回测；比赛或调用方需要提供价格历史。

源码包含冻结资产配对、精确阈值及在线选择逻辑，保留原头部说明，没有删减成示意代码。

## 来源身份

| 项目 | 值 |
|---|---|
| 原项目 | `algothon26-starter-code` 工作区 |
| 原相对路径 | `audit_v10_20260730/final_submission_3127cdb2/get prize.py` |
| 本目录路径 | `code/strategy_v10_o2.py` |
| 字节数 | 16,572 |
| SHA-256 | `45E99414A1E237E1330F425A713D7E9F39EFF7F9E95F837CD6C70789778DF6DD` |
| 导入 | Python 标准库 `hashlib`、第三方 `numpy` |
| 历史验证环境 | Python 3.13.9、NumPy 2.3.5 |

仅改变存放位置和文件名；复制后哈希与原文件及历史报告一致。使用可导入的文件名便于阅读，正式比赛包的根文件名要求仍需按相应比赛规则处理。

## 本次检查与未执行内容

本次核对文件身份、依赖和文本内容；未发现凭据、私人绝对路径或文件／网络读取依赖。没有重新运行源码、回测或历史测试，因此本目录不把历史运行记录表述为本次验证结果。

## 来源与使用条款

比赛背景与接口参考 UNSW FinTech Society / Susquehanna Algothon 2026。官方起点见 [starter repository](https://github.com/UNSW-FinTech-Society-IT/algothon26-starter-code)。本目录复制的是本地候选策略，未复制官方评估器和价格数据。

所选候选源文件未附许可证头，原工作区根目录亦未发现独立许可证。原注释完整保留，本次不擅自添加 MIT、Apache 等许可证，也不表示已取得任何第三方材料的再许可权。依赖库、官方规则及其他第三方材料适用其原有条款。
