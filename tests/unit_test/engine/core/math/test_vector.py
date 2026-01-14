import math
import pytest
from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.core.transform.rotation import Rotation


# --------------------
# Magnitude & orientation
# --------------------
@pytest.mark.parametrize(
    "x, y, expected_magnitude",
    [(0, 0, 0.0), (-3, -4, 5.0), (3, 4, 5.0), (5, 12, 13.0), (8, 15, 17.0)],
)
def test_vector_magnitude(x, y, expected_magnitude):
    v = Vector2D(x, y)
    assert math.isclose(v.magnitude(), expected_magnitude)


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (0, 0, 0.0),
        (3, 4, 25.0),
        (5, 12, 169.0),
        (-3, -4, 25.0),
    ],
)
def test_magnitude_squared(x, y, expected):
    v = Vector2D(x, y)
    assert math.isclose(v.magnitude_squared(), expected)


@pytest.mark.parametrize(
    "x, y, expected_orientation",
    [
        (0, 0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, math.pi / 2),
        (-1.0, 0.0, math.pi),
        (0.0, -1.0, -math.pi / 2),
        (1.0, 1.0, math.pi / 4),
        (-1.0, 1.0, 3 * math.pi / 4),
    ],
)
def test_vector_orientation(x, y, expected_orientation):
    v = Vector2D(x, y)
    assert math.isclose(v.orientation(), expected_orientation)


# TODO : Test d'integration pour from_direction, à migrer en temps voulu
@pytest.mark.parametrize(
    "angle, x_expected, y_expected",
    [
        (0.0, 1.0, 0.0),
        (math.pi / 2, 0.0, 1.0),
        (math.pi, -1.0, 0.0),
        (-math.pi / 2, 0.0, -1.0),
        (math.pi / 4, math.sqrt(2) / 2, math.sqrt(2) / 2),
    ],
)
def test_vector_from_direction(angle, x_expected, y_expected):
    rotation = Rotation(angle)
    v = Vector2D.from_direction(rotation)
    # tolérance flottante raisonnable
    tol = 1e-9
    assert math.isclose(v.x, x_expected, abs_tol=tol)
    assert math.isclose(v.y, y_expected, abs_tol=tol)


# --------------------
# Normalisation
# --------------------
@pytest.mark.parametrize(
    "x, y, expected_magnitude, expected_old_magnitude",
    [(0, 0, 0.0, 0.0), (3, 4, 1.0, 5.0), (5, 12, 1.0, 13.0), (8, 15, 1.0, 17.0)],
)
def test_vector_normalized(x, y, expected_magnitude, expected_old_magnitude):
    v = Vector2D(x, y)
    vn = v.normalized()

    assert v is not vn
    assert math.isclose(vn.magnitude(), expected_magnitude)
    assert math.isclose(v.magnitude(), expected_old_magnitude)


@pytest.mark.parametrize(
    "x, y, expected_magnitude",
    [(0, 0, 0.0), (3, 4, 1.0), (5, 12, 1.0), (8, 15, 1.0)],
)
def test_vector_normalize(x, y, expected_magnitude):
    v = Vector2D(x, y)
    v.normalize()
    assert math.isclose(v.magnitude(), expected_magnitude)


@pytest.mark.parametrize(
    "x, y, expected_x, expected_y",
    [
        (1, 0, 0, 1),
        (0, 1, -1, 0),
        (-1, 0, 0, -1),
        (0, -1, 1, 0),
        (3, 4, -4, 3),
    ],
)
def test_vector_normal(x, y, expected_x, expected_y):
    v = Vector2D(x, y)
    n = v.normal()
    assert n == Vector2D(expected_x, expected_y)


# --------------------
# Produit scalaire
# --------------------
@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_dot_product",
    [
        (1, 2, 3, 4, 11.0),
        (-1, -2, -3, -4, 11.0),
        (1, -2, -3, 4, -11.0),
        (0, 0, 5, 7, 0.0),
        (5, 5, 10, 0, 50.0),
    ],
)
def test_dot_product(x1, y1, x2, y2, expected_dot_product):
    v1 = Vector2D(x1, y1)
    v2 = Vector2D(x2, y2)
    assert math.isclose(v1.dot(v2), expected_dot_product)


# --------------------
# Opérations algébriques
# --------------------
@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_x, expected_y",
    [
        (1, 2, 3, 4, 4, 6),
        (0, 0, 5, 7, 5, 7),
        (-1, -2, 1, 2, 0, 0),
        (10, -5, -3, 8, 7, 3),
    ],
)
def test_vector_addition(x1, y1, x2, y2, expected_x, expected_y):
    v1 = Vector2D(x1, y1)
    v2 = Vector2D(x2, y2)
    result = v1 + v2
    assert result == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_x, expected_y",
    [
        (5, 4, 3, 1, 2, 3),
        (10, 10, 5, 5, 5, 5),
        (0, 0, 1, 1, -1, -1),
        (-3, 7, -5, 2, 2, 5),
    ],
)
def test_vector_subtraction(x1, y1, x2, y2, expected_x, expected_y):
    v1 = Vector2D(x1, y1)
    v2 = Vector2D(x2, y2)
    result = v1 - v2
    assert result == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "x, y, scalar, expected_x, expected_y",
    [
        (2, -3, 2, 4, -6),
        (1, 1, 0, 0, 0),
        (5, 10, -1, -5, -10),
        (3, 4, 0.5, 1.5, 2),
    ],
)
def test_vector_scalar_multiplication(x, y, scalar, expected_x, expected_y):
    v = Vector2D(x, y)
    assert v * scalar == Vector2D(expected_x, expected_y)
    assert scalar * v == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "x, y, scalar, expected_x, expected_y",
    [
        (4, 6, 2, 2, 3),
        (10, -5, 5, 2, -1),
        (1, 1, 2, 0.5, 0.5),
        (9, 12, 3, 3, 4),
    ],
)
def test_vector_scalar_division(x, y, scalar, expected_x, expected_y):
    v = Vector2D(x, y)
    result = v / scalar
    assert result == Vector2D(expected_x, expected_y)


def test_vector_scalar_division_by_zero():
    v = Vector2D(1, 1)
    with pytest.raises(ValueError):
        _ = v / 0


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
def test_vector_equality(x1, y1, x2, y2, expected):
    v1 = Vector2D(x1, y1)
    v2 = Vector2D(x2, y2)
    assert (v1 == v2) == expected
