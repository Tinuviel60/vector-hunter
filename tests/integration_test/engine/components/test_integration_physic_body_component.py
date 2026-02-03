import pytest
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.objects import GameObject


# --------------------
# Setup
# --------------------
@pytest.fixture
def game_object_with_physics():
    """GameObject avec PhysicBodyComponent attaché."""
    obj = GameObject("TestObject")
    physic_body = PhysicBodyComponent(speed=300.0, is_controlled=True)
    obj.add_component(physic_body)
    return obj


# --------------------
# Intégration PhysicBodyComponent ↔ Transform
# --------------------
@pytest.mark.parametrize(
    "vx, vy, delta_time, expected_dx, expected_dy",
    [
        (100, 0, 0.016, 1.6, 0.0),  # Droite
        (0, 100, 0.016, 0.0, 1.6),  # Bas
        (100, 100, 0.016, 1.6, 1.6),  # Diagonale
        (-100, 0, 0.016, -1.6, 0.0),  # Gauche
        (0, -100, 0.016, 0.0, -1.6),  # Haut
        (200, 0, 0.5, 100.0, 0.0),  # Long delta_time
    ],
)
def test_physic_body_applies_velocity_to_transform(
    game_object_with_physics, vx, vy, delta_time, expected_dx, expected_dy
):
    """
    Test d'intégration : vérifie que PhysicBodyComponent applique
    correctement la vélocité au Transform.
    """
    game_object = game_object_with_physics
    physic_body = game_object.get_component(PhysicBodyComponent)

    # Position initiale
    initial_position = game_object.transform.position

    # Définir une vélocité
    physic_body.set_velocity(Vector2D(vx, vy))

    # Update
    physic_body.update(delta_time)

    # Vérifier le déplacement via Transform
    new_position = game_object.transform.position
    assert new_position.x == pytest.approx(initial_position.x + expected_dx, abs=0.01)
    assert new_position.y == pytest.approx(initial_position.y + expected_dy, abs=0.01)


def test_physic_body_with_zero_velocity_does_not_move_transform(
    game_object_with_physics,
):
    """
    Test d'intégration : vérifie que vélocité nulle n'affecte pas Transform.
    """
    game_object = game_object_with_physics
    physic_body = game_object.get_component(PhysicBodyComponent)

    initial_position = game_object.transform.position

    # Vélocité nulle
    physic_body.set_velocity(Vector2D(0, 0))

    # Update
    physic_body.update(0.016)

    # Position inchangée
    assert game_object.transform.position == initial_position


def test_physic_body_acceleration_affects_velocity_and_transform(
    game_object_with_physics,
):
    """
    Test d'intégration : vérifie que l'accélération modifie la vélocité
    qui est ensuite appliquée au Transform.
    """
    game_object = game_object_with_physics
    physic_body = game_object.get_component(PhysicBodyComponent)

    initial_position = game_object.transform.position

    # Vélocité initiale
    physic_body.set_velocity(Vector2D(100, 0))

    # Ajouter une force qui génère une accélération
    physic_body.add_force(Vector2D(50, 25))

    # Update avec delta_time = 0.1
    physic_body.update(0.1)

    # Vélocité attendue = (100, 0) + (50, 25) * 0.1 = (105, 2.5)
    assert physic_body.velocity.x == pytest.approx(105.0, abs=0.01)
    assert physic_body.velocity.y == pytest.approx(2.5, abs=0.01)

    # Déplacement attendu = (105, 2.5) * 0.1 = (10.5, 0.25)
    new_position = game_object.transform.position
    assert new_position.x == pytest.approx(initial_position.x + 10.5, abs=0.01)
    assert new_position.y == pytest.approx(initial_position.y + 0.25, abs=0.01)


def test_multiple_physic_body_updates_cumulative_movement(game_object_with_physics):
    """
    Test d'intégration : vérifie que plusieurs updates cumulent
    le déplacement sur Transform.
    """
    game_object = game_object_with_physics
    physic_body = game_object.get_component(PhysicBodyComponent)

    initial_position = game_object.transform.position

    # Vélocité constante
    physic_body.set_velocity(Vector2D(100, 0))

    # 3 updates de 0.1s chacun
    physic_body.update(0.1)
    physic_body.update(0.1)
    physic_body.update(0.1)

    # Déplacement total = 100 * 0.3 = 30
    new_position = game_object.transform.position
    assert new_position.x == pytest.approx(initial_position.x + 30.0, abs=0.01)
    assert new_position.y == pytest.approx(initial_position.y, abs=0.01)
