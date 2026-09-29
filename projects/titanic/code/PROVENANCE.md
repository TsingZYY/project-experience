# 代码来源与整理边界

**整理日期：** 2026-09-30  
**来源：** 用户现有本地Titanic项目的当前源码与Notebook；未核实该项目有独立远端源码仓库。

## 复制方式

- src/titanic_pipeline.py、src/__init__.py、requirements.txt逐文件复制，内容未修改。
- notebooks/titanic_end_to_end.ipynb保留所有单元格源码及顺序，只清除输出、执行计数、单元格元数据与附件；文档级元数据仅保留通用Python内核信息。JSON缩进会随序列化改变。
- 新增的README、数据说明、.gitignore及本文件用于打包和说明，不改变算法。
- 原模块和Notebook未发现上游LICENSE或版权署名声明；保留已有注释，没有给数据、依赖或其他第三方材料追加授权。
- 本次没有新增或运行实现测试、训练或Notebook执行。发布前只检查复制内容及潜在私密信息。

## SHA-256快照

| 文件 | SHA-256 |
|---|---|
| 原始Notebook，仅哈希，不随包发布 | 03b031830b0cbfa296b09ebf6ebc64143854fd9aea303fe54fc22ae6285c8bb9 |
| 清除输出后的Notebook | 7df4a64e5944c7bbd85c634eab3f035612a49cd378a98a4f150a4f5082871dbb |
| src/titanic_pipeline.py | 7c7aa087939ce6f14b50801d488c2eb68b37635fad36afb524e9615e8b0a5d6d |
| src/__init__.py | e52e84a67ec422865a7d7209b421a340226a77eec53a6741b6b396e089d39170 |
| requirements.txt | 99d9ee8517abc2fbacb902e4ca374fcdb38d8b5e2a7abfa39ed58a1ca7725569 |

## 未随包发布

原始CSV及压缩包、已训练模型、预测文件、Notebook原有表格和图像输出、个人绝对路径、旧README、旧随机划分验证脚本、旧Notebook生成脚本及原测试文件。

旧验证脚本与当前家庭分组协议不一致，排除它是为了避免混合协议；本次没有改写或运行该脚本。文档中的历史数字来自原Notebook保存输出，不是对整理包的新一次执行结果。

