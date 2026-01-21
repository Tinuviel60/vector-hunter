import pytest

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.scenes.scene import Scene
from vect_hunt.engine.physics.collision_resolution_system import (
    CollisionResolutionSystem,
)


@pytest.mark.parametrize(
    "kin_a, kin_b, expected_a, expected_b",
    [
        (False, False, Vector2D(1.0, 0.0), Vector2D(-1.0, 0.0)),
        (True, False, Vector2D(0.0, 0.0), Vector2D(-2.0, 0.0)),
        (False, True, Vector2D(2.0, 0.0), Vector2D(0.0, 0.0)),
    ],
)
def test_position_correction(kin_a, kin_b, expected_a, expected_b):
    scene = Scene(units={"pixels_per_meter": 100.0, "gravity_m_s2": 9.81})

    obj_a = GameObject("A")
    obj_b = GameObject("B")
    body_a = PhysicBodyComponent(is_kinematic=kin_a)
    body_b = PhysicBodyComponent(is_kinematic=kin_b)
    obj_a.add_component(body_a)
    obj_b.add_component(body_b)
    scene.add_game_object(obj_a)
    scene.add_game_object(obj_b)

    resolver = CollisionResolutionSystem(scene)
    info = {"normal": Vector2D(1, 0), "depth": 2.0}

    applied = resolver.update_from_collisions(
        [(obj_a.id, obj_b.id)], {(obj_a.id, obj_b.id): info}
    )

    assert applied is True
    assert obj_a.transform.position == expected_a
    assert obj_b.transform.position == expected_b


def test_no_correction_when_no_depth():
    scene = Scene(units={"pixels_per_meter": 100.0, "gravity_m_s2": 9.81})
    obj_a = GameObject("A")
    obj_b = GameObject("B")
    obj_a.add_component(PhysicBodyComponent())
    obj_b.add_component(PhysicBodyComponent())
    scene.add_game_object(obj_a)
    scene.add_game_object(obj_b)

    resolver = CollisionResolutionSystem(scene)
    info = {"normal": Vector2D(1, 0), "depth": 0.0}

    applied = resolver.update_from_collisions(
        [(obj_a.id, obj_b.id)], {(obj_a.id, obj_b.id): info}
    )

    assert applied is False
    assert obj_a.transform.position == Vector2D(0.0, 0.0)
    assert obj_b.transform.position == Vector2D(0.0, 0.0)
