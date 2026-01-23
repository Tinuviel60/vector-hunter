import pytest
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.physics.external_forces_system import ExternalForcesSystem
from vect_hunt.engine.scenes.scene import Scene


@pytest.mark.parametrize(
    "use_gravity, is_kinematic, expected_y",
    [
        (True, False, 981.0),
        (False, False, 0.0),
        (True, True, 0.0),
    ],
)
def test_apply_gravity(use_gravity, is_kinematic, expected_y):
    scene = Scene(units={"pixels_per_meter": 100.0, "gravity_m_s2": 9.81})
    obj = GameObject("Body")
    body = PhysicBodyComponent(use_gravity=use_gravity, is_kinematic=is_kinematic)
    obj.add_component(body)
    scene.add_game_object(obj)

    ExternalForcesSystem.apply_gravity(scene, 0.016)

    assert body.acceleration == Vector2D(0.0, expected_y)
