# Boofuzz 框架探究

由于 Boofuzz 是本漏挖系统的核心，所以值得花费大量的时间来研究该框架的用法。

## 原语

### Blocks

#### [Repeat](https://boofuzz.readthedocs.io/en/stable/user/protocol-definition.html#repeat)

场景：当需要重复使用一个相同的字段/字段组时，有什么办法可以简洁地表达这种重复呢？

TODO

#### Size

协议经常会出现长度字段，其值决定了后续数据的长度。一般在定义时由两种情况：

1. 根据数据确定长度字段值
2. 根据长度字段值确定数据

针对第一种操作，解决方案是利用 Boofuzz 的 [Size](https://boofuzz.readthedocs.io/en/stable/user/protocol-definition.html#size) Block 来定义长度字段。
