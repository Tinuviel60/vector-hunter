from unittest.mock import MagicMock, Mock

import pytest
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core import Vector2D
from vect_hunt.game.components import IaComponent


# --------------------
# Setup
# --------------------
@pytest.fixture
def mock_game_object():
    """Mock du GameObject pour tests unitaires."""
    mock = Mock()
    mock.transform = Mock()
    mock.transform.position = Vector2D(400, 300)
    mock.transform.forward = MagicMock(return_value=Vector2D(0, 1))
    mock.transform.rotation = Mock()
    mock.transform.rotation.reflect = MagicMock(return_value=Mock())
    mock.get_component = MagicMock()
    return mock


@pytest.fixture
def mock_physic_body():
    """Mock du PhysicBodyComponent."""
    mock = Mock(spec=PhysicBodyComponent)
    mock.speed = 150.0
    mock.set_velocity = MagicMock()
    return mock


# --------------------
# Initialisation
# --------------------
def test_ia_component_initialization_defaults():
    """Vérifie que le composant s'initialise avec les valeurs par défaut."""
    component = IaComponent()

    assert component.top_left == Vector2D(100, 100)
    assert component.bottom_right == Vector2D(700, 500)
    assert component.game_object is None


@pytest.mark.parametrize(
    "top_left_x, top_left_y, bottom_right_x, bottom_right_y",
    [
        (0, 0, 800, 600),
        (50, 50, 750, 550),
        (100, 100, 1000, 800),
    ],
)
def test_ia_component_initialization(
    top_left_x, top_left_y, bottom_right_x, bottom_right_y
):
    """Vérifie que le composant s'initialise avec des valeurs personnalisées."""
    top_left = Vector2D(top_left_x, top_left_y)
    bottom_right = Vector2D(bottom_right_x, bottom_right_y)

    component = IaComponent(top_left, bottom_right)

    assert component.top_left == top_left
    assert component.bottom_right == bottom_right


# --------------------
# Logique de calcul de vélocité
# --------------------
@pytest.mark.parametrize(
    "forward_x, forward_y, speed, expected_vx, expected_vy",
    [
        (0, 1, 150.0, 0, 150),  # Bas
        (-1, 0, 150.0, -150, 0),  # Gauche
        (0, -1, 150.0, 0, -150),  # Haut
        (1, 0, 150.0, 150, 0),  # Droite
        (0.7071, 0.7071, 150.0, 106.07, 106.07),  # Diagonale
    ],
)
def test_move_in_limits_calculates_velocity_from_forward(
    mock_game_object,
    mock_physic_body,
    forward_x,
    forward_y,
    speed,
    expected_vx,
    expected_vy,
):
    """Vérifie que move_in_limits calcule la vélocité depuis forward."""
    # Setup
    mock_game_object.transform.forward.return_value = Vector2D(forward_x, forward_y)
    mock_physic_body.speed = speed
    mock_game_object.get_component.return_value = mock_physic_body

    component = IaComponent(top_left=Vector2D(0, 0), bottom_right=Vector2D(800, 600))
    component.game_object = mock_game_object

    # Call move_in_limits
    component.move_in_limits(0.016)

    # Vérifie que set_velocity a été appelé avec les bonnes valeurs
    assert mock_physic_body.set_velocity.call_count >= 1
    velocity_arg = mock_physic_body.set_velocity.call_args[0][0]
    assert velocity_arg.x == pytest.approx(expected_vx, abs=0.1)
    assert velocity_arg.y == pytest.approx(expected_vy, abs=0.1)


def test_move_in_limits_does_nothing_without_physic_body(mock_game_object):
    """Vérifie que move_in_limits ne plante pas si PhysicBodyComponent est absent."""
    # get_component retourne None
    mock_game_object.get_component.return_value = None

    component = IaComponent()
    component.game_object = mock_game_object

    # Ne doit pas planter
    component.move_in_limits(0.016)


# --------------------
# Détection des limites
# --------------------
@pytest.mark.parametrize(
    "position_x, position_y, direction_x, direction_y, top_left_x, top_left_y, "
    "bottom_right_x, bottom_right_y, should_reflect",
    [
        # Proche du bord gauche (101), direction gauche:
        # future_position = 101 - 150*0.016 = 98.6 < 100 → reflect
        (101, 300, -1, 0, 100, 100, 700, 500, True),
        # Proche du bord droit (699), direction droite:
        # future_position = 699 + 150*0.016 = 701.4 > 700 → reflect
        (699, 300, 1, 0, 100, 100, 700, 500, True),
        # Proche du bord supérieur (499), direction haut:
        # future_position = 499 + 150*0.016 = 501.4 > 500 → reflect
        (400, 499, 0, 1, 100, 100, 700, 500, True),
        # Proche du bord inférieur (101), direction bas:
        # future_position = 101 - 150*0.016 = 98.6 < 100 → reflect
        (400, 101, 0, -1, 100, 100, 700, 500, True),
        # Au centre, aucune limite déclenchée
        (400, 300, 1, 0, 100, 100, 700, 500, False),
        # Proche du bord mais direction opposée (éloignement)
        (101, 300, 1, 0, 100, 100, 700, 500, False),
    ],
)
def test_move_in_limits_detects_boundaries(
    mock_game_object,
    mock_physic_body,
    position_x,
    position_y,
    direction_x,
    direction_y,
    top_left_x,
    top_left_y,
    bottom_right_x,
    bottom_right_y,
    should_reflect,
):
    """Vérifie que move_in_limits détecte correctement les limites."""
    # Setup
    mock_game_object.transform.position = Vector2D(position_x, position_y)
    mock_game_object.transform.forward.return_value = Vector2D(direction_x, direction_y)
    mock_physic_body.speed = 150.0
    mock_game_object.get_component.return_value = mock_physic_body

    # Conserver une référence au mock rotation AVANT l'appel
    # (car l'assignation dans le code écrasera mock_game_object.transform.rotation)
    original_rotation_mock = mock_game_object.transform.rotation

    component = IaComponent(
        top_left=Vector2D(top_left_x, top_left_y),
        bottom_right=Vector2D(bottom_right_x, bottom_right_y),
    )
    component.game_object = mock_game_object

    # Call move_in_limits
    component.move_in_limits(0.016)

    # Vérifie si reflect a été appelé sur le mock ORIGINAL
    if should_reflect:
        original_rotation_mock.reflect.assert_called_once()
    else:
        original_rotation_mock.reflect.assert_not_called()


def test_update_calls_make_decision(mock_game_object, mock_physic_body):
    """Vérifie que update appelle make_decision."""
    mock_game_object.get_component.return_value = mock_physic_body

    component = IaComponent()
    component.game_object = mock_game_object

    # Spy on make_decision
    original_make_decision = component.make_decision
    call_count = [0]

    def spy_make_decision(delta_time):
        call_count[0] += 1
        return original_make_decision(delta_time)

    component.make_decision = spy_make_decision

    # Update
    component.update(0.016)

    # Vérifie que make_decision a été appelé
    assert call_count[0] == 1


def test_make_decision_calls_move_in_limits(mock_game_object, mock_physic_body):
    """Vérifie que make_decision appelle move_in_limits."""
    mock_game_object.get_component.return_value = mock_physic_body

    component = IaComponent()
    component.game_object = mock_game_object

    # Spy on move_in_limits
    original_move_in_limits = component.move_in_limits
    call_count = [0]

    def spy_move_in_limits(delta_time):
        call_count[0] += 1
        return original_move_in_limits(delta_time)

    component.move_in_limits = spy_move_in_limits

    # make_decision
    component.make_decision(0.016)

    # Vérifie que move_in_limits a été appelé
    assert call_count[0] == 1
