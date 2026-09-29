# 使用说明

[项目首页](../README.md) · [来源](../PROVENANCE.md)

需要 Python 3，使用标准库，无第三方依赖。没有为此快照保存完整运行环境版本；本次未重新运行。

把工作目录设为当前 `code/`，准备自己的 `old.txt`、`new.txt` 后，在 Python 中调用：

```python
from diff import OriginalNewFiles

pair = OriginalNewFiles("old.txt", "new.txt")
for commands in pair.all_diff_commands():
    print(commands)
```

若已有差异命令文件，可以解析后检查：

```python
from diff import DiffCommands, DiffCommandsError, OriginalNewFiles

pair = OriginalNewFiles("old.txt", "new.txt")
try:
    commands = DiffCommands("changes.txt")
except DiffCommandsError as error:
    print(error)
else:
    if pair.is_valid_diff(commands):
        pair.print_diff(commands)
```

以上为接口使用说明，不包含课程输入／输出样例，也未在本次执行。模块没有 CLI，直接运行 `python diff.py` 不会自动比较文件。

文件应能用当前 Python 默认文本编码读取。全最优结果枚举适合小型文本；长文件或大量重复行可能占用很多时间和内存。
