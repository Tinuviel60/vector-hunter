import math
import pytest
from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.physics import (
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderComponent,
)


# --------------------
# Classe minimale pour simuler un GameObject parent
# --------------------
class DummyGameObject:
    """Classe minimale simulant un GameObject pour les tests unitaires."""

    pass


# --------------------
# Tests unitaires de Collider
# --------------------
def test_collider_geometry_not_implemented():
    parent = DummyGameObject()
    with pytest.raises(TypeError):
        ColliderComponent(parent)  # type: ignore


# --------------------
# Tests unitaires de BoxCollider
# --------------------
@pytest.mark.parametrize(
    "width, height, center_x, center_y, orientation",
    [
        (10, 5, 0, 0, 0),
        (4, 4, 1, -1, math.pi / 2),
        (2, 8, -2, 3, math.pi / 4),
        (0, 5, 0, 0, 0),  # largeur nulle
        (5, 0, 0, 0, 0),  # hauteur nulle
    ],
)
def test_box_collider_initialization(width, height, center_x, center_y, orientation):
    parent = DummyGameObject()
    center = Vector2D(center_x, center_y)
    box = BoxColliderComponent(
        parent, width, height, center, orientation, solid=True  # type: ignore
    )

    assert box.width == width
    assert box.height == height
    assert box.transform.position == center
    assert math.isclose(box.transform.rotation.angle, orientation)
    assert box.solid is True
    assert len(box.corners) == 4
    for corner in box.corners:
        assert isinstance(corner, Vector2D)


@pytest.mark.parametrize(
    "width, height, expected_area",
    [
        (10, 5, 50),
        (4, 4, 16),
        (2, 8, 16),
        (0, 5, 0),  # largeur nulle
        (5, 0, 0),  # hauteur nulle
    ],
)
def test_box_collider_area(width, height, expected_area):
    parent = DummyGameObject()
    box = BoxColliderComponent(parent, width, height)  # type: ignore
    assert math.isclose(box.get_area(), expected_area)


@pytest.mark.parametrize(
    "width, height, center_x, center_y, orientation",
    [
        (10, 5, 0, 0, 0),
        (4, 4, 1, -1, math.pi / 2),
        (2, 8, -2, 3, math.pi / 4),
    ],
)
def test_box_collider_geometry_returns_polygon(
    width, height, center_x, center_y, orientation
):
    parent = DummyGameObject()
    center = Vector2D(center_x, center_y)
    box = BoxColliderComponent(parent, width, height, center, orientation)  # type: ignore
    geo = box.get_geometry()

    assert geo["type"] == "box"
    assert len(geo["points"]) == 4
    for point in geo["points"]:
        assert isinstance(point, Vector2D)


# --------------------
# Tests unitaires de CircleCollider
# --------------------
@pytest.mark.parametrize(
    "radius, center_x, center_y, solid",
    [
        (5, 0, 0, True),
        (3, 1, 1, False),
        (10, -2, 4, True),
        (0, 0, 0, True),  # rayon nul
        (1e-6, 0, 0, True),  # très petit rayon
    ],
)
def test_circle_collider_initialization(radius, center_x, center_y, solid):
    parent = DummyGameObject()
    center = Vector2D(center_x, center_y)
    circle = CircleColliderComponent(parent, center, radius, solid=solid)  # type: ignore

    assert circle.radius == radius
    assert circle.transform.position == center
    assert circle.solid == solid


@pytest.mark.parametrize(
    "radius, expected_area",
    [
        (1, math.pi),
        (2, math.pi * 4),
        (3, math.pi * 9),
        (0, 0),  # rayon nul
        (1e-6, math.pi * 1e-12),  # très petit rayon
    ],
)
def test_circle_collider_area(radius, expected_area):
    parent = DummyGameObject()
    circle = CircleColliderComponent(parent, radius=radius)  # type: ignore
    assert math.isclose(circle.get_area(), expected_area)


@pytest.mark.parametrize(
    "radius, center_x, center_y",
    [
        (5, 0, 0),
        (3, 1, 1),
        (10, -2, 4),
    ],
)
def test_circle_collider_geometry_returns_circle(radius, center_x, center_y):
    parent = DummyGameObject()
    center = Vector2D(center_x, center_y)
    circle = CircleColliderComponent(parent, center, radius)  # type: ignore
    geo = circle.get_geometry()

    assert geo["type"] == "circle"
    assert geo["center"] == center
    assert geo["radius"] == radius
