import math
import pytest
from vect_hunt.core import Vector2D, Transform
from vect_hunt.core import Collider, BoxCollider, CircleCollider


# --------------------
# Classe minimale pour simuler un GameObject parent
# --------------------
class DummyGameObject:
    """Classe minimale simulant un GameObject pour les tests unitaires."""

    pass


# --------------------
# Tests unitaires de Collider
# --------------------
def test_collider_initialization():
    parent = DummyGameObject()
    transform = Transform(Vector2D(1, 2), 0.5)
    collider = Collider(parent, transform, solid=False)  # type: ignore

    assert collider.parent is parent
    assert collider.transform == transform
    assert collider.solid is False


def test_collider_geometry_not_implemented():
    parent = DummyGameObject()
    collider = Collider(parent)  # type: ignore

    with pytest.raises(NotImplementedError):
        collider.get_geometry()


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
    box = BoxCollider(
        parent, width, height, center, orientation, solid=True  # type: ignore
    )

    assert box.width == width
    assert box.height == height
    assert box.transform.position == center
    assert math.isclose(box.transform.rotation.to_angle(), orientation)
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
    box = BoxCollider(parent, width, height)  # type: ignore
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
    box = BoxCollider(parent, width, height, center, orientation)  # type: ignore
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
    circle = CircleCollider(parent, center, radius, solid=solid)  # type: ignore

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
    circle = CircleCollider(parent, radius=radius)  # type: ignore
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
    circle = CircleCollider(parent, center, radius)  # type: ignore
    geo = circle.get_geometry()

    assert geo["type"] == "circle"
    assert geo["center"] == center
    assert geo["radius"] == radius


# --------------------
# Tests limites combinés pour BoxCollider et CircleCollider
# --------------------
@pytest.mark.parametrize(
    "width, height, radius",
    [
        (0, 0, 0),
        (1, 1, 1),
        (100, 50, 25),
        (1e-6, 1e-6, 1e-6),
        (1e6, 1e6, 1e6),
    ],
)
def test_colliders_with_extreme_values(width, height, radius):
    parent = DummyGameObject()
    box = BoxCollider(parent, width, height)  # type: ignore
    circle = CircleCollider(parent, radius=radius)  # type: ignore

    # Aire correcte
    assert math.isclose(box.get_area(), width * height)
    assert math.isclose(circle.get_area(), math.pi * radius**2)

    # Géométrie correcte
    geo_box = box.get_geometry()
    geo_circle = circle.get_geometry()
    assert geo_box["type"] == "box"
    assert len(geo_box["points"]) == 4
    assert geo_circle["type"] == "circle"
    assert geo_circle["radius"] == radius
