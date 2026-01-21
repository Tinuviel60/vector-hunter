import pytest

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.components.collider import (
    BoxColliderComponent,
    CircleColliderComponent,
)
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.physics.collider_system import ColliderSystem


@pytest.mark.parametrize(
    "pos_a, pos_b, radius, expect_collision",
    [
        (Vector2D(0, 0), Vector2D(1.5, 0), 1.0, True),
        (Vector2D(0, 0), Vector2D(3.0, 0), 1.0, False),
    ],
)
def test_circle_circle_collision(pos_a, pos_b, radius, expect_collision):
    obj_a = GameObject("A")
    obj_b = GameObject("B")
    obj_a.transform.position = pos_a
    obj_b.transform.position = pos_b

    c1 = CircleColliderComponent(radius=radius)
    c2 = CircleColliderComponent(radius=radius)
    obj_a.add_component(c1)
    obj_b.add_component(c2)

    info = ColliderSystem.check_collision(c1, c2)
    assert (info is not None) is expect_collision


@pytest.mark.parametrize(
    "circle_pos, radius, expect_collision",
    [
        (Vector2D(1.5, 0), 1.0, True),
        (Vector2D(3.0, 0), 1.0, False),
    ],
)
def test_circle_box_collision(circle_pos, radius, expect_collision):
    obj_circle = GameObject("Circle")
    obj_box = GameObject("Box")
    obj_circle.transform.position = circle_pos
    obj_box.transform.position = Vector2D(0, 0)

    circle = CircleColliderComponent(radius=radius)
    box = BoxColliderComponent(width=2.0, height=2.0)
    obj_circle.add_component(circle)
    obj_box.add_component(box)

    info = ColliderSystem.check_collision(circle, box)
    assert (info is not None) is expect_collision


def test_aabb_overlap():
    system = ColliderSystem()
    a = (Vector2D(0, 0), Vector2D(2, 2))
    b = (Vector2D(1, 1), Vector2D(3, 3))
    assert system.aabb_overlap(a, b) is True
