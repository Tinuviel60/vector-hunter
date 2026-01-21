import pytest

from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.components.collider import (
    CircleColliderComponent,
    ColliderComponent,
)


@pytest.mark.parametrize(
    "radius, center_x, center_y, solid",
    [
        (5, 0, 0, True),
        (3, 1, 1, False),
        (10, -2, 4, True),
        (1e-6, 0, 0, True),
    ],
)
def test_circle_collider_initialization(radius, center_x, center_y, solid):
    center = Vector2D(center_x, center_y)
    circle = CircleColliderComponent(center=center, radius=radius, solid=solid)

    assert isinstance(circle, ColliderComponent)
    assert circle.shape.radius == pytest.approx(radius)
    assert circle.transform.position == center
    assert circle.solid is solid
