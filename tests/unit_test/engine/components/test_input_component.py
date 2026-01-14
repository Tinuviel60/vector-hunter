import pytest
from unittest.mock import MagicMock, Mock

from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.components.input_component import InputComponent
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent


# --------------------
# Setup
# --------------------
@pytest.fixture
def mock_input_system():
    """Mock du InputSystem pour les tests."""
    mock = MagicMock()
    mock.get_vector = MagicMock(return_value=Vector2D(0, 0))
    return mock


@pytest.fixture
def mock_game_object():
    """Mock du GameObject pour tests unitaires."""
    mock = Mock()
    mock.get_component = MagicMock()
    return mock


@pytest.fixture
def mock_physic_body():
    """Mock du PhysicBodyComponent."""
    mock = Mock(spec=PhysicBodyComponent)
    mock.speed = 200.0
    mock.velocity = Vector2D(0, 0)
    mock.set_velocity = MagicMock()
    return mock


# --------------------
# Initialisation
# --------------------
def test_input_component_initialization(mock_input_system):
    """Vérifie que le composant s'initialise correctement."""
    component = InputComponent(mock_input_system)

    assert component.input_system is mock_input_system
    assert component.game_object is None


def test_input_component_stores_input_system_reference(mock_input_system):
    """Vérifie que le composant garde la référence à l'InputSystem."""
    component = InputComponent(mock_input_system)

    assert component.input_system is mock_input_system


# --------------------
# Logique de calcul de vélocité
# --------------------
@pytest.mark.parametrize(
    "input_x, input_y, speed, expected_velocity_x, expected_velocity_y",
    [
        (1.0, 0.0, 200.0, 200.0, 0.0),  # Droite
        (-1.0, 0.0, 200.0, -200.0, 0.0),  # Gauche
        (0.0, 1.0, 200.0, 0.0, 200.0),  # Bas
        (0.0, -1.0, 200.0, 0.0, -200.0),  # Haut
        (0.7071, 0.7071, 200.0, 141.42, 141.42),  # Diagonale
        (1.0, 0.0, 300.0, 300.0, 0.0),  # Vitesse différente
    ],
)
def test_update_calculates_velocity_from_input(
    mock_input_system,
    mock_game_object,
    mock_physic_body,
    input_x,
    input_y,
    max_speed,
    expected_velocity_x,
    expected_velocity_y,
):
    """Vérifie que update calcule correctement la vélocité à partir de l'input."""
    # Setup
    mock_input_system.get_vector.return_value = Vector2D(input_x, input_y)
    mock_physic_body.max_speed = max_speed
    mock_game_object.get_component.return_value = mock_physic_body

    component = InputComponent(mock_input_system)
    component.game_object = mock_game_object

    # Update
    component.update(0.016)

    # Vérifie que set_velocity a été appelé avec les bonnes valeurs
    assert mock_physic_body.set_velocity.call_count == 1
    velocity_arg = mock_physic_body.set_velocity.call_args[0][0]
    assert velocity_arg.x == pytest.approx(expected_velocity_x, abs=0.01)
    assert velocity_arg.y == pytest.approx(expected_velocity_y, abs=0.01)


def test_update_sets_zero_velocity_when_no_input(
    mock_input_system, mock_game_object, mock_physic_body
):
    """Vérifie que la vélocité est mise à zéro quand il n'y a pas d'input."""
    # Simuler aucun input
    mock_input_system.get_vector.return_value = Vector2D(0, 0)
    mock_game_object.get_component.return_value = mock_physic_body

    component = InputComponent(mock_input_system)
    component.game_object = mock_game_object

    # Update
    component.update(0.016)

    # Vérifie que set_velocity(0, 0) a été appelé
    mock_physic_body.set_velocity.assert_called_once()
    velocity_arg = mock_physic_body.set_velocity.call_args[0][0]
    assert velocity_arg.x == 0.0
    assert velocity_arg.y == 0.0


def test_update_does_nothing_without_physic_body(mock_input_system, mock_game_object):
    """Vérifie que update ne plante pas si PhysicBodyComponent est absent."""
    # get_component retourne None
    mock_game_object.get_component.return_value = None

    component = InputComponent(mock_input_system)
    component.game_object = mock_game_object

    mock_input_system.get_vector.return_value = Vector2D(1.0, 0.0)

    # Ne doit pas planter
    component.update(0.016)


def test_update_calls_input_system_get_vector(mock_input_system, mock_game_object):
    """Vérifie que update appelle input_system.get_vector avec le bon contexte."""
    mock_game_object.get_component.return_value = None

    component = InputComponent(mock_input_system)
    component.game_object = mock_game_object

    component.update(0.016)

    mock_input_system.get_vector.assert_called_once_with("move")


def test_update_retrieves_physic_body_component(
    mock_input_system, mock_game_object, mock_physic_body
):
    """Vérifie que update récupère le PhysicBodyComponent via get_component."""
    mock_game_object.get_component.return_value = mock_physic_body

    component = InputComponent(mock_input_system)
    component.game_object = mock_game_object

    component.update(0.016)

    mock_game_object.get_component.assert_called_once_with(PhysicBodyComponent)
