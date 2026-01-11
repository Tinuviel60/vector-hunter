import math
import pytest
from vect_hunt.core import Vector2D
from vect_hunt.core.rotation import Rotation


# --------------------
# Initialisation
# --------------------
@pytest.mark.parametrize(
    "angle, expected_m00, expected_m01, expected_m10, expected_m11",
    [
        (0.0, 1.0, -0.0, 0.0, 1.0),
        (math.pi / 2, 0.0, -1.0, 1.0, 0.0),
        (math.pi, -1.0, -0.0, 0.0, -1.0),
        (-math.pi / 2, 0.0, 1.0, -1.0, 0.0),
        (2 * math.pi, 1.0, -0.0, 0.0, 1.0),  # rotation complète
        (-2 * math.pi, 1.0, -0.0, 0.0, 1.0),  # rotation complète négative
        (10 * math.pi, 1.0, -0.0, 0.0, 1.0),  # multiple rotation positive
        (-15 * math.pi, -1.0, -0.0, 0.0, -1.0),  # multiple rotation négative
        (1e-9, 1.0, -1e-9, 1e-9, 1.0),  # angle très petit
    ],
)
def test_rotation_initialization(
    angle, expected_m00, expected_m01, expected_m10, expected_m11
):
    rot = Rotation(angle)
    tol = 1e-9
    assert math.isclose(rot.m00, expected_m00, abs_tol=tol)
    assert math.isclose(rot.m01, expected_m01, abs_tol=tol)
    assert math.isclose(rot.m10, expected_m10, abs_tol=tol)
    assert math.isclose(rot.m11, expected_m11, abs_tol=tol)


# --------------------
# Application sur vecteur
# --------------------
@pytest.mark.parametrize(
    "angle, vec_x, vec_y, expected_x, expected_y",
    [
        (0.0, 1, 0, 1, 0),
        (math.pi / 2, 1, 0, 0, 1),
        (math.pi, 1, 0, -1, 0),
        (-math.pi / 2, 0, 1, 1, 0),
        (math.pi / 4, 1, 0, math.sqrt(2) / 2, math.sqrt(2) / 2),
    ],
)
def test_rotation_apply(angle, vec_x, vec_y, expected_x, expected_y):
    rot = Rotation(angle)
    v = Vector2D(vec_x, vec_y)
    result = rot.apply(v)
    tol = 1e-9
    assert math.isclose(result.x, expected_x, abs_tol=tol)
    assert math.isclose(result.y, expected_y, abs_tol=tol)


# --------------------
# Rotation inverse
# --------------------
@pytest.mark.parametrize(
    "angle, vec_x, vec_y",
    [
        (0.0, 1, 1),
        (math.pi / 2, 2, 0),
        (math.pi, -1, 3),
        (math.pi / 4, 1, 0),
    ],
)
def test_rotation_inverse(angle, vec_x, vec_y):
    rot = Rotation(angle)
    inv = rot.inverse()
    v = Vector2D(vec_x, vec_y)

    # Appliquer rot puis son inverse doit retrouver le vecteur initial
    result = inv.apply(rot.apply(v))
    tol = 1e-9
    assert math.isclose(result.x, v.x, abs_tol=tol)
    assert math.isclose(result.y, v.y, abs_tol=tol)


# --------------------
# Composition de rotations
# --------------------
@pytest.mark.parametrize(
    "angle1, angle2, vec_x, vec_y",
    [
        (0.0, math.pi / 2, 1, 0),
        (math.pi / 4, math.pi / 4, 1, 0),
        (math.pi / 2, math.pi / 2, 0, 1),
    ],
)
def test_rotation_compose(angle1, angle2, vec_x, vec_y):
    rot1 = Rotation(angle1)
    rot2 = Rotation(angle2)
    composed = rot1.compose(rot2)
    v = Vector2D(vec_x, vec_y)

    # Appliquer rot2 puis rot1 devrait être équivalent à composed
    expected = rot1.apply(rot2.apply(v))
    result = composed.apply(v)
    tol = 1e-9
    assert math.isclose(result.x, expected.x, abs_tol=tol)
    assert math.isclose(result.y, expected.y, abs_tol=tol)


# --------------------
# Conversion en angle
# --------------------
@pytest.mark.parametrize(
    "angle",
    [
        0.0,
        math.pi / 2,
        math.pi,
        -math.pi / 2,
        math.pi / 4,
        -math.pi / 4,
    ],
)
def test_rotation_to_angle(angle):
    rot = Rotation(angle)
    tol = 1e-9
    # La conversion en angle doit retrouver l'angle initial à tolérance près
    assert math.isclose(rot.to_angle(), angle, abs_tol=tol)
