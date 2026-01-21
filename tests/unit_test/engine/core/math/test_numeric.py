import math
import random
import pytest

from vect_hunt.engine.core.math import Numeric


# -------------------
# clamp
# -------------------
@pytest.mark.parametrize(
    "value, min_v, max_v, expected",
    [
        (5, 0, 10, 5),
        (-1, 0, 10, 0),
        (12, 0, 10, 10),
        (0, 0, 10, 0),
        (10, 0, 10, 10),
        (-5, -10, -2, -5),
        (100, 50, 200, 100),
    ],
)
def test_clamp(value, min_v, max_v, expected):
    assert Numeric.clamp(value, min_v, max_v) == expected


# -------------------
# lerp / inverse_lerp / remap
# -------------------
@pytest.mark.parametrize(
    "a, b, t, expected",
    [
        (0.0, 10.0, 0.0, 0.0),
        (0.0, 10.0, 1.0, 10.0),
        (0.0, 10.0, 0.25, 2.5),
        (10.0, 0.0, 0.5, 5.0),
    ],
)
def test_lerp(a, b, t, expected):
    assert Numeric.lerp(a, b, t) == pytest.approx(expected)


def test_inverse_lerp():
    assert Numeric.inverse_lerp(0.0, 10.0, 2.5) == pytest.approx(0.25)
    assert Numeric.inverse_lerp(5.0, 5.0, 5.0) == 0.0


def test_remap():
    assert Numeric.remap(5.0, 0.0, 10.0, 0.0, 1.0) == pytest.approx(0.5)


# -------------------
# saturate / is_close / nearly_zero
# -------------------
@pytest.mark.parametrize("value, expected", [(1.2, 1.0), (-0.2, 0.0), (0.4, 0.4)])
def test_saturate(value, expected):
    assert Numeric.saturate(value) == pytest.approx(expected)


def test_is_close_nearly_zero():
    assert Numeric.is_close(0.1 + 0.2, 0.3, eps=1e-6)
    assert Numeric.nearly_zero(1e-8, eps=1e-6)


# -------------------
# sign / step / smoothstep
# -------------------
@pytest.mark.parametrize("value, expected", [(-2.0, -1), (0.0, 0), (3.0, 1)])
def test_sign(value, expected):
    assert Numeric.sign(value) == expected


@pytest.mark.parametrize("edge, value, expected", [(0.5, 0.3, 0.0), (0.5, 0.5, 1.0)])
def test_step(edge, value, expected):
    assert Numeric.step(edge, value) == expected


def test_smoothstep():
    assert Numeric.smoothstep(0.0, 1.0, -1.0) == 0.0
    assert Numeric.smoothstep(0.0, 1.0, 2.0) == 1.0
    assert Numeric.smoothstep(0.0, 1.0, 0.5) == pytest.approx(0.5)


# -------------------
# wrap / pingpong
# -------------------
@pytest.mark.parametrize(
    "value, min_v, max_v, expected",
    [
        (370.0, 0.0, 360.0, 10.0),
        (-10.0, 0.0, 360.0, 350.0),
        (0.0, 0.0, 360.0, 0.0),
    ],
)
def test_wrap(value, min_v, max_v, expected):
    assert Numeric.wrap(value, min_v, max_v) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value, length, expected",
    [
        (0.0, 1.0, 0.0),
        (0.5, 1.0, 0.5),
        (1.5, 1.0, 0.5),
        (2.5, 1.0, 0.5),
    ],
)
def test_pingpong(value, length, expected):
    assert Numeric.pingpong(value, length) == pytest.approx(expected)


# -------------------
# approach / damp
# -------------------
@pytest.mark.parametrize(
    "current, target, delta, expected",
    [
        (0.0, 10.0, 3.0, 3.0),
        (9.0, 10.0, 3.0, 10.0),
        (10.0, 0.0, 4.0, 6.0),
    ],
)
def test_approach(current, target, delta, expected):
    assert Numeric.approach(current, target, delta) == pytest.approx(expected)


def test_damp():
    value = Numeric.damp(0.0, 10.0, smoothing=5.0, dt=0.1)
    assert 0.0 < value < 10.0
    assert Numeric.damp(0.0, 10.0, smoothing=0.0, dt=0.1) == 10.0
    assert Numeric.damp(3.0, 10.0, smoothing=5.0, dt=0.0) == 3.0


# -------------------
# rand_range / rand_int
# -------------------
def test_rand_range():
    rng = random.Random(42)
    value = Numeric.rand_range(0.0, 1.0, rng=rng)
    assert 0.0 <= value <= 1.0


def test_rand_int():
    rng = random.Random(42)
    value = Numeric.rand_int(1, 6, rng=rng)
    assert 1 <= value <= 6
