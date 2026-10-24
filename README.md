# Embedded Test Learning

这是我的嵌入式测试的自学笔记和相关代码的仓库。

## 1. Day1

### 1.1 UV 日常管理流程

```bash
uv init my-project        # 初始化项目
cd my-project

uv add requests fastapi   # 添加运行时依赖
uv add --dev pytest ruff  # 添加开发依赖

uv run main.py            # 运行项目，自动同步环境
uv run pytest             # 运行测试

uv sync                   # 拉代码后同步环境到 lock 文件状态
uv tree                   # 查看依赖树
uv remove requests        # 移除依赖
```

- 不手动编辑 `uv.lock`
- 尽量不用 `pip install` 混装，避免环境漂移

### 1.2 Github Token 更新

仅记录Windows环境下。

```bash
# 1. 在 ps/cmd 执行以下命令，打开 Windows 凭证管理器
control /name Microsoft.CredentialManager

# 2. 在 Windows 凭据中找到 github.com 相关项，并删除。

# 3. 在一个设置了 github 仓库作为远程仓库的仓库中执行
git push

# 4. 在弹出的提示框中选择 Token 登录，并粘贴新的Token
```

### 1.3 pytest 参数化与参数化处理异常

用 `nullcontext` 实现一个空的上下文处理器，统一了异常处理与非异常处理。

```python
from contextlib import nullcontext
import pytest


# 定义测试用例：每一组包含 (输入, 期望的行为上下文)
@pytest.mark.parametrize(
    "input, outcome",
    [
        (2, nullcontext(3)),  # 正常情况：期望结果是 3
        (0, pytest.raises(ZeroDivisionError)),  # 异常情况：期望抛出 ZeroDivisionError
        ("abc", pytest.raises(TypeError)),  # 异常情况：期望抛出 TypeError
    ],
)
def test_division(input, outcome):
    # outcome 是一个上下文管理器
    with outcome as expected_result:
        # 如果 outcome 是 nullcontext，expected_result 就是 nullcontext(3) 传入的值 3
        # 如果 outcome 是 pytest.raises，expected_result 是 ExceptionInfo 对象，这里用不上
        assert (6 / input) == expected_result
```

### 1.4 fixture 基础

#### 1. 直接返回值（无清理）

测试函数参数名与 fixture 函数名一致，pytest 会自动注入返回值。

```python
import pytest


@pytest.fixture
def sample_data():
    return {"user": "alice", "role": "admin"}


def test_role(sample_data):
    assert sample_data["role"] == "admin"
```

#### 2. yield 模式（有 setup 和 teardown）

`yield` 之前是 setup，之后是 teardown，适用于数据库连接、临时资源、浏览器实例等需要清理的场景。

```python
@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn  # 测试拿到 conn
    conn.close()  # 测试结束后清理
```

> **注意**：如果 fixture 在 `yield` 之前抛出异常，`yield` 之后的 teardown **不会执行**。需要“即使 setup 部分失败也要清理”时，可考虑 `request.addfinalizer()`，但多数情况下 `yield` 已经够用。
>

#### 3. 作用域（scope）：选对范围，避免重复和串数据

`scope` 决定 fixture 被创建和销毁的频率。

| scope | 创建频率 | 典型场景 |
| --- | --- | --- |
| `function`（默认） | 每个测试函数一次 | 测试数据、临时文件、独立的页面对象 |
| `class` | 每个测试类一次 | 类内共享的配置 |
| `module` | 每个模块一次 | 模块级数据库连接、只读配置 |
| `session` | 整个测试会话一次 | 全局配置、昂贵资源（浏览器、引擎） |

```python
@pytest.fixture(scope="session")
def config():
    return load_config()  # 全程只加载一次


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine()
    yield engine
    engine.dispose()
```

**执行顺序规则**：作用域大的先执行（`session → module → function`）；作用域相同时，被依赖的 fixture 先执行；无依赖且同作用域时按参数声明顺序执行；teardown 顺序与 setup 相反。

**一个常见选择原则**：昂贵、只读、可安全共享的资源用 `session`/`module`；需要隔离、可能被修改的状态用 `function`。官方反模式提醒：耗时资源如果每次测试都重新创建，是明显的性能浪费。

#### 4. 依赖注入：fixture 可以依赖 fixture

fixture 像测试一样，把另一个 fixture 名写在参数里即可。

```python
@pytest.fixture
def base_url():
    return "<https://api.example.com>"


@pytest.fixture
def api_client(base_url):
    return Client(base_url)


def test_health(api_client):
    assert api_client.get("/health").status_code == 200
```

好处是把复杂前置拆成可复用的小块，依赖关系显式化，而不是在一个 fixture 里堆砌所有步骤。
