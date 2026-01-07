import math
import pytest

from vect_hunt.core import Position2D
from vect_hunt.core import Vector2D


# --------------------
# Création & accès
# --------------------

def test_position_default_initialization():
    p = Position2D()
    assert p.x == 0.0
    assert p.y == 0.0

@pytest.mark.parametrize(
    "x, y",
    [
        (10, 10),
        (0, 0),
        (-49, 49),
        (-25, -25),
    ],
)
def test_position_initialization(x, y):
    p = Position2D(x, y)
    assert p.x == x
    assert p.y == y


# --------------------
# Setters
# --------------------
@pytest.mark.parametrize(
    "x, y",
    [
        (10, 10),
        (0, 0),
        (-49, 49),
        (-25, -25),
    ],
)
def test_set_position(x, y):
    p = Position2D()
    p.set_position(x, y)
    assert p.x == x
    assert p.y == y


# --------------------
# Distance
# --------------------
@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_distance",
    [
        (0, 0, 0, 0, 0.0),
        (1, 1, 4, 5, 5.0),
        (-1, -1, -4, -5, 5.0),
        (-2, -1, 1, 3, 5.0),
    ],
)
def test_distance_to(x1, y1, x2, y2, expected_distance):
    p1 = Position2D(x1, y1)
    p2 = Position2D(x2, y2)
    assert p1.distance_to(p2) == expected_distance

# --------------------
# Translation
# --------------------
@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_x, expected_y",
    [
        (0, 0, 0, 0, 0.0, 0.0),
        (1, 1, 4, 5, 5.0, 6.0),
        (-1, -1, -4, -5, -5.0, -6.0),
        (-2, -1, 1, 3, -1.0, 2.0),
    ],
)
def test_translate(x1, y1, x2, y2, expected_x, expected_y):
    p = Position2D(x1, y1)
    v = Vector2D(x2, y2)

    p.translate(v)

    assert p.x == expected_x
    assert p.y == expected_y

# --------------------
# Égalité
# --------------------
@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected",
    [
        (0.0, 0.0, 0.0, 0.0, True),
        (1.0, 2.0, 1.0, 2.0, True),
        (-1.0, -2.0, -1.0, -2.0, True),
        (1.0, 2.0, 2.0, 1.0, False),
        (1.0, 2.0, 1.0, 2.1, False),
        (1.0, 2.0, 1.1, 2.0, False),
        (1.0, 2.0, 1.1, 2.1, False),
        (1.000000001, 2.000000001, 1.000000002, 2.000000002, True),
    ],
)
def test_position_equality(x1, y1, x2, y2, expected):
    p1 = Position2D(x1, y1)
    p2 = Position2D(x2, y2)
    assert (p1 == p2) == expected