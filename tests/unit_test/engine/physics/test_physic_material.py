import pytest

from vect_hunt.engine.physics.physic_material import CombineMode, PhysicMaterial


@pytest.mark.parametrize(
    "friction, restitution, linear_damping, bounciness_threshold, expected",
    [
        (-0.2, 0.5, 0.1, 10.0, (0.0, 0.5, 0.1, 10.0)),
        (1.2, 0.5, 0.1, 10.0, (1.0, 0.5, 0.1, 10.0)),
        (0.2, -0.5, 0.1, 10.0, (0.2, 0.0, 0.1, 10.0)),
        (0.2, 1.5, 0.1, 10.0, (0.2, 1.0, 0.1, 10.0)),
        (0.2, 0.5, -0.1, 10.0, (0.2, 0.5, 0.0, 10.0)),
        (0.2, 0.5, 1.2, 10.0, (0.2, 0.5, 1.0, 10.0)),
        (0.2, 0.5, 0.1, -1.0, (0.2, 0.5, 0.1, 0.0)),
    ],
)
def test_physic_material_clamps_values(
    friction,
    restitution,
    linear_damping,
    bounciness_threshold,
    expected,
):
    material = PhysicMaterial(
        friction=friction,
        restitution=restitution,
        linear_damping=linear_damping,
        bounciness_threshold=bounciness_threshold,
    )

    assert material.friction == expected[0]
    assert material.restitution == expected[1]
    assert material.linear_damping == expected[2]
    assert material.bounciness_threshold == expected[3]


@pytest.mark.parametrize(
    "mode_a, mode_b, expected",
    [
        (CombineMode.MIN, CombineMode.MAX, CombineMode.MAX),
        (CombineMode.AVERAGE, CombineMode.MIN, CombineMode.AVERAGE),
        (CombineMode.MULTIPLY, CombineMode.AVERAGE, CombineMode.MULTIPLY),
        (CombineMode.MAX, CombineMode.MAX, CombineMode.MAX),
    ],
)
def test_resolve_combine_mode(mode_a, mode_b, expected):
    assert PhysicMaterial.resolve_combine_mode(mode_a, mode_b) == expected


@pytest.mark.parametrize(
    "value_a, value_b, mode, expected",
    [
        (0.2, 0.8, CombineMode.MIN, 0.2),
        (0.2, 0.8, CombineMode.MAX, 0.8),
        (0.2, 0.8, CombineMode.AVERAGE, 0.5),
        (0.2, 0.8, CombineMode.MULTIPLY, 0.16),
    ],
)
def test_combine_values(value_a, value_b, mode, expected):
    assert PhysicMaterial.combine_values(value_a, value_b, mode) == pytest.approx(
        expected
    )


def test_combine_with_uses_modes_and_max_damping():
    a = PhysicMaterial(
        friction=0.2,
        restitution=0.8,
        friction_mode=CombineMode.MIN,
        restitution_mode=CombineMode.MAX,
        linear_damping=0.1,
        bounciness_threshold=5.0,
    )
    b = PhysicMaterial(
        friction=0.6,
        restitution=0.3,
        friction_mode=CombineMode.MAX,
        restitution_mode=CombineMode.MIN,
        linear_damping=0.4,
        bounciness_threshold=10.0,
    )

    combined = a.combine_with(b)

    assert combined.friction == pytest.approx(0.6)
    assert combined.restitution == pytest.approx(0.8)
    assert combined.linear_damping == pytest.approx(0.4)
    assert combined.bounciness_threshold == pytest.approx(10.0)
