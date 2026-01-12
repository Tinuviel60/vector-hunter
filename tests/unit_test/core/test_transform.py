import math
import pytest
from vect_hunt.core import Transform, Vector2D


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


# --------------------
# Vecteurs directionnels
# --------------------
@pytest.mark.parametrize(
    "rotation, expected_forward, expected_right, expected_behind, expected_left",
    [
        (0.0, (0.0, 1.0), (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0)),
        (math.pi / 2, (-1.0, 0.0), (0.0, 1.0), (1.0, 0.0), (0.0, -1.0)),
        (math.pi, (0.0, -1.0), (-1.0, 0.0), (0.0, 1.0), (1.0, 0.0)),
        (-math.pi / 2, (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0), (0.0, 1.0)),
    ],
)
def test_transform_directions(
    rotation, expected_forward, expected_right, expected_behind, expected_left
):
    t = Transform(rotation=rotation)
    
    forward = t.forward()
    right = t.right()
    behind = t.behind()
    left = t.left()
    
    # Vérifie forward
    assert math.isclose(forward.x, expected_forward[0], abs_tol=1e-9)
    assert math.isclose(forward.y, expected_forward[1], abs_tol=1e-9)
    
    # Vérifie right
    assert math.isclose(right.x, expected_right[0], abs_tol=1e-9)
    assert math.isclose(right.y, expected_right[1], abs_tol=1e-9)
    
    # Vérifie behind
    assert math.isclose(behind.x, expected_behind[0], abs_tol=1e-9)
    assert math.isclose(behind.y, expected_behind[1], abs_tol=1e-9)
    
    # Vérifie left
    assert math.isclose(left.x, expected_left[0], abs_tol=1e-9)
    assert math.isclose(left.y, expected_left[1], abs_tol=1e-9)
    
    # Vérifie que forward et behind sont opposés
    assert math.isclose(forward.x, -behind.x, abs_tol=1e-9)
    assert math.isclose(forward.y, -behind.y, abs_tol=1e-9)
    
    # Vérifie que right et left sont opposés
    assert math.isclose(right.x, -left.x, abs_tol=1e-9)
    assert math.isclose(right.y, -left.y, abs_tol=1e-9)
    
    # Vérifie que forward et right sont perpendiculaires (dot product = 0)
    dot = forward.x * right.x + forward.y * right.y
    assert math.isclose(dot, 0.0, abs_tol=1e-9)
