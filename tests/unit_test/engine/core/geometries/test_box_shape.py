import pytest
from vect_hunt.engine.core.geometries import BoxShape
from vect_hunt.engine.core.math import Vector2D


@pytest.mark.parametrize(
    "width, height",
    [
        (0.0, 1.0),
        (1.0, 0.0),
        (-1.0, 1.0),
        (1.0, -1.0),
    ],
)
def test_box_shape_invalid_dimensions(width, height):
    with pytest.raises(ValueError):
        BoxShape(width, height)


@pytest.mark.parametrize(
    "width, height, expected_area, expected_perimeter",
    [
        (2.0, 4.0, 8.0, 12.0),
        (1.5, 3.0, 4.5, 9.0),
    ],
)
def test_box_shape_area_perimeter(width, height, expected_area, expected_perimeter):
    shape = BoxShape(width, height)
    assert shape.area() == pytest.approx(expected_area)
    assert shape.perimeter() == pytest.approx(expected_perimeter)


@pytest.mark.parametrize(
    "width, height, expected_min, expected_max",
    [
        (2.0, 4.0, Vector2D(-1.0, -2.0), Vector2D(1.0, 2.0)),
        (1.0, 1.0, Vector2D(-0.5, -0.5), Vector2D(0.5, 0.5)),
    ],
)
def test_box_shape_aabb_local(width, height, expected_min, expected_max):
    shape = BoxShape(width, height)
    aabb_min, aabb_max = shape.aabb_local()
    assert aabb_min == expected_min
    assert aabb_max == expected_max


@pytest.mark.parametrize(
    "width, height, expected_vertices",
    [
        (
            2.0,
            4.0,
            [
                Vector2D(-1.0, -2.0),
                Vector2D(1.0, -2.0),
                Vector2D(1.0, 2.0),
                Vector2D(-1.0, 2.0),
            ],
        ),
        (
            1.0,
            1.0,
            [
                Vector2D(-0.5, -0.5),
                Vector2D(0.5, -0.5),
                Vector2D(0.5, 0.5),
                Vector2D(-0.5, 0.5),
            ],
        ),
    ],
)
def test_box_shape_local_vertices(width, height, expected_vertices):
    shape = BoxShape(width, height)
    assert shape.local_vertices() == expected_vertices


@pytest.mark.parametrize(
    "direction, expected",
    [
        (Vector2D(1.0, 1.0), Vector2D(1.0, 2.0)),
        (Vector2D(-1.0, 1.0), Vector2D(-1.0, 2.0)),
        (Vector2D(1.0, -1.0), Vector2D(1.0, -2.0)),
        (Vector2D(-1.0, -1.0), Vector2D(-1.0, -2.0)),
        (Vector2D(0.0, 0.0), Vector2D(1.0, 2.0)),
    ],
)
def test_box_shape_support(direction, expected):
    shape = BoxShape(2.0, 4.0)
    assert shape.support(direction) == expected


@pytest.mark.parametrize(
    "point, expected",
    [
        (Vector2D(0.0, 0.0), Vector2D(0.0, 0.0)),
        (Vector2D(2.0, 3.0), Vector2D(1.0, 2.0)),
        (Vector2D(-3.0, -1.0), Vector2D(-1.0, -1.0)),
        (Vector2D(0.5, -3.0), Vector2D(0.5, -2.0)),
    ],
)
def test_box_shape_closest_point_local(point, expected):
    shape = BoxShape(2.0, 4.0)
    assert shape.closest_point_local(point) == expected
