import pytest

from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.components.input_component import InputComponent
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.input import InputSystem


# --------------------
# Setup
# --------------------
@pytest.fixture
def input_system():
    """InputSystem réel pour tests d'intégration."""
    return InputSystem()


@pytest.fixture
def game_object_with_physics_and_input(input_system):
    """GameObject avec PhysicBodyComponent et InputComponent attachés."""
    obj = GameObject("Player")
    physic_body = PhysicBodyComponent(speed=200.0)
    input_comp = InputComponent(input_system)
    obj.add_component(physic_body)
    obj.add_component(input_comp)
    return obj, input_system


# --------------------
# Intégration InputComponent ↔ PhysicBodyComponent
# --------------------
@pytest.mark.parametrize(
    "input_x, input_y, expected_velocity_x, expected_velocity_y",
    [
        (1.0, 0.0, 200.0, 0.0),  # Droite
        (-1.0, 0.0, -200.0, 0.0),  # Gauche
        (0.0, 1.0, 0.0, 200.0),  # Bas
        (0.0, -1.0, 0.0, -200.0),  # Haut
        (0.7071, 0.7071, 141.42, 141.42),  # Diagonale (normalisé)
    ],
)
def test_input_component_updates_physic_body_velocity(
    game_object_with_physics_and_input,
    input_x,
    input_y,
    expected_velocity_x,
    expected_velocity_y,
):
    """
    Test d'intégration : vérifie que InputComponent communique
    correctement avec PhysicBodyComponent.
    """
    game_object, input_system = game_object_with_physics_and_input

    # Simuler un input en modifiant directement l'état de l'action
    from vect_hunt.engine.input.input_action import ActionState, ActionType

    if "move" not in input_system._action_states:
        input_system._action_states["move"] = ActionState(
            action_name="move", action_type=ActionType.VECTOR2D
        )
    input_system._action_states["move"].vector_value = Vector2D(input_x, input_y)

    # Récupérer les composants
    input_comp = game_object.get_component(InputComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    # Update le composant d'input
    input_comp.update(0.016)

    # Vérifie que la vélocité a été définie sur le PhysicBodyComponent
    assert physic_body.velocity.x == pytest.approx(expected_velocity_x, abs=0.01)
    assert physic_body.velocity.y == pytest.approx(expected_velocity_y, abs=0.01)


def test_input_component_stops_physic_body_when_no_input(
    game_object_with_physics_and_input,
):
    """
    Test d'intégration : vérifie que l'absence d'input arrête le PhysicBodyComponent.
    """
    game_object, input_system = game_object_with_physics_and_input

    # Définir une vélocité initiale
    physic_body = game_object.get_component(PhysicBodyComponent)
    physic_body.set_velocity(Vector2D(100, 100))

    # Simuler aucun input (vecteur nul)
    from vect_hunt.engine.input.input_action import ActionState, ActionType

    if "move" not in input_system._action_states:
        input_system._action_states["move"] = ActionState(
            action_name="move", action_type=ActionType.VECTOR2D
        )
    input_system._action_states["move"].vector_value = Vector2D(0, 0)

    # Update le composant d'input
    input_comp = game_object.get_component(InputComponent)
    input_comp.update(0.016)

    # Vérifie que la vélocité est à zéro
    assert physic_body.velocity.x == 0.0
    assert physic_body.velocity.y == 0.0


# --------------------
# Intégration InputComponent ↔ PhysicBodyComponent ↔ Transform
# --------------------
def test_full_input_to_movement_integration(game_object_with_physics_and_input):
    """
    Test d'intégration complet : Input → PhysicBody → Transform → Déplacement.
    """
    game_object, input_system = game_object_with_physics_and_input

    # Position initiale
    initial_position = game_object.transform.position

    # Simuler un input vers la droite
    from vect_hunt.engine.input.input_action import ActionState, ActionType

    if "move" not in input_system._action_states:
        input_system._action_states["move"] = ActionState(
            action_name="move", action_type=ActionType.VECTOR2D
        )
    input_system._action_states["move"].vector_value = Vector2D(1.0, 0.0)

    # Update les composants
    input_comp = game_object.get_component(InputComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    input_comp.update(0.1)  # Input génère vélocité
    physic_body.update(0.1)  # PhysicBody applique déplacement

    # Vérifie le déplacement réel
    new_position = game_object.transform.position
    expected_displacement = 200.0 * 0.1  # speed * delta_time

    assert new_position.x == pytest.approx(
        initial_position.x + expected_displacement, abs=0.01
    )
    assert new_position.y == pytest.approx(initial_position.y, abs=0.01)
