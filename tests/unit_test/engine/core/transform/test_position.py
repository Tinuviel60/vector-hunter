import pytest

from vect_hunt.engine.core import Position2D
from vect_hunt.engine.core import Vector2D


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


@pytest.mark.parametrize(
    "x1, y1, dx, dy, expected_x, expected_y",
    [
        (0, 0, 5, 10, 5, 10),
        (10, 20, -5, -10, 5, 10),
        (-5, 5, 10, -5, 5, 0),
    ],
)
def test_translated(x1, y1, dx, dy, expected_x, expected_y):
    p = Position2D(x1, y1)
    v = Vector2D(dx, dy)

    p_new = p.translated(v)

    # Vérifie que l'original n'a pas changé
    assert p.x == x1
    assert p.y == y1

    # Vérifie la nouvelle position
    assert p_new.x == expected_x
    assert p_new.y == expected_y


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
