# 代码与使用

[返回项目](README.md) · [来源与哈希](PROVENANCE.md)

## 最小源码

| 文件 | 主要接口 |
|---|---|
| [solitaire_1.py](code/solitaire_1.py) | `play_game(seed_value)`、`count_removed_pictures(seed_value)`、`simulate(n, i)`、`main()` |
| [solitaire_2.py](code/solitaire_2.py) | `play_game(seed_value)`、`simulate_one_game(seed_value)`、`simulate(n, i)`、`main()` |

两份文件都是原正式实现的字节一致副本。只使用标准库模块，包括 `sys`、`random`、`collections`，以及各自的文本处理辅助模块，不需要安装第三方包。

可以直接从终端启动，也可以导入 `simulate` 运行批量模拟，见 [code/README.md](code/README.md)。两个 `play_game` 的返回／输出方式不同，不应假设它们具有完全相同的 API。

## 本次范围

本次检查源码签名、文本内容与哈希，没有运行游戏、添加测试或修改逻辑。课程任务与游戏规则来自 UNSW COMP9021；目录只保存本地实现，没有学校 PDF、标准答案或官方输入输出样例。

所选文件没有许可证头。本次保留原内容，不擅自为第三方课程材料添加新许可。
