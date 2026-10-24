"""calc — 极简计算工具模块（纯 Python，无第三方依赖）。"""

from numbers import Real

__all__ = ["add", "div", "clamp"]


def add(a, b):
    """返回 a + b。

    >>> add(1, 2)
    3
    """
    return a + b


def div(a, b):
    """返回 a / b（真除法，返回 float）。

    参数:
        a: 被除数
        b: 除数，不能为 0

    异常:
        ZeroDivisionError: 当 b 为 0 时。
        TypeError: 当 a 或 b 不是数值类型时。

    >>> div(6, 3)
    2.0
    """
    if not isinstance(a, Real) or not isinstance(b, Real):
        raise TypeError("div() 只接受数值类型，收到: %r, %r" % (a, b))
    if b == 0:
        raise ZeroDivisionError("div() 的除数不能为 0")
    return a / b


def clamp(x, low, high):
    """把 x 限制在 [low, high] 区间内并返回。

    参数:
        x: 待限制的值
        low: 下界
        high: 上界，必须 >= low

    异常:
        ValueError: 当 low > high 时。
        TypeError: 当参数不是数值类型时。

    >>> clamp(5, 0, 3)
    3
    >>> clamp(-1, 0, 3)
    0
    >>> clamp(2, 0, 3)
    2
    """
    if not all(isinstance(v, Real) for v in (x, low, high)):
        raise TypeError("clamp() 只接受数值类型")
    if low > high:
        raise ValueError("clamp() 要求 low <= high，收到 low=%r, high=%r" % (low, high))
    if x < low:
        return low
    if x > high:
        return high
    return x