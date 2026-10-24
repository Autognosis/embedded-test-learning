from contextlib import nullcontext

import pytest

from calc import add, clamp, div


@pytest.mark.parametrize(
    "a, b, outcome",
    [
        (1, 1, nullcontext(2)),
        ("a", "1", nullcontext("a1")),
        ("a", 1, pytest.raises(TypeError)),
    ],
)
def test_add(a, b, outcome):
    with outcome as expect_result:
        assert add(a, b) == expect_result


@pytest.mark.parametrize(
    "a, b, outcome",
    [
        (4, 2, nullcontext(2)),
        (3, 2, nullcontext(1.5)),
        (10, 0, pytest.raises(ZeroDivisionError, match="除数不能为 0")),
        ("a", "b", pytest.raises(TypeError, match="只接受数值类型")),
    ],
)
def test_div(a, b, outcome):
    with outcome as expect_result:
        assert div(a, b) == expect_result


@pytest.mark.parametrize(
    "a,b,c,outcome",
    [
        (5, 1, 4, nullcontext(4)),
        (-2, 1, 4, nullcontext(1)),
        (2, 1, 4, nullcontext(2)),
        (1, 1, 0, pytest.raises(ValueError, match="要求 low <= high")),
    ],
)
def test_clamp(a, b, c, outcome):
    with outcome as expect_result:
        assert clamp(a, b, c) == expect_result
