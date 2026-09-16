# 代码规范
## 使用说明

#### 规范等级

- **必须 / 禁止**：团队统一执行，代码评审和自动检查可以阻止合并；
- **应当 / 避免**：一般情况下执行，有明确理由时可以例外；
- **可以**：根据上下文选择，不要求统一采用。

#### 原则顺序

当规则发生冲突时，按以下顺序判断：

1. 正确性和安全性；
2. 项目中已经自动化执行的配置；
3. 与现有代码的一致性；
4. 本文档的默认规则；
5. 个人习惯；

## Google Python Style Guide

Official Version: https://google.github.io/styleguide/pyguide.html

中文版本: https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/contents.html

下方版本: 中文版本的markdown复现并精简，包含以下部分

- Python语言规范：导入，包，异常，全局变量，嵌套/局部/内部类和函数，推导式和生成式，迭代器和操作符，生成器，lambda函数，条件表达式，默认参数值，True/False的求值，函数装饰器，__future__
- Python风格规范：分号，行款，括号，缩进，尾部逗号，注释和文档字符串，字符串，导入语句格式，语句，命名，主程序，函数长度，类型注解

### Python 语言规范

#### 导入

- 必须只导入包和模块，不直接导入普通函数、类或常量。
- 必须使用 `import x` 或 `from x import y`；其中 `y` 应当是模块。
- 只有名称冲突、名称过长或语义不清时，才可以使用 `as` 重命名。
- 只有公认缩写可以直接作为别名，例如 `numpy as np`。
- `typing`、`collections.abc` 和 `typing_extensions` 可直接导入其中的类。
- 禁止使用通配符`*`导入。

```python
# correct
import numpy as np
from sound.effects import echo
from typing import Any, TypeAlias

echo.EchoFilter(input_path, output_path)

# wrong
from sound.effects.echo import EchoFilter
from sound.effects.echo import *
```

#### 包

- 必须使用完整包路径导入模块。
- 禁止使用相对导入，也不能依赖当前工作目录或 `sys.path` 的偶然状态。

```python
# correct
from doctor.who import jodie
from project.services import user_service

# wrong
import jodie
from . import user_service
```

#### 异常

- 应当优先使用内置异常类，例如 `ValueError`、`TypeError`、`KeyError`。
- 自定义异常必须继承已有异常类，名称应以 `Error` 为后缀。
- 禁止使用 `assert` 校验公共 API 参数或实现业务逻辑；`assert` 只用于验证内部不变量和测试预期。
- 禁止使用裸 `except:`；避免捕获过宽的 `Exception`，只有重新抛出异常，或在任务、线程、服务入口等隔离边界记录异常时，才可以捕获宽泛异常。
- `try` 部分代码量必须尽可能小，只包含预期可能抛出目标异常的语句。
- 清理逻辑应使用 `finally`；文件、连接等资源优先使用 `with`。

```python
# correct
def connect_to_next_port(minimum: int) -> int:
    if minimum < 1024:
        raise ValueError(f"minimum must be at least 1024, got {minimum}")

    port = find_next_open_port(minimum)
    if port is None:
        raise ConnectionError("no available port found")

    assert port >= minimum  # 仅验证内部不变量。
    return port

# wrong
def connect_to_next_port(minimum: int) -> int:
    assert minimum >= 1024
    try:
        return find_next_open_port(minimum)
    except Exception:
        return -1
```

#### 全局变量

- 应当避免使用全局变量。
- 模块级常量可以使用，必须使用全大写与下划线命名。
- 确有必要使用可变全局状态时，必须：
    - 使用单下划线前缀标记为内部状态；
    - 通过公共函数或类方法访问；
    - 用注释或设计文档说明原因。

```python
_MAX_RETRY_COUNT = 3  # 内部常量
PUBLIC_TIMEOUT_SECONDS = 30  # 公开API的常量

_registered_handlers: dict[str, Handler] = {}

def register_handler(name: str, handler: Handler) -> None:
    _registered_handlers[name] = handler
```

#### 嵌套/局部/内部类和函数

- 只有需要捕获除 `self` 或 `cls` 以外的局部变量时，才使用嵌套函数或局部类。
- 禁止仅为了隐藏函数而嵌套函数；应改为模块级内部函数，使用单下划线前缀。
- 嵌套导致外层函数过长、难以测试或难以理解时，必须拆分。

#### 推导式和生成式

- 可以使用简单的列表、字典、集合推导式和生成器表达式。
- 每个推导式只应包含一个 `for` 和一个过滤条件。
- 出现多层循环、多层过滤或复杂转换时，必须改为普通循环。

```python
# correct
active_names = [user.name for user in users if user.is_active]
squares = (number**2 for number in range(10))

coordinates = []
for x in range(10):
    for y in range(5):
        if x * y > 10:
            coordinates.append((x, y))

# wrong
coordinates = [
    (x, y)
    for x in range(10)
    for y in range(5)
    if x * y > 10
]
```

#### 迭代器和操作符

- 对支持迭代协议的对象（列表、字典、文件），使用 `in` 或 `not in`。
- 遍历字典键时直接迭代字典；需要键值对时使用 `.items()`。
- 遍历文件时直接迭代文件对象。
- 禁止在迭代容器的同时修改该容器。

```python
# correct
for key in settings:
    process(key)

for key, value in settings.items():
    save(key, value)

for line in source_file:
    parse(line)

# avoid
for key in settings.keys():
    process(key)

for line in source_file.readlines():
    parse(line)
```

#### 生成器

- 可以使用生成器处理流式数据或大型数据集。
- 生成器文档字符串必须使用 `Yields:`，不能使用 `Returns:` 描述产出值。
- 生成器持有文件、连接等资源时，必须确保未完全消费时也能释放资源。

```python
def iter_valid_rows(path: str):
    """逐行生成有效记录。

    Yields:
        解析后的有效记录。
    """
    with open(path, encoding="utf-8") as source:
        for line in source:
            if record := parse_record(line):
                yield record
```

#### Lambda 函数

- `lambda` 只可以用于简短、单行且含义直接的表达式。
- 超过 60～80 个字符、包含复杂逻辑或需要文档说明时，必须改为命名函数。
- 应当使用推导式或生成器表达式替代 `map()`、`filter()` 与 `lambda` 的组合。
- 常见运算应优先使用 `operator` 模块中的函数。

```python
# correct
sorted_users = sorted(users, key=lambda user: user.last_login)
active_names = [user.name for user in users if user.is_active]

# avoid
active_names = list(
    map(lambda user: user.name, filter(lambda user: user.is_active, users))
)
```

#### 条件表达式

- 条件表达式只可以用于条件、真值和假值分支都很简单的情况。
- 包含复杂调用、多步逻辑或难以快速理解时，必须用完整的 `if` 语句。

```python
# correct
label = "active" if user.is_active else "inactive"

# wrong
message = (
    build_success_message(user, permissions)
    if validate_user_and_permissions(user, permissions)
    else build_detailed_denial_message(user, permissions)
)
```

#### 默认参数值

- 禁止使用列表、字典、集合等可变(mutable)对象作为默认参数值，允许空元组。
- 禁止使用当前时间、配置值或其他运行期间可能变化的表达式作为默认值。
- 需要可变默认对象时，必须使用 `None` 作为哨兵，并在函数体内创建实际值。

```python
# correct
def append_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# wrong
def append_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items
```

#### True/False 的求值

- 应当使用 Python 的隐式真值规则判断字符串、列表、元组和字典是否为空，例如使用`if foo:`而不是`if foo != []`。
- 检查 `None` 必须使用 `is None` 或 `is not None`。
- 禁止使用 `== True` 或 `== False` 比较布尔值。
- 多用空序列是假值的特点，`if not seq`比`if len(seq):`更好
- 整数是否为零可以显式使用 `value == 0`，避免把 `None` 当作 `0`。
- NumPy 数组判断是否为空必须使用 `.size`。

```python
# correct
if not users:
    return None

if result is None:
    return None

if retry_count == 0:
    stop_retrying()

# wrong
if len(users) == 0:
    return None

if result == None:
    return None

if enabled == True:
    run()
```

#### 函数装饰器

- 只有收益明确时才应使用装饰器，自定义装饰器必须有文档字符串和单元测试。
- 装饰器不得依赖导入时可能不可用的文件、网络、数据库等外部资源。
- 禁止用装饰器隐藏参数、返回值或控制流的重大变化。
- 应避免使用 `@staticmethod`；无实例依赖的逻辑应改为模块级函数。
- `@classmethod` 只应用于具名构造器或必要的类级状态操作。

```python
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

_P = ParamSpec("_P")
_T = TypeVar("_T")

def log_calls(function: Callable[_P, _T]) -> Callable[_P, _T]:
    """记录函数调用的装饰器。"""

    @functools.wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        logger.info("calling %s", function.__name__)
        return function(*args, **kwargs)

    return wrapper
```

#### `__future__`

- 可以使用 `from __future__ import ...` 在旧版 Python 中启用新的语言行为。
- `__future__` 导入必须位于模块文档字符串之后、所有普通导入之前。
- 在确认项目不再支持需要该导入的 Python 版本之前，禁止删除已有的 `__future__` 导入；当不再需要支持老版本时，请自行删除。

```python
"""文档字符串"""

from __future__ import annotations

import dataclasses
```

### Python 风格规范

#### 分号

- 禁止在行尾使用分号。
- 禁止使用分号把多条语句写在同一行。

```python
# correct
process_user(user)
save_user(user)

# wrong
process_user(user); save_user(user);
```

#### 行宽

- 最大行宽为80个字符。
- URL、路径、不可拆分的长导入和工具抑制注释可以例外。
- 禁止使用反斜杠显式续行；必须使用圆括号、方括号或花括号的隐式续行。
- 长字符串应放入圆括号，通过相邻字符串字面量自动拼接。

```python
# correct
if (
    width == 0
    and height == 0
    and color == "red"
    and emphasis == "strong"
):
    reset_style()

message = (
    "This is a long message that is split into "
    "multiple readable physical lines."
)

# wrong
if width == 0 and height == 0 and \
        color == "red" and emphasis == "strong":
    reset_style()
```

#### 括号

- 禁止给简单条件或返回值添加无意义的括号。
- 只有为隐式续行、明确运算优先级或表达元组时才应添加括号。

```python
# correct
if user.is_active:
    activate(user)

single_item = (item,)
return result, metadata

# wrong
if (user.is_active):
    activate(user)

return (result)
```

#### 缩进

- 每级缩进必须使用 4 个空格，禁止使用 Tab。
- 续行必须与左定界符垂直对齐，或使用 4 个空格的悬挂缩进。
- 使用悬挂缩进时，左定界符所在行不能放置参数或元素。
- 多行表达式的右括号单独成行时，必须与表达式起始位置对齐。

```python
# correct: 与左括号对齐。
result = long_function_name(first_argument, second_argument,
                            third_argument, fourth_argument)

# correct: 4 空格悬挂缩进。
result = long_function_name(
    first_argument,
    second_argument,
    third_argument,
)

# wrong
result = long_function_name(
  first_argument,
  second_argument,
)
```

#### 尾部逗号

- 单元素元组必须保留尾部逗号。
- 仅当 `]`, `)`, `}` 和最后一个元素不在同一行时, 推荐在序列尾部添加逗号。

```python
# correct
single_item = (item,)
ports = [80, 443]
ports = [
    80,
    443,
]

initialize(
    source,
    destination,
)

# wrong
ports = [80, 443,]
ports = [
    80,
    443,]
```

#### 注释和文档字符串

- 模块、公共类、公共函数和公共方法必须有文档字符串；行为、限制或副作用不明显的内部接口也应有文档字符串。
- 文档字符串应以单行摘要、空行、多行说明组成，用`"""`。
- 函数文档字符串按需使用 `Args:`、`Returns:`、`Yields:` 和 `Raises:`。
- 类文档字符串应以一行概述类的含义，并在 `Attributes:` 中记录公共属性。
- 行内注释与代码之间至少保留两个空格，并以 `#`  开头。

```python
def fetch_user(user_id: str, include_deleted: bool = False) -> User | None:
    """根据用户 ID 查询用户。

    Args:
        user_id: 用户的唯一标识。
        include_deleted: 是否包含已删除的用户。

    Returns:
        匹配的用户；不存在时返回 None。

    Raises:
        StorageError: 存储服务不可用。
    """
    ...
    
class SampleClass(object):
    """这里是类的概述.

    这里是更多信息....
    这里是更多信息....

    Attributes:
        likes_spam: 布尔值, 表示我们是否喜欢午餐肉.
        eggs: 用整数记录的下蛋的数量.
    """

    def __init__(self, likes_spam = False):
        """用某某某初始化 SampleClass."""
        self.likes_spam = likes_spam
        self.eggs = 0

    def public_method(self):
        """执行某某操作."""
        
        
if i & (i-1) == 0:  # 如果 i 是 0 或者 2 的整数次幂, 则为真.
```

#### 字符串

- 字符串格式化应优先使用 f-string，可以使用`%` 运算符或 `format` 方法。
- 禁止通过多个 `+` 拼接格式文本和变量。
- 禁止在循环中用 `+` 或 `+=` 累积字符串；应使用列表加 `"".join(parts)` 。
- 同一文件中的普通字符串`"`必须保持一致；为避免转义可以使用`'`。
- 多行字符串可以利用python的自动拼接语法

```python
# correct
x = f'名称: {name}; 分数: {n}'
x = '%s, %s!' % (imperative, expletive)
x = '{}, {}'.format(first, second)
x = '名称: %s; 分数: %d' % (name, n)
x = '名称: %(name)s; 分数: %(score)d' % {'name':name, 'score':n}
x = '名称: {}; 分数: {}'.format(name, n)
html = "".join(parts)
long_string = ("如果你不能接受多余的空格,\n"
               "也可以这样.")

# wrong
message = "user " + user_id + " has " + str(item_count) + " items"

html = ""
for part in parts:
    html += part
"""
```

#### 导入语句格式

- 每条普通 `import` 必须单独成行；`typing` 和 `collections.abc` 中的多个名称可以写在同一条导入语句中。
- 导入必须位于模块文档字符串之后、模块全局变量和常量之前。
- 导入必须按以下顺序分组：
    1. `from __future__ import ...`；
    2. Python 标准库；
    3. 第三方包；
    4. 当前代码仓库中的包。
- 每组内部必须按完整模块路径排序，排序时忽略大小写。
- 除延迟加载、可选依赖或类型检查等明确场景外，禁止在函数内部导入模块。

```python
from __future__ import annotations

import collections
from collections.abc import Mapping, Sequence
import sys
from typing import Any, TypeAlias

from absl import app
import numpy as np

from myproject.backend import user_service
from myproject.models import user
```

#### 语句

- 每行必须只写一条语句。
- 禁止把 `if`、`else`、`try`、`except` 或 `finally` 的主体写在关键字同一行。

```python
# correct
if user.is_active:
    send_notification(user)

try:
    save(user)
except StorageError:
    logger.exception("failed to save user")

# wrong
if user.is_active: send_notification(user)

try: save(user)
except StorageError: logger.exception("failed to save user")
```

#### 命名

- 名称必须有描述性，避免含义不明或项目外读者不熟悉的缩写。
- 名称长度应与作用域成正比；公共或大作用域名称必须更明确。
- 避免单字符名称，除了以下特殊情况：
    - 计数器和迭代器`i, j, k, v`
    - 在`try/except` 语句中代表异常的`e`
    - 在`with` 语句中代表文件句柄的`f`
    - 私有的、没有约束的类型变量`_T, _P`
- 包和模块的名称禁止出现连字符`-`
- 下划线的使用：
    - 双下划线开头且结尾的名称为Python保留名称。
    - 单下划线开头的名称为内部变量。
    - 双下划线开头的名称为类的私有成员，会触发名称修饰机制。

| 对象 | 公共名称 |
| --- | --- |
| 包 | `lower_with_under` |
| 模块 | `lower_with_under` |
| 类 | `CapWords` |
| 异常 | `CapWords`，通常以 `Error` 结尾 |
| 函数 | `lower_with_under()` |
| 全局／类常量 | `CAPS_WITH_UNDER` |
| 全局／类变量 | `lower_with_under` |
| 实例变量 | `lower_with_under` |
| 方法 | `lower_with_under()` |
| 函数／方法参数 | `lower_with_under` |
| 局部变量 | `lower_with_under` |

#### 主程序

- 可执行文件的主要逻辑必须放在 `main()` 函数中。
- 必须使用 `if __name__ == "__main__":` 保护主程序入口。
- 模块顶层禁止执行网络访问、对象创建或其他只应在程序启动时发生的副作用。

```python
def main() -> None:
    run_application()

if __name__ == "__main__":
    main()
```

#### 函数长度

- 函数应当短小且职责单一，函数超过约 40 行时，必须评估是否可以拆分。
- 出现多阶段、嵌套深、局部变量多或部分逻辑需要测试时，应当拆分。
- 禁止仅为满足行数而机械拆分；拆出的函数必须具有明确名称和独立职责。

#### 类型注解

1. 参考下方 PEP-484 .
2. 仅在有额外类型信息时才需要注解方法中 `self` 或 `cls` 的类型. 
3. 类似地, 不需要注解 `__init__` 的返回值 (只能返回 `None`).
4. 对于其他不需要限制变量类型或返回类型的情况, 应该使用 `Any`.
5. 无需注解模块中的所有函数；至少需要注解你的公开 API；请自行权衡

## PEP 8 -  Style Guide for Python Code

Official Version: https://peps.python.org/pep-0008/

中文版本: https://alvin.red/2017/10/07/python-pep-8/

下方版本：python 3.10+下的整理版本，重新组织了顺序

### 代码布局

#### 缩进

- 每级缩进使用4个空格
- 禁止使用Tab缩进；禁止混用Tab和空格
- 连续行有两种对齐方式，优先使用悬挂缩进
    - 对齐缩进：让所包裹的元素垂直对齐于 [] () {}，第一行有参数
        
        ```python
        foo = long_function_name(var_one, var_two,
                                 var_three, var_four)
        ```
        
    - 悬挂缩进：第一行不应该包括参数，在续行中需要再缩进一级
        
        ```python
        # 连续行多缩进一级，与其本身应所在的位置相比，缩进4个空格
        def long_fuction_name(
                var_one, var_two, var_three,
                var_four):
            print(var_one)
            
        # 连续行多缩进一级，即4个空格    
        foo = long_function_name(
            var_one, var_two,
            var_three, var_four)
        ```
        
- 较长的多个 `with` 语句使用圆括号包裹加悬挂缩进
    
    ```python
    with (
        open(source_path, encoding="utf-8") as source,
        open(target_path, "w", encoding="utf-8") as target,
    ):
        target.write(source.read())
    ```
    
- 长 `if`条件语句，使用括号包裹加悬挂缩进：`if` 加一个空格加一个左括号刚好4个字符，此时最好用空行来区分"条件继续"和"条件结束后的代码体”
    
    ```python
    if (
        user.is_active
        and user.has_permission("write")
        and resource.is_available
    ):
        update_resource(resource)
    ```
    
- 多行结束右圆/方/花括号可以单独一行书写，和上一行的缩进对齐
    
    ```python
    my_list = [
        1, 2, 3,
        4, 5, 6,
        ]
    result = some_function_that_takes_arguments(
        'a', 'b', 'c',
        'd', 'e', 'f',
        )
    ```
    

#### 每行最大长度

- 每行控制在79字符以内，文档字符串/注释为72字符
- URL、无法拆分的错误消息和不可控的第三方名称可以例外

#### 空行

- 模块级函数和类之间使用两个空行
- 类中的方法之间使用一个空行
- 函数内部可以使用一个空行分隔不同逻辑阶段
- 不要连续使用大量空行制造视觉分区

#### 空格

- 避免在方括号、圆括号和花括号之后，逗号、分号和冒号之前使用空格
    
    ```python
    # correct
    spam(ham[1], {eggs: 2})
    if x == 4: print x,y; x, y = y, x
    
    # wrong
    spam( ham [ 1 ], { eggs: 2 } )
    if x == 4 :print x , y ; x , y = y , x
    ```
    
- 在切片操作时，`:`和二元运算符是一样的，应该在其左右保留相同数量的空格；当切片操作中的参数被省略时，也应该忽略空格
    
    ```python
    # correct
    ham[1:9], hame[1:9:3], ham[:9:3], ham[1::3], ham[1:9:]
    ham[lower:upper], ham[lower:upper:], ham[lower::step]
    ham[lower+offset : upper+offset]
    ham[: upper_fn(x) : step_fn(x)], ham[:: step_fn(x)]
    ham[lower + offset : upper + offset]
    
    # wrong
    ham[lower + offset:upper + offset]
    ham[1: 9], ham[1 :9], ham[1:9 :3]
    ham[lower : : upper]
    ham[ : upper]
    ```
    
- 在二元运算符的两边都使用一个空格：赋值运算符(`=`)，增量赋值运算符(`+=`, `-=` etc.)，比较运算符(`==`, `<`, `>`, `!=`, `<>`, `<=`, `>=`, `in`, `not in`, `is`, `is not`)，布尔运算符(`and`, `or`, `not`)。不要用额外空格对齐赋值符号。
    
    ```python
    # correct
    i = i + 1
    submitted += 1
    
    x = 1
    y = 2
    long_variable = 3
    
    # wrong
    i=i+1
    submitted +=1
    
    x             = 1
    y             = 2
    long_variable = 3
    ```
    
- 如果使用了优先级不同的运算符，则在优先级较低的操作符周围增加空格，不要用超过1个空格，并保持二元运算符两侧的空格数量一致。
    
    ```python
    # correct
    x = x*2 - 1
    hypot2 = x*x + y*y
    c = (a+b) * (a-b)
    
    # wrong
    x = x * 2 - 1
    hypot = x * x + y * y
    c = (a + b) * (a - b)
    ```
    
- 使用`=`符号来表示关键字参数或参数默认值时，不要在其周围使用空格。
    
    ```python
    # correct
    def complex(real, imag=0.0)
        return magic(r=real, i=imag)
        
    # wrong
    def complex(real, imag = 0.0):
        return magic(r = real, i = imag)
    ```
    
- 在组合使用函数注解和参数默认值时，需要在`=` 两侧各使用一个空格（只有当这个参数既有函数注解，又有默认值的时候）。
    
    ```python
    # correct
    def munge(sep: AnyStr = None): ...
    def munge(input: AnyStr, sep: AnyStr = None, limit=1000): ...
    
    # wrong
    def munge(input: AnyStr=None): ...
    def munge(input: AnyStr, limit = 1000): ...
    ```
    
- 函数注解中的`:` 也遵循一般的`:` 加空格的规则，在`->` 两侧各使用一个空格。
    
    ```python
    # correct
    def munge(input: AnyStr): ...
    def munge() -> AnyStr: ...
    
    # wrong
    def munge(input:AnyStr): ...
    def munge()->PosInt: ...
    ```
    

#### 运算符换行

- 长表达式在二元运算符之前换行，使操作符与后面的操作数保持在一起：
    
    ```python
    income = (gross_wages
              + taxable_interest
              + (dividends - qualified_dividends)
              - ira_deduction
              - student_loan_interest)
    ```
    

#### 结尾逗号

- 单元素元组(tuple)必须使用结尾逗号，其他情况下无需使用
    
    ```python
    # correct
    FILES = ('setup.cfg',)
    
    # wrong
    FILES = 'setup.cfg',
    ```
    
- 多行集合、函数调用和函数签名应保留结尾逗号，以方便后续修改；单行内容不要保留结尾逗号
    
    ```python
    # correct
    FILES = [
        'setup.cfg',
        'tox.ini',
             ]
    initialize(FILES,
               error=True,
               )        
               
     # wrong
     FILES = ['setup.cfg', 'tox.ini',]
     initialize(FILES, error=True,) 
    ```
    

#### 复合语句

- 禁止使用复合语句：将多行表达式写在一行
    
    ```python
    # correct
    if foo == 'blah':
        do_blah_thing()
        do_one()
        do_two()
        do_three()
    
    # wrong
    if foo = 'blah': do_blah_thing()
    do_one(); do_two(); do_three()
    ```
    

### 源文件与模块导入

#### 源文件编码

- 源码文件使用 UTF-8 保存，但不要写编码声明
    
    ```python
    # -*- coding: utf-8 -*-
    ```
    
- 按照规范，标识符、普通注释和字符串应该尽量只写ASCII字符
- 标识符统一使用英文；用户可见字符使用产品需要的语言；注释和文档字符使用团队共同理解的语言（优先英文）

#### 模块导入

- 不同库imports必须分行写，同一模块的多个名称可以写在一行
    
    ```python
    import os
    import sys
    from subprocess import Popen, PIPE
    ```
    
- 优先使用绝对导入
    
    ```python
    import mypkg.sibling
    from mypkg import sibling
    from mypkg.sibling import example
    ```
    
- 在处理复杂的包布局时，也可用显式的相对导入，隐式的相对导入不能使用。
    
    ```python
    # 显式
    from . import sibling
    from .sibling import example
    
    # 隐式
    import sibling
    import example
    ```
    
- 当从一个包括类的模块中import一个类时，通常这样写：
    
    ```python
    from myclass import MyClass
    from foo.bar.yourclass import YourClass
    ```
    
- 如果和本地命名的拼写产生了冲突，应当直接import模块
    
    ```python
    import myclass
    import foo.bar.yourclass
    
    # 然后使用myclass.MyClass来区分MyClass
    # 使用foo.bar.yourclass.YourClass来区分YourClass
    ```
    
- 避免使用通配符`from module import *`
    
    ```python
    # 错误
    from math import *
    print(sqrt(9))
    
    # 正确
    from math import sqrt
    print(sqrt(9))
    ```
    

#### 模块内容顺序

1. 模块文档字符串`__doc__`。
2. `from __future__ import ...` 若使用，必须紧跟在模块文档字符串之后、任何普通代码或普通导入之前。`__future__` 用来在当前文件中提前启用某项语言特性或语义，它让旧版本 Python 可以提前采用某个较新版本的行为。
3. `__all__`、`__author__`、`__version__` 等模块级双下划线数据。
4. 库的导入，按以下顺序
    1. 标准库导入
    2. 第三方库导入
    3. 项目内部库导入
5. 模块本身内容
    
    ```python
    """This is the example module.
    
    This module does stuff.
    """
    
    from __future__ import annotations 
    
    __all__ = ['User']
    __version__ = '1.0.0'
    __author_- = 'Zhang'
    
    import os
    import sys
    ```
    

### 命名

#### 首要原则

对于用户可见的公共部分API，其命名应当表达出功能用途而不是其具体的实现细节。

#### 描述：命名风格

通常区分以下命名样式：

- `b` (单个小写字母)
- `B` (单个大写字母)
- `lowercase`(小写)
- `lower_case_with_underscores`(带下划线小写)
- `UPPERCASE`(大写)
- `UPPER_CASE_WITH_UNDERSCORES`(带下划线大写)
- `CapitalizedWords` (也叫做CapWords或者CamelCase – 因为单词首字母大写看起来很像驼峰)。注意：当CapWords里包含缩写时，将缩写部分的字母都大写。`HTTPServerError`比`HttpServerError`要好。
- `mixedCase` (注意：和CapitalizedWords不同在于其首字母小写！)
- `Capitalized_Words_With_Underscores` (这种风格超丑！)

下划线开始或结尾的特殊形式：

- `_single_leading_underscore`: 以单下划线开头表示模块或类的内部实现，不属于稳定公共接口。 比如， `from M import *`不会import下划线开头的对象。
- `single_trailing_underscore_`: 以单下划线结尾用来避免和Python关键词产生冲突。
- `__double_leading_underscore`: 以双下划线开头命名类属性表示触发命名修饰，主要用于防止子类意外覆盖（在`FooBar`类中，`__boo`命名会被修饰成`_FooBar__boo`）。
- `__double_leading_and_trailing_underscore__`: 以双下划线开头和结尾的命名表示“魔术”对象或属性，存在于用户控制的命名空间里（这些命名已经存在，但通常需要用户覆写以实现用户所需要的功能）。 比如， `__init__`, `__import__` 或 `__file__`。请依照文档描述来使用这些命名，千万不要自己发明。

需要避免的命名：不要使用字符’l’（L的小写的字母），’O’（o大写的字母），或者’I’（i的大写的字母）来作为单个字符的变量名，这些字符和数字1和0无法区别开来。

#### 规范：命名约定

| 对象 | 规则 | 示例 |
| --- | --- | --- |
| 模块（module） | 短小，全小写，可加下划线 | user_service.py |
| 包（package） | 短小，全小写，不可加下划线 | backend/ |
| 类（class） | CapWords | UserRepository |
| 异常（Exception） | 以Error结尾的CapWords | UserNotFoundError |
| 函数（Function） | 全小写，可加下划线 | find_user |
| 参数（Argument） | 全小写，可加下划线 | user_count |
| 常量（Constant） | 全大写，可加下划线 | MAX_RETRY_COUNT |
- 函数和方法参数：
    - 实例方法的第一参数永远都是`self` ，操作实例本身，可访问实例属性；
    - 类方法的第一参数永远都是`cls` ，操作类本身或替代构造器，不可访问实例属性，要用装饰器`@classmethod`。
- 公开和内部接口
    - 模块应该在`__all__`属性中明确申明可导出的公开API
    - 内部接口使用单下划线开头

### 注释

- 注释不应该是复述代码行为，而应该是解释代码本身无法表达的内容
- 当代码有改动时，优先更改注释使其保持最新
- 注释应该是完整的多个句子，如果是短语或一个句子，其首字母应该大写
- 如果注释很短，结束的句号可以不写。块注释的每句都应以句号结束。

#### 块注释

- 写在对应代码之前，并且和对应代码有同样的缩进级别
- 以`#` 和一个空格开头
- 如果是段落，每一行用`#` 开头来隔开

#### 行内注释

- 尽量少用行内注释
- 如果用，以`#` 和一个空格开头，至少与代码语句之间有两个空格的间隔

```python
x = x + 1    # Increment x
```

#### 文档字符串注释

参考下方 PEP 257

#### 函数注解

参考下方 PEP 484

## PEP 257 - Docstring Conventions

Official Version: https://peps.python.org/pep-0257/

中文版本: https://peps.pythonlang.cn/pep-0257/

下方版本: 整理后的版本，只保留了必要的部分

### Docstring是什么

docstring是一种出现在模块、函数、类或者方法定义的第一行说明的字符串。

以下对象必须要文档字符串：

- 公共模块、包、函数、方法
- 行为、约束或副作用不显式的内部函数

### Docstring怎么写

#### 单行Docstring

- 使用三引号，结束引号与开始引号在同一行
- 在文档字符串前后都没有空行

```python
def kos_root():
    """Return the pathname of the KOS root directory."""
    global _kos_root
    if _kos_root: return _kos_root
```

#### 多行Docstring

- 由一个摘要行（和开始引号在同一行）、一个空行，和多行详细说明组成
- 在类的所有Docstring(一行或多行)之后插入一个空白行
- 模块的Docstring通常应列出由模块导出的类，异常和函数(以及任何其他对象)，其中包含每个模块的一行摘要，这些摘要通常比对象的Docstring中的摘要行提供的细节更少。
    
    ```python
    """用户管理功能。
    
    导出的内容：
        User: 表示系统用户。
        UserNotFoundError: 找不到用户时抛出的异常。
        find_user: 根据用户 ID 查找用户。
    """
    ```
    
- 软件包的Docstring(即软件包的__init__.py模块)也应该列出软件包导出的模块和子包。例如，`shop/__init__.py` 可以写成：
    
    ```python
    """在线商店软件包。
    
    导出的模块：
        users: 用户账户管理。
        orders: 订单创建和询。
    
    导出的子包：
        payment: 支付处理功能。
    """
    ```
    
- 函数或方法的Docstring应该总结其行为并记录其参数，返回值，副作用，异常。
    
    ```python
    
    def find_user(user_id):
        """根据 ID 查找并返回用户。
    
        Args:
            user_id: 用户的唯一标识。
    
        Returns:
            对应的 User 对象。
    
        Raises:
            UserNotFoundError: 指定用户不存在时抛出。
        """
    ```
    
- 类的Docstring应该总结其行为并列出公共方法和实例变量。
    
    ```python
    class User:
        """表示系统中的注册用户。
    
        提供用户数据的封装、序列化及权限检查功能。
        该类设计为不可变对象，修改操作将返回新实例。
    
        Attributes:
            user_id: 用户的唯一标识符，只读。
            username: 用户的显示名称。
            email: 用户的注册邮箱地址。
            is_active: 账户是否处于激活状态。
    
        Methods:
            to_dict: 将用户对象序列化为字典。
            has_permission: 检查用户是否拥有指定权限。
            deactivate: 停用当前用户账户并返回更新后的实例。
        """
    
        def __init__(self, user_id, username, email, is_active=True):
            self.user_id = user_id
            self.username = username
            self.email = email
            self.is_active = is_active
    
        def to_dict(self):
            """将用户对象序列化为字典。
    
            Returns:
                包含用户属性的字典。
            """
            return {
                "user_id": self.user_id,
                "username": self.username,
                "email": self.email,
                "is_active": self.is_active,
            }
    
        def has_permission(self, permission):
            """检查用户是否拥有指定权限。
    
            Args:
                permission: 要检查的权限名称。
    
            Returns:
                如果用户拥有该权限则返回 True，否则返回 False。
            """
            # 实现省略
            return True
    
        def deactivate(self):
            """停用当前用户账户。
    
            Returns:
                一个 is_active 为 False 的新 User 实例。
            """
            return User(self.user_id, self.username, self.email, is_active=False)
    ```
    

## PEP 484 - Type Hints

Official Version: https://peps.python.org/pep-0484/

中文版本: https://www.cnblogs.com/popapa/p/PEP484.html

下方版本: 综合 PEP 484, `typing` , `collections.abc` , `typing_extensions` 的整理版本，适用于 python3

### 版本与导入

- Python 3.10+ 必须使用内置泛型和 `|` 联合类型，例如 `list[str]`、
`dict[str, int]` 和 `str | None`。
- 禁止在新代码中使用 `typing.List`、`typing.Dict`、`typing.Tuple`、
`typing.Set`、`typing.Optional` 和 `typing.Union` 等旧式别名。
- `Callable`、`Iterable`、`Iterator`、`Sequence`、`Mapping`、
`Generator`、`AsyncIterable` 和 `AsyncIterator` 等抽象类型必须从
`collections.abc` 导入。
- `Any`、`Literal`、`Protocol`、`TypeVar`、`TypedDict` 等特殊类型
必须从 `typing` 导入。
- 最低 Python 版本尚未提供的类型工具应当从 `typing_extensions` 导入；
当全部受支持版本都已提供该工具时，应当统一迁移到 `typing`。
- 禁止通过捕获 `ImportError` 在 `typing` 和 `typing_extensions` 之间动态
选择。应由项目最低 Python 版本决定唯一导入位置。
- 只有明确采用延迟求值注解时，才使用`from __future__ import annotations`。

```python
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Literal, Protocol, TypeVar, TypedDict

from typing_extensions import Self  # Python 3.10 项目。
```

### 注解范围与完整性

- 公共函数、公共方法和公共类属性必须有完整类型提示。
- 一个函数只要进入类型检查范围，所有参数和返回值就必须标注；禁止留下隐式
`Any`。`self` 和 `cls` 通常不标注，类型检查器可以自动推断。
- 没有返回值的函数和 `__init__` 必须标注 `-> None`。
- 局部变量可以依靠类型推断；空容器、初始值为 `None`、类型会在控制流中改变，或推断结果不够准确时，应当显式标注。
- 实例属性应当在类体或 `__init__` 中标注，避免只在不相关的方法中首次定义。
- `*args: T` 表示每个额外位置参数都是 `T`；`**kwargs: T` 表示每个额外
关键字参数的值都是 `T`，不能标注成 `tuple[T, ...]` 或`dict[str, T]`。
- 参数的默认值不会改变其类型，为 `None` 时参数类型必须显式包含`None`。

```python
class UserCache:
    _users: dict[str, User]

    def __init__(self) -> None:
        self._users = {}

def render_lines(
    *lines: str,
    prefix: str = "",
    **labels: str,
) -> str:
    ...

def find_user(user_id: str, fallback: User | None = None) -> User | None:
    ...
```

### 格式

- 参数注解写成 `name: Type`，返回类型写成 `-> Type`。
- 参数同时具有注解和默认值时，必须写成 `name: Type = value`；无注解的关键字参数才写成 `name=value`。
- 短签名应当保持单行；超过行宽时，每行放置一个参数，并保留尾部逗号。
- 类型表达式过长时，应当先提取有业务含义的类型别名，而不是仅为缩短代码创建含义模糊的缩写。

```python
def load_user(user_id: str, include_deleted: bool = False) -> User | None:
    ...

def build_report(
    users: Sequence[User],
    formatter: Callable[[User], str],
    metadata: Mapping[str, str] | None = None,
) -> list[str]:
    ...
```

### 基本类型与 `None`

- 基本值直接使用 `str`、`int`、`float`、`complex`、`bool`、`bytes` 等。
- `None` 是合法的类型提示。只返回 `None` 的函数使用 `-> None`。
- 参数或返回值可能为 `None` 时，必须显式写成 `T | None`。
- 禁止仅因为参数的默认值是 `None` 就省略联合类型；也禁止把“缺少值”、
`0`、空字符串和空容器混为一谈。

```python
def parse_port(raw_value: str) -> int | None:
    if not raw_value:
        return None
    return int(raw_value)
```

### 容器

- 具体容器使用内置泛型：`list[T]`、`dict[K, V]`、`set[T]`、
`frozenset[T]` 和 `tuple[...]`。
- 禁止使用未参数化的裸容器类型，例如 `list`、`dict`、`set` 和 `tuple`；
无法确定元素类型时必须说明原因，并使用 `Any` 或 `object` 明确表达边界。
- 固定长度、各位置类型不同的元组使用 `tuple[T1, T2, ...]`；任意长度的
同质元组使用 `tuple[T, ...]`；空元组使用 `tuple[()]`。
- 返回具有固定字段和业务含义的数据时，应当优先使用具名类、数据类、
`NamedTuple` 或 `TypedDict`，避免难以理解的长元组。

```python
user_ids: list[int] = []
scores: dict[str, float] = {}
point: tuple[float, float] = (12.5, 8.0)
path_parts: tuple[str, ...] = ("var", "log", "app")
empty: tuple[()] = ()
```

### 抽象集合类型

| 所需能力 | 推荐类型 |
| --- | --- |
| 只需逐项读取 | `Iterable[T]` |
| 需要 `next()` | `Iterator[T]` |
| 需要长度和按位置读取 | `Sequence[T]` |
| 需要添加、删除或改写序列 | `MutableSequence[T]` |
| 只读键值访问 | `Mapping[K, V]` |
| 需要修改键值映射 | `MutableMapping[K, V]` |
| 只需成员检查和集合运算 | `Set[T]` |
| 需要修改集合 | `MutableSet[T]` |

```python
from collections.abc import Iterable, Mapping

def total(values: Iterable[float]) -> float:
    return sum(values)

def copy_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return dict(headers)
```

### `Union`、`Optional` 与联合类型

- 一个值确实可能属于多个类型时使用 `T1 | T2`。
- `Union[T1, T2]` 与 `T1 | T2` 含义相同；Python 3.10+ 必须使用后者。
- `Optional[T]` 与 `T | None` 含义相同，不表示参数有默认值；Python 3.10+
必须使用后者。

```python
def normalize_identifier(value: int | str) -> str:
    if isinstance(value, int):
        return str(value)
    return value.strip()
```

### `Literal`

- 参数只能接受少量特定字面量时，可以使用 `Literal[...]`。
- `Literal` 适用于字符串、字节串、整数、布尔值、`None` 和枚举成员等受支持的
字面值；复杂业务状态应当优先定义 `Enum`。
- 返回类型取决于某个字面量参数时，应当结合 `@overload` 表达对应关系。
- 禁止用 `Literal` 枚举数量大、频繁变化或来自外部配置的任意字符串。

```python
from typing import Literal

SortOrder = Literal["ascending", "descending"]

def sort_users(users: list[User], order: SortOrder) -> list[User]:
    ...
```

### `Any` 与 `object`

- `Any` 表示退出该值相关的静态类型检查：它既可以赋给任意类型，也可以接受
任意操作。`Any` 不是“任意但仍需检查”的安全顶层类型。
- `object` 表示可以接收任意 Python 对象，但使用前必须通过类型收窄证明其支持所需操作。对未知输入只做存储、比较或检查时，应当优先使用 `object`。
- `Any` 只可以用于无法建模的动态边界，例如未提供类型信息的第三方库、动态
反序列化入口或逐步迁移的旧代码，并应当限制在尽可能小的作用域。
- 禁止为了消除类型错误，把整个容器、公共返回值或大段调用链改成 `Any`。
- 从动态边界取得 `Any` 后，应当尽快校验并转换成精确类型。

```python
from typing import Any

def count_truthy(elements: List[Any]) -> int:
    return sum(1 for elem in elements if elem)

def is_positive_integer(value: object) -> bool:
    return isinstance(value, int) and value > 0

def decode_external(payload: Any) -> User:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a mapping")
    return parse_user(payload)
```

### `AnyStr`

- 禁止在新代码中使用 `typing.AnyStr`。它从 Python 3.13 起已弃用，并计划在
Python 3.18 移除。
- `AnyStr` 不是“任意字符串”，也不等于 `str | bytes`；它是受 `str` 和
`bytes` 约束的类型变量，用于表达多个位置必须同时为其中同一种类型。
- Python 3.10/3.11 兼容代码应当自行定义受约束的 `TypeVar`；如果返回类型不
依赖输入类型，则应当直接使用 `str | bytes`。

### `Callable`

- 简单回调使用 `Callable[[Arg1, Arg2], ReturnType]`。
- 参数类型完全未知时才可以使用 `Callable[..., ReturnType]`；省略号会放弃对调用参数的检查

```python
from typing import Callable
 
def feeder(get_next_item: Callable[[], str]) -> None:
    
 
def async_query(on_success: Callable[[int], None],
                on_error: Callable[[int, Exception], None]
                ) -> None:

def partial(func: Callable[..., str], *args) -> Callable[..., str]:
```

### `Never` 与 `NoReturn`

- 永远不会正常返回的函数必须标注为 `NoReturn`；若项目最低版本为 Python
3.11+，应当统一使用语义更通用的 `Never`。
- `NoReturn` 和 `Never` 不等同于 `None`。前者表示控制流不会返回调用方，
后者表示函数正常返回且返回值是 `None`。

```python
from typing import NoReturn

def fail(message: str) -> NoReturn:
    raise RuntimeError(message)
```

### `Generic`

- `Generic[T]` 声明"这是一个泛型类，有一个类型参数 T"
- Python 3.10/3.11 兼容代码必须通过 `Generic[T]` 定义泛型类。
- 只有类的多个属性或方法之间确实存在类型关系时才应定义泛型类。
- 只有项目最低版本为 Python 3.12+ 时，才可以统一采用 `class Box[T]` 和
`def firstT` ，不需要显示继承`Generic`。

```python
from typing import Generic, TypeVar

_T = TypeVar("_T")

class Box(Generic[_T]):
    def __init__(self, value: _T) -> None:
        self._value = value

    def get(self) -> _T:
        return self._value
        
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")

x = int_box.get()  # 类型检查器推断 x 是 int
y = str_box.get()  # 类型检查器推断 y 是 str

class Box:
    def __init__(self, item) -> None:
        self.item = item

    def get(self):
        return self.item
        
b = Box(42)
x = b.get()  # 类型检查器认为 x 是 Any，不知道它是 int
```

```python
K = TypeVar('K')
V = TypeVar('V')

class MyMap(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

# 使用
m: MyMap[str, int] = MyMap()
m.set("age", 30)
```

### `TypeVar`

- 表示”某种类型“，但写代码时还不确定是哪一种。
- 私有类型变量使用 `_T`、`_K`、`_V`、`_R`、`_P` 等名称；公开类型变量
应当使用能表达含义的名称。
- 无约束类型变量可以绑定任意类型；`bound=Base` 表示任意 `Base` 子类型；
约束形式 `TypeVar("T", A, B)` 表示只能从列出的类型中选择一种。

```python
from collections.abc import Sequence
from typing import TypeVar
from numbers import Number

# T 只能是 int 或 str
T = TypeVar('T', int, str)

# MyNumber 必须是 Number 的子类
MyNumber = TypeVar('T', bound=Number)

_T = TypeVar("_T")
_Number = TypeVar("_Number", int, float)

def first(values: Sequence[_T]) -> _T:
    return values[0]

def add(left: _Number, right: _Number) -> _Number:
    return left + right
```

### `ParamSpec`

- 表示”一个函数的完整参数签名“，让装饰器保留原函数的参数类型。
- `P` 表示整个参数签名`Callable[P,T]`，`P.args` 表示位置参数类型`*arg: P.args` ，`P.kwargs` 表示关键字参数类型`**kwargs: P.kwargs`
- 高阶函数或装饰器需要保留被包装函数的完整参数签名时，必须使用
`ParamSpec`，不能使用 `Callable[..., T]` 丢失参数信息。

```python
# without ParamSpec
from typing import Callable, TypeVar

T = TypeVar('T')

def my_decorator(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args, **kwargs) -> T:
        print("before")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"
    
# 测试样例
greet("Alice", 30)   # ✅ 能运行
greet(123, "oops")   # ❌ 类型检查器不会报错！因为 ... 表示"任意参数"
    
# with ParamSpec
from typing import ParamSpec

P = ParamSpec('P')

def new_decorator(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args, **kwargs) -> T:
        print("after")
        return func(*args, **kwargs)
    return wrapper

@new_decorator
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"
    
# 测试样例
greet("Alice", 30)   # ✅ 能运行
greet(123, "oops")   # ❌ 类型检查器会报错！
```

```python
import functools
from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

def traced(function: Callable[_P, _R]) -> Callable[_P, _R]:
    @functools.wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.info("calling %s", function.__name__)
        return function(*args, **kwargs)

    return wrapper

def with_context(
    function: Callable[Concatenate[RequestContext, _P], _R],
) -> Callable[_P, _R]:
    @functools.wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        return function(current_context(), *args, **kwargs)

    return wrapper
```

### 协变，逆变，不变

- **为什么不能传 `List[Manager]` 给 `List[Employee]`？**
    
    ```python
    class Employee: ...
    class Manager(Employee): ...  # Manager 继承 Employee
    
    def promote_all(emps: list[Employee]) -> None:
        for emp in emps:
            emp.promote()  # 假设这是 Employee 的方法
    
    managers: list[Manager] = [Manager(), Manager()]
    promote_all(managers)  # 看起来没问题？
    
    def add_intern(emps: list[Employee]) -> None:
        emps.append(Employee())  # 塞进去一个普通员工
    
    managers: list[Manager] = [Manager(), Manager()]
    add_intern(managers)  # 类型检查器如果允许，这里就通过了
    
    for m in managers:
        m.give_bonus()  # 最后一个元素其实是 Employee，不是 Manager
    ```
    
- 协变（Covariant）为只读，只能往外拿，只能产出也就是往外送；
    
    ```python
    from typing import TypeVar, Generic, Iterator
    
    T_co = TypeVar('T_co', covariant=True)  # _co 后缀是约定
    
    class ReadOnlyBox(Generic[T_co]):
        def __init__(self, item: T_co) -> None:
            self._item = item
        
        def get(self) -> T_co:  # 只产出 T，不消费 T
            return self._item
    
    box: ReadOnlyBox[Manager] = ReadOnlyBox(Manager())
    
    def show(box: ReadOnlyBox[Employee]) -> None:
        e = box.get()  # 安全：拿出来的一定是 Employee（实际是 Manager）
        
    show(box)  # ✅ 类型检查器允许，因为 ReadOnlyBox 是协变的
    ```
    
- 逆变（Contravariant）为只写，只能往里放，只能消费也就是拿进来；
    
    ```python
    T_contra = TypeVar('T_contra', contravariant=True)  # _contra 后缀是约定
    
    class TrashCan(Generic[T_contra]):
        def put(self, item: T_contra) -> None:  # 只消费 T，不产出 T
            print(f"Discarding {item}")
    
    # TrashCan[Employee] 能装任何 Employee
    # 如果某个地方需要 TrashCan[Manager]，能不能给 TrashCan[Employee]？
    # 可以！因为"能装任何 Employee"的垃圾桶，当然能装 Manager
    
    def dispose_manager(can: TrashCan[Manager]) -> None:
        can.put(Manager())
    
    employee_can: TrashCan[Employee] = TrashCan()
    dispose_manager(employee_can)  # ✅ 逆变允许
    ```
    
- 不变（Invariant）为可读写；
    
    ```python
    T = TypeVar('T')  # 默认：不变
    
    class Box(Generic[T]):
        def get(self) -> T: ...
        def set(self, item: T) -> None: ...
    
    # Box[Manager] 不能传给 Box[Employee]
    # Box[Employee] 也不能传给 Box[Manager]
    # 必须完全匹配：Box[Manager] ↔ Box[Manager]
    ```
    

| 容器 | 可变性 | 类型参数 |
| --- | --- | --- |
| `Sequence[T]` / `Mapping[K,V]` | 只读 | **协变** |
| `MutableSequence[T]` / `MutableMapping[K,V]` | 可读可写 | **不变** |

### `type[C]`

- `C` 表示类 `C` 或其子类的实例。`type[C]` 表示类 `C` 本身或它的子类对象。
- 参数需要接收类本身而不是类的实例时，使用 `type[C]`。
- Python 3.10+ 必须使用 `type[C]`，避免使用 PEP 484 中的旧写法 `Type[C]`。
- `type[Base]` 可以接收 `Base` 及其子类的类对象；如果返回值必须保持传入的
具体子类，应当结合有上界的 `TypeVar`。
- 禁止把类对象参数写成实例类型，也禁止用裸 `type` 丢失类之间的关系。

```python
from typing import TypeVar

_UserT = TypeVar("_UserT", bound="User")

def create_user(user_class: type[_UserT], name: str) -> _UserT:
    return user_class(name=name)
```

### `Self`

- 返回当前实例或当前子类实例的方法应当使用 `Self`，包括链式方法、返回
`self` 的上下文管理器和返回 `cls(...)` 的替代构造器。
- Python 3.10 从 `typing_extensions` 导入 `Self`；3.11+从 `typing` 导入。

```python
from typing_extensions import Self

class Query:
    def __init__(self, clauses: list[str]) -> None:
        self._clauses = clauses
        self._limit: int | None = None

    @classmethod
    def empty(cls) -> Self:
        return cls([])

    def limit(self, count: int) -> Self:
        self._limit = count
        return self
```

```python
# 返回自身类型
from typing import Generic, TypeVar

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def clone(self) -> "Container[T]":
        return Container(self.value)
       
# Python 3.11+ 可以直接用 Self（更简洁）
from typing import Self

class Container:
    def __init__(self, value: int) -> None:
        self.value = value

    def clone(self) -> Self:
        return self.__class__(self.value)
```

### `TypedDict`

- 已知字符串键及其值类型的普通字典使用 `TypedDict`，只用于静态描述字典结构，不会创建运行时数据类，也不执行数据校验。
- `TypedDict` 按结构而不是按继承关系判断兼容性；两个独立定义只要键、必需性
和值类型兼容，就可以互相赋值。
- 默认所有键均为必需键。只有确实允许缺少部分键时才使用 `total=False` 或
`NotRequired[T]`；“键可以缺少”和“键存在但值可以为 `None`”必须区分。
- Python 3.10 项目中的 `Required`、`NotRequired` 和 `Unpack` 从
`typing_extensions` 导入；Python 3.11+ 从 `typing` 导入。
- 函数 `**kwargs` 具有固定键集合时，应当使用 `Unpack[SomeTypedDict]`，
不能把整个参数标注成 `SomeTypedDict`。

```python
from typing import TypedDict
from typing_extensions import NotRequired, Required, Unpack

class UserPayload(TypedDict):
    user_id: str
    display_name: str
    email: NotRequired[str]

class UserPatch(TypedDict, total=False):
    user_id: Required[str]
    display_name: str

class RequestOptions(TypedDict, total=False):
    timeout: float
    trace_id: str

def request(url: str, **options: Unpack[RequestOptions]) -> bytes:
    ...
```

### 新类型

#### 类型别名

- 类型别名用于给复杂类型提供业务名称，不会创建新类型；别名与原类型可互相
赋值。
- Python 3.10/3.11 使用 `TypeAlias` 显式声明别名。只有项目最低版本为
Python 3.12+ 时，才可以统一使用 `type Name = ...` 语句。
- 禁止把普通运行时变量误写成类型别名，也应避免为简单类型创建没有语义价值的别名。

```python
from typing import TypeAlias

UserId: TypeAlias = str
Headers: TypeAlias = dict[str, str]
UserLookup: TypeAlias = dict[UserId, User]
```

#### `NewType`

- 两个值在运行时表示相同，但在静态检查中禁止混用时，应当使用 `NewType`，
例如用户 ID 与订单 ID。
- 创建 `NewType` 值时必须显式调用对应名称；底层类型不能隐式赋给新类型，
新类型可以传给接受底层类型的接口。
- `NewType` 不进行运行时校验，也不创建可以用于 `isinstance()` 的普通类。
如果需要校验、方法或不同运行时表示，必须定义真实类。

```python
from typing import NewType

UserId = NewType("UserId", str)
OrderId = NewType("OrderId", str)

def load_user(user_id: UserId) -> User:
    ...

load_user(UserId("u-123"))
# load_user(OrderId("o-123"))  # 类型检查错误。
```

### 迭代器、生成器与异步

#### 概念与关系

| 类型 | 表示的能力 | 典型操作 |
| --- | --- | --- |
| `Iterable[T]` | 可以创建一个产生 `T` 的迭代器 | `for item in value` |
| `Iterator[T]` | 保存遍历位置，可以取得下个 `T` | `next(value)` |
| `Generator[Y, S, R]` | 支持双向通信和返回值的迭代器 | `next()`、`send()` |
| `AsyncIterable[T]` | 可以创建一个异步迭代器 | `async for item in value` |
| `AsyncIterator[T]` | 可以异步取得下一个 `T` | `await anext(value)` |
| `AsyncGenerator[Y, S]` | 支持双向通信的特殊异步迭代器 | `async for`、`asend()` |

```
Iterable[T] --iter()--> Iterator[T] --next()--> T
                              ^
                              |
                  Generator[Y, S, R]

AsyncIterable[T] --aiter()--> AsyncIterator[T] --await anext()--> T
                                    ^
                                    |
                         AsyncGenerator[Y, S]
```

- `Iterator[T]` 一定也是 `Iterable[T]`，但反过来不成立。例如列表可以使用
`for`，但必须先调用 `iter(list_value)` 才能使用 `next()`。
- 迭代器保存当前消费位置，通常只能向前消费一次，耗尽后不会自动重置。
- `Iterable[T]` 和 `AsyncIterable[T]` 不保证可以重复遍历，因为迭代器本身
也是一种可迭代对象。
- 必须重复遍历、读取长度或按位置访问时，应当使用 `Collection[T]`、
`Sequence[T]`，或接收 `Callable[[], Iterator[T]]` 形式的迭代器工厂。

```python
from collections.abc import Iterable, Iterator, Sequence

def total(values: Iterable[int]) -> int:
    return sum(values)

def take_one(values: Iterator[int]) -> int:
    return next(values)

def first_and_last(values: Sequence[int]) -> tuple[int, int]:
    return values[0], values[-1]
```

#### 函数形式决定调用方式

函数使用 `def` 还是 `async def`，以及函数体中是否含有 `yield`，决定调用后
得到的对象和正确的返回注解。

| 实际需求 | 使用的类型 |
| --- | --- |
| 参数只需要 `for` | `Iterable[T]` |
| 参数需要 `next()` 或共享消费位置 | `Iterator[T]` |
| 普通函数含 `yield`，只产出值 | `Iterator[T]` |
| 需要 `send()` 或生成器最终返回值 | `Generator[Y, S, R]` |
| 参数只需要 `async for` | `AsyncIterable[T]` |
| 参数需要 `anext()` 或共享异步消费位置 | `AsyncIterator[T]` |
| `async def` 含 `yield`，只产出值 | `AsyncIterator[T]` |
| `async def`含`yield` ，需要`asend()` | `AsyncGenerator[Y, S]` |
| `async def` 不含 `yield` | 返回注解写 `await` 后的结果 `T` |
| 参数只需要 `await` | `Awaitable[T]` |

| 函数形式 | 调用后得到 | 使用方式 | 返回注解 |
| --- | --- | --- | --- |
| `def`，不含 `yield` | 普通返回值 | 直接使用 | `-> T` |
| `def`，含 `yield` | 生成器对象 | `for` 或 `next()` | `-> Iterator[T]` 或 `Generator[...]` |
| `async def`，不含 `yield` | 协程对象 | `await` | `-> T` |
| `async def`，含 `yield` | 异步生成器对象 | `async for` 或 `anext()` | `-> AsyncIterator[T]` 或 `AsyncGenerator[...]` |
- 调用生成器函数只创建生成器对象；函数体在第一次迭代、`next()` 或
`send()` 时才开始执行。
- 调用不含 `yield` 的 `async def` 只创建协程对象；必须 `await` 该对象，
或将它创建为由事件循环调度的任务。
- 调用含 `yield` 的 `async def` 直接创建异步生成器对象；必须使用
`async for` 或 `anext()`，禁止对它使用 `await`。

#### `Iterable, Iterator`

- 参数只需要使用 `for` 时，必须优先使用 `Iterable[T]`。
- 参数会调用 `next()`、需要共享消费位置或明确操作当前游标时，必须使用
`Iterator[T]`。
- 使用 `yield` 且只向外产出值的生成器函数，应当返回`Iterator[YieldType]`。
- 生成器函数的返回注解描述函数调用后得到的生成器对象，禁止标注成单个
`yield` 值的类型。
- `return` 会结束生成器。`return some_iterable` 不会产出其中的元素；需要
依次产出另一个同步可迭代对象中的元素时，必须使用 `yield from`。

```python
from collections.abc import Iterable, Iterator

# correct
def iter_valid_names(users: Iterable[User]) -> Iterator[str]:
    for user in users:
        if user.is_active:
            yield user.name

def iter_lines(parts: Iterable[str]) -> Iterator[str]:
    for part in parts:
        yield from part.splitlines()
```

```python
# wrong: 函数调用返回生成器对象，不是 str。
def iter_names(users: Iterable[User]) -> str:
    for user in users:
        yield user.name

# wrong: return 会结束生成器，不会产出 users 中的元素。
def iter_users(users: Iterable[User]) -> Iterator[User]:
    yield fallback_user
    return users
```

#### `Generator`

- 只有调用方确实需要 `send()` 或生成器的最终返回值时，才使用完整的
`Generator[YieldType, SendType, ReturnType]` 类型：

```
received = yield emitted
    |               |
    |               +-- YieldType：生成器向外产出的类型
    +------------------ SendType：调用方通过 send() 送入的类型

return result
       |
       +-- ReturnType：生成器结束时返回的类型
```

- `ReturnType` 保存在 `StopIteration.value` 中，普通 `for` 循环会忽略它。
- 第一次启动生成器时没有暂停的 `yield` 可以接收值，因此必须使用
`next(generator)` 或 `generator.send(None)`；之后才能发送声明的类型。
- 不使用双向通信时，`Generator[T, None, None]` 虽然正确，但必须优先简化为
`Iterator[T]`。

```python
from collections.abc import Generator

def running_total() -> Generator[int, int, str]:
    total = 0
    increment = yield total

    while increment >= 0:
        total += increment
        increment = yield total

    return f"total={total}"

totals = running_total()
assert next(totals) == 0
assert totals.send(5) == 5
assert totals.send(2) == 7

try:
    totals.send(-1)
except StopIteration as error:
    assert error.value == "total=7"
```

#### 协程(coroutine)与 `Awaitable[T]`

- 不含 `yield` 的 `async def` 是协程函数。其返回注解必须写成 `-> T`，
表示 `await` 后得到 `T`。
- 禁止把普通 `async def` 标注为 `-> Awaitable[T]` ，除非等待后确实还会返回另一个可等待对象。
- 参数只要求可以 `await` 时，应当使用 `Awaitable[T]`，以接受协程、任务、
`Future` 和其他可等待对象。
- 只有需要表示协程对象本身，并使用其 `send()`、`throw()` 或 `close()` 能力
时，才使用 `Coroutine[YieldType, SendType, ReturnType]`。

```python
from collections.abc import Awaitable

async def fetch_user(user_id: str) -> User:
    return await storage.fetch_user(user_id)

async def wait_for_user(pending_user: Awaitable[User]) -> User:
    return await pending_user
```

#### `AsyncIterator`与`AsyncGenerator`

```
iter(value)             aiter(value)
next(iterator)          await anext(async_iterator)
for item in value       async for item in value
StopIteration           StopAsyncIteration
```

- `async def` 中含 `yield` 时，它是异步生成器函数，可以在两次产出之间
使用 `await`。
- 参数只需要 `async for` 时，必须优先使用 `AsyncIterable[T]`。
- 参数会调用 `anext()`、需要共享消费位置或操作当前异步游标时，必须使用
`AsyncIterator[T]`。
- 自定义异步可迭代对象的 `__aiter__()` 必须直接返回异步迭代器；
`__anext__()` 完成时产生 `T`，耗尽时抛出 `StopAsyncIteration`。
- 只产出值的异步生成器函数必须优先返回 `AsyncIterator[YieldType]`。

```python
from collections.abc import AsyncIterable, AsyncIterator

async def iter_events(
    source: AsyncIterable[RawEvent],
) -> AsyncIterator[Event]:
    async for raw_event in source:
        event = await parse_event(raw_event)
        if event is not None:
            yield event
```

- 需要 `asend()`、`athrow()` 或 `aclose()` 时，使用
`AsyncGenerator[YieldType, SendType]`。异步生成器不能 `return value`，因此没有 `ReturnType` 。
- 异步生成器不支持 `yield from`；转发其他异步可迭代对象时，必须显式使用
`async for` 并逐项 `yield`。

```python
from collections.abc import AsyncGenerator

async def event_channel() -> AsyncGenerator[Event, Command]:
    command = yield await load_initial_event()

    while command is not Command.STOP:
        command = yield await load_event(command)
```