import math
import pytest

from vect_hunt.engine.core.geometries import CircleShape
from vect_hunt.engine.core.math import Vector2D


@pytest.mark.parametrize("radius", [0.0, -1.0, -0.5])
def test_circle_shape_invalid_radius(radius):
    with pytest.raises(ValueError):
        CircleShape(radius)


@pytest.mark.parametrize(
    "radius, expected_area, expected_perimeter",
    [
        (1.0, math.pi, 2.0 * math.pi),
        (2.0, 4.0 * math.pi, 4.0 * math.pi),
    ],
)
def test_circle_shape_area_perimeter(radius, expected_area, expected_perimeter):
    shape = CircleShape(radius)
    assert shape.area() == pytest.approx(expected_area)
    assert shape.perimeter() == pytest.approx(expected_perimeter)


@pytest.mark.parametrize(
    "radius, expected_min, expected_max",
    [
        (1.0, Vector2D(-1.0, -1.0), Vector2D(1.0, 1.0)),
        (2.5, Vector2D(-2.5, -2.5), Vector2D(2.5, 2.5)),
    ],
)
def test_circle_shape_aabb_local(radius, expected_min, expected_max):
    shape = CircleShape(radius)
    aabb_min, aabb_max = shape.aabb_local()
    assert aabb_min == expected_min
    assert aabb_max == expected_max


@pytest.mark.parametrize(
    "direction, expected",
    [
        (Vector2D(1.0, 0.0), Vector2D(2.0, 0.0)),
        (Vector2D(0.0, 1.0), Vector2D(0.0, 2.0)),
        (Vector2D(0.0, 0.0), Vector2D(2.0, 0.0)),
    ],
)
def test_circle_shape_support(direction, expected):
    shape = CircleShape(2.0)
    result = shape.support(direction)
    assert result == expected


@pytest.mark.parametrize(
    "point, expected",
    [
        (Vector2D(0.0, 0.0), Vector2D(0.0, 0.0)),
        (Vector2D(1.0, 0.0), Vector2D(1.0, 0.0)),
        (Vector2D(3.0, 0.0), Vector2D(2.0, 0.0)),
        (Vector2D(0.0, -3.0), Vector2D(0.0, -2.0)),
    ],
)
def test_circle_shape_closest_point_local(point, expected):
    shape = CircleShape(2.0)
    result = shape.closest_point_local(point)
    assert result == expected
