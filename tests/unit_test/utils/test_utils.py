import math
import pytest
import random

from vect_hunt.utils.numeric import (
    hex_to_rgb,
    clamp,
    normalize,
    normalize_ratio,
    normalize_log,
    normalize_ratio_log,
    exponential_scale,
    gaussian_between,
)


# -------------------
# hex_to_rgb
# -------------------
@pytest.mark.parametrize(
    "hex_color, expected",
    [
        ("#FF0000", (255, 0, 0)),
        ("00FF00", (0, 255, 0)),
        ("0000FF", (0, 0, 255)),
        ("123456", (18, 52, 86)),
    ],
)
def test_hex_to_rgb_valid(hex_color, expected):
    assert hex_to_rgb(hex_color) == expected


@pytest.mark.parametrize("invalid_hex", ["#FFF", "GGHHII", "12345", "ZZZZZZ"])
def test_hex_to_rgb_invalid_raises(invalid_hex):
    with pytest.raises(ValueError):
        hex_to_rgb(invalid_hex)


# -------------------
# clamp
# -------------------
@pytest.mark.parametrize(
    "value, min_v, max_v, expected",
    [
        (5, 0, 10, 5),  # valeur dans la plage
        (-1, 0, 10, 0),  # en dessous du min
        (12, 0, 10, 10),  # au dessus du max
        (0, 0, 10, 0),  # exactement au min
        (10, 0, 10, 10),  # exactement au max
        (-5, -10, -2, -5),  # valeurs négatives
        (100, 50, 200, 100),  # grandes valeurs
    ],
)
def test_clamp(value, min_v, max_v, expected):
    assert clamp(value, min_v, max_v) == expected


# -------------------
# normalize
# -------------------
@pytest.mark.parametrize(
    "value, min_v, max_v, cap, expected",
    [
        (5, 0, 10, True, 0.5),
        (-5, 0, 10, True, 0.0),
        (15, 0, 10, True, 1.0),
        (5, 0, 10, False, 0.5),
        (-5, 0, 10, False, -0.5),
        (15, 0, 10, False, 1.5),
        (0, 0, 0, True, 0.0),  # max == min
    ],
)
def test_normalize(value, min_v, max_v, cap, expected):
    assert normalize(value, min_v, max_v, cap) == pytest.approx(expected)


# -------------------
# normalize_ratio
# -------------------
@pytest.mark.parametrize(
    "v1, v2, expected",
    [
        (1, 1, 0.5),
        (0, 0, 0.5),
        (3, 1, 0.75),
        (1, 3, 0.25),
        (0, 5, 0.0),
        (5, 0, 1.0),
    ],
)
def test_normalize_ratio(v1, v2, expected):
    assert normalize_ratio(v1, v2) == pytest.approx(expected)


# -------------------
# normalize_log
# -------------------
@pytest.mark.parametrize(
    "value, min_v, max_v, cap, expected_min, expected_max",
    [
        (5, 0, 10, True, 0.0, 1.0),  # valeur dans la plage avec cap
        (-5, 0, 10, True, 0.0, 1.0),  # valeur négative avec cap
        (15, 0, 10, True, 0.0, 1.0),  # valeur au dessus avec cap
        (5, 0, 10, False, 0.0, None),  # sans cap, juste >= 0
        (-5, 0, 10, False, 0.0, None),  # valeur négative sans cap
        (15, 0, 10, False, 0.0, None),  # valeur au dessus sans cap
        (0, 0, 0, True, 0.0, 1.0),  # min == max
    ],
)
def test_normalize_log(value, min_v, max_v, cap, expected_min, expected_max):
    result = normalize_log(value, min_v, max_v, cap)
    assert result >= expected_min
    if expected_max is not None:
        assert result <= expected_max


# -------------------
# normalize_ratio_log
# -------------------
@pytest.mark.parametrize(
    "v1, v2",
    [
        (0, 0),
        (1, 1),
        (0, 5),
        (5, 0),
        (3, 1),
        (1, 3),
    ],
)
def test_normalize_ratio_log(v1, v2):
    ratio = normalize_ratio_log(v1, v2)
    assert 0.0 <= ratio <= 1.0
    if v1 == v2 == 0:
        assert ratio == 0.5


# -------------------
# exponential_scale
# -------------------
@pytest.mark.parametrize(
    "value, threshold, rate",
    [
        (0.5, 1.0, 1.5),  # en dessous du seuil
        (1.0, 1.0, 1.5),  # exactement au seuil
        (1.5, 1.0, 1.5),  # au dessus du seuil
        (2.0, 1.0, 2.0),  # au dessus avec rate différent
        (0.0, 1.0, 1.5),  # valeur zéro
        (3.0, 2.0, 3.0),  # grands écarts
    ],
)
def test_exponential_scale(value, threshold, rate):
    result = exponential_scale(value, threshold, rate)
    if value <= threshold:
        assert result == 0.0
    else:
        # Vérifie que le résultat est positif et cohérent avec la formule exponentielle
        assert result > 0.0
        # Plus value est grand par rapport au seuil, plus le résultat devrait être grand
        if value > threshold + 1:
            result2 = exponential_scale(threshold + 0.1, threshold, rate)
            assert result > result2


# -------------------
# gaussian_between
# -------------------
@pytest.mark.parametrize(
    "low, high, num_samples",
    [
        (0.0, 1.0, 100),
        (-1.0, 1.0, 100),
        (10.0, 20.0, 100),
        (5.0, 5.0, 1),  # cas limite : low == high
    ],
)
def test_gaussian_between_range(low, high, num_samples):
    rng = random.Random(42)  # seed fixe pour test reproductible

    for _ in range(num_samples):
        value = gaussian_between(low, high, rng=rng)
        assert low <= value <= high


def test_gaussian_between_distribution():
    """
    Teste que la distribution est bien centrée autour de la moyenne.
    """
    rng = random.Random(42)
    low, high = 0.0, 100.0
    samples = [gaussian_between(low, high, rng=rng) for _ in range(1000)]

    mean = sum(samples) / len(samples)
    expected_mean = (low + high) / 2

    # La moyenne devrait être proche du centre avec une certaine tolérance
    assert abs(mean - expected_mean) < 10  # tolérance de 10% de la plage


import os
