# 代码与使用

[返回项目](README.md) · [源文件身份](PROVENANCE.md)

## 最小源码

[code/diff.py](code/diff.py) 是原正式实现的字节一致副本，没有改变逻辑或重命名类。依赖只有 Python 标准库 `re`、`sys`，不需要安装第三方包。

入口签名经源码检查为：

```python
DiffCommands(filename)
OriginalNewFiles(original_filename, new_filename)
pair.is_valid_diff(diff_commands)
pair.print_diff(diff_commands)
pair.print_unmodified_from_original(diff_commands)
pair.print_unmodified_from_new(diff_commands)
pair.all_diff_commands()
```

文件没有命令行主入口。应从 Python 导入并提供自己的文本文件；完整调用说明见 [code/README.md](code/README.md)。

## 本次范围

只复制正式实现，不包含题面、官方样例、错误命令样例或他人往届解答。复制后哈希与原文件一致；进行了文本内容检查，没有运行、修改或添加测试。

课程任务和接口来自 UNSW COMP9021，源码来自本地该课程项目。所选文件无许可证头，本次不为课程材料或未知权属内容添加新的许可；来源记录见 [PROVENANCE.md](PROVENANCE.md)。
