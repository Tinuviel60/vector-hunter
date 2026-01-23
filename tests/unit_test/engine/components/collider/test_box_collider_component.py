import math

import pytest
from vect_hunt.engine.components.collider import BoxColliderComponent, ColliderComponent
from vect_hunt.engine.core import Vector2D


@pytest.mark.parametrize(
    "width, height, center_x, center_y, orientation, solid",
    [
        (10, 5, 0, 0, 0.0, True),
        (4, 4, 1, -1, math.pi / 2, False),
        (2, 8, -2, 3, math.pi / 4, True),
    ],
)
def test_box_collider_initialization(
    width, height, center_x, center_y, orientation, solid
):
    center = Vector2D(center_x, center_y)
    box = BoxColliderComponent(
        width=width,
        height=height,
        center=center,
        orientation=orientation,
        solid=solid,
    )

    assert isinstance(box, ColliderComponent)
    assert box.shape.width == width
    assert box.shape.height == height
    assert box.transform.position == center
    assert math.isclose(box.transform.rotation.angle, orientation)
    assert box.solid is solid
