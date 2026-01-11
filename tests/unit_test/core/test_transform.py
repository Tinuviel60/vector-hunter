import math
import pytest
from vect_hunt.core import Transform, Vector2D


# --------------------
# Création & accès
# --------------------


def test_transform_default_initialization():
    transform = Transform()
    assert transform.position.x == 0.0
    assert transform.position.y == 0.0
    assert transform.rotation.to_angle() == 0.0


@pytest.mark.parametrize(
    "x, y, rotation",
    [
        (10, 10, 0),
        (0, 0, 1),
        (-49, 49, -3),
        (-25, -25, -3),
    ],
)
def test_transform_custom_initialization(x, y, rotation):
    transform = Transform(Vector2D(x, y), rotation)
    assert transform.position == Vector2D(x, y)
    assert transform.position.x == x
    assert transform.position.y == y
    assert transform.rotation.to_angle() == rotation


# --------------------
# Deplacement
# --------------------
@pytest.mark.parametrize(
    "x, y, dx, dy, expected_x, expected_y",
    [
        (0, 0, 5, 5, 5, 5),
        (10, 10, -5, -5, 5, 5),
        (-10, -10, 10, 10, 0, 0),
        (3.5, 2.5, 1.5, -0.5, 5.0, 2.0),
        (0, 0, 0, 0, 0, 0),
    ],
)
def test_transform_move(x, y, dx, dy, expected_x, expected_y):
    transform = Transform(Vector2D(x, y), 0)
    transform.move(Vector2D(dx, dy))
    assert transform.position == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "x, y, new_x, new_y",
    [
        (0, 0, 5, 5),
        (10, 10, -5, -5),
        (-10, -10, 0, 0),
        (3.5, 2.5, 1.5, -0.5),
        (0, 0, 0, 0),
    ],
)
def test_transform_translate(x, y, new_x, new_y):
    transform = Transform(Vector2D(x, y), 0)
    transform.translate(Vector2D(new_x, new_y))
    assert transform.position == Vector2D(new_x, new_y)


# --------------------
# Rotation
# --------------------
@pytest.mark.parametrize(
    "orientation, delta, expected_orientation",
    [
        (0.0, 0.0, 0.0),
        (3.0, 4.0, 0.7168146928204138),
        (5.0, 12.0, -1.8495559215387587),
        (15.0, 8.0, -2.132741228718345),
        (-math.pi, -math.pi / 2, math.pi / 2),
        (math.pi, math.pi / 2, -math.pi / 2),
        (math.pi / 2, math.pi, -math.pi / 2),
        (-math.pi / 2, -math.pi, math.pi / 2),
    ],
)
def test_transform_rotate(orientation, delta, expected_orientation):
    transform = Transform(rotation=orientation)
    transform.rotate(delta)
    assert math.isclose(
        transform.rotation.to_angle(), expected_orientation, rel_tol=1e-9
    )


@pytest.mark.parametrize(
    "rotation, expected_rotation",
    [
        (0.0, 0.0),
        (3.0, 3.0),
        (5.0, -1.2831853071795862),
        (-15.0, -2.4336293856408275),
        (8, 1.7168146928204138),
    ],
)
def test_transform_set_rotation(rotation, expected_rotation):
    transform = Transform()
    transform.set_rotation(rotation)
    assert math.isclose(transform.rotation.to_angle(), expected_rotation, rel_tol=1e-9)
