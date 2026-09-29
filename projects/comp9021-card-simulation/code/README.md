# 使用说明

[项目首页](../README.md) · [来源](../PROVENANCE.md)

需要 Python 3，无第三方依赖。终端应支持 UTF-8 和扑克牌 Unicode 字符。此快照没有单独的环境锁文件；本次未重新运行。

## 单局交互

在当前 `code/` 目录执行其中一个：

```sh
python solitaire_1.py
python solitaire_2.py
```

按提示输入整数 seed。第二个程序运行后可根据菜单查看日志行或输入 `q` 退出。

## 批量模拟

在 Python 中导入所需版本：

```python
from solitaire_1 import simulate

# 参数：正整数局数、起始整数 seed。
simulate(100, 37)
```

第二套接口同名：

```python
from solitaire_2 import simulate

simulate(100, 37)
```

这里给出的是自定义调用示例，没有附预期输出，未在本次执行，也不是学校原题样例。函数打印样本频率表，不返回概率模型。需要比较记录时，应保留局数、起始 seed、Python 版本和源码哈希。

文件原样保留；源码来源和使用条款说明见 [PROVENANCE.md](../PROVENANCE.md)。
