import pytest
from unittest.mock import Mock, MagicMock

from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent


# --------------------
# Setup
# --------------------
@pytest.fixture
def mock_game_object():
    """Mock du GameObject pour tests unitaires."""
    mock = Mock()
    mock.transform = Mock()
    mock.transform.move = MagicMock()
    return mock


# --------------------
# Initialisation
# --------------------
def test_physic_body_initialization_defaults():
    """Vérifie que le composant s'initialise avec les valeurs par défaut."""
    component = PhysicBodyComponent()

    assert component.speed == 300.0
    assert component.velocity == Vector2D(0, 0)
    assert component.acceleration == Vector2D(0, 0)
    assert component.game_object is None


@pytest.mark.parametrize(
    "speed",
    [100.0, 200.0, 500.0, 1000.0],
)
def test_physic_body_initialization(speed):
    """Vérifie que le composant s'initialise avec une vitesse personnalisée."""
    component = PhysicBodyComponent(speed=speed)

    assert component.speed == speed
    assert component.velocity == Vector2D(0, 0)
    assert component.acceleration == Vector2D(0, 0)


# --------------------
# Gestion de la vélocité
# --------------------
@pytest.mark.parametrize(
    "vx, vy",
    [
        (0, 0),
        (100, 0),
        (0, 100),
        (100, 100),
        (-50, 75),
    ],
)
def test_set_velocity(vx, vy):
    """Vérifie que set_velocity définit correctement la vélocité."""
    component = PhysicBodyComponent()
    velocity = Vector2D(vx, vy)

    component.set_velocity(velocity)

    assert component.velocity == velocity


# --------------------
# Gestion des forces
# --------------------
@pytest.mark.parametrize(
    "force_x, force_y",
    [
        (10, 0),
        (0, 10),
        (10, 10),
        (-5, 15),
    ],
)
def test_add_force(force_x, force_y):
    """Vérifie que add_force ajoute une force à l'accélération."""
    # TODO : faire une variante avec une masse différente de 1.0
    component = PhysicBodyComponent()
    force = Vector2D(force_x, force_y)

    component.add_force(force)

    assert component.acceleration == force


def test_add_multiple_forces():
    """Vérifie que add_force cumule les forces."""
    component = PhysicBodyComponent()

    component.add_force(Vector2D(10, 0))
    component.add_force(Vector2D(0, 10))
    component.add_force(Vector2D(5, 5))

    assert component.acceleration == Vector2D(15, 15)


# --------------------
# Calcul de déplacement
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
def test_update_calculates_displacement(
    mock_game_object, vx, vy, delta_time, expected_dx, expected_dy
):
    """Vérifie que update calcule le déplacement correct à partir de la vélocité."""
    component = PhysicBodyComponent()
    component.game_object = mock_game_object

    # Définir une vélocité
    component.set_velocity(Vector2D(vx, vy))

    # Update
    component.update(delta_time)

    # Vérifier que transform.move a été appelé avec le bon déplacement
    mock_game_object.transform.move.assert_called_once()
    displacement_arg = mock_game_object.transform.move.call_args[0][0]
    assert displacement_arg.x == pytest.approx(expected_dx, abs=0.01)
    assert displacement_arg.y == pytest.approx(expected_dy, abs=0.01)


def test_update_does_not_call_move_with_zero_velocity(mock_game_object):
    """Vérifie que update ne déplace pas si la vélocité est nulle."""
    component = PhysicBodyComponent()
    component.game_object = mock_game_object

    # Vélocité nulle
    component.set_velocity(Vector2D(0, 0))

    # Update
    component.update(0.016)

    # transform.move ne doit pas être appelé
    mock_game_object.transform.move.assert_not_called()


def test_update_applies_acceleration_to_velocity(mock_game_object):
    """Vérifie que update applique l'accélération à la vélocité."""
    component = PhysicBodyComponent()
    component.game_object = mock_game_object

    # Vélocité initiale
    component.set_velocity(Vector2D(100, 0))

    # Ajouter une accélération
    component.add_force(Vector2D(50, 25))

    # Update avec delta_time = 0.1
    component.update(0.1)

    # Vélocité attendue = (100, 0) + (50, 25) * 0.1 = (105, 2.5)
    assert component.velocity.x == pytest.approx(105.0, abs=0.01)
    assert component.velocity.y == pytest.approx(2.5, abs=0.01)


def test_update_resets_acceleration(mock_game_object):
    """Vérifie que update réinitialise l'accélération après application."""
    component = PhysicBodyComponent()
    component.game_object = mock_game_object

    # Ajouter une accélération
    component.add_force(Vector2D(100, 100))

    # Update
    component.update(0.016)

    # Accélération réinitialisée
    assert component.acceleration == Vector2D(0, 0)


# --------------------
# Stop
# --------------------
def test_stop_resets_velocity_and_acceleration():
    """Vérifie que stop arrête complètement le mouvement."""
    component = PhysicBodyComponent()

    # Définir vélocité et accélération
    component.set_velocity(Vector2D(100, 100))
    component.add_force(Vector2D(50, 50))

    # Stop
    component.stop()

    # Tout doit être à zéro
    assert component.velocity == Vector2D(0, 0)
    assert component.acceleration == Vector2D(0, 0)


# --------------------
# Logique combinée
# --------------------
def test_update_with_acceleration_calculates_correct_displacement(mock_game_object):
    """Vérifie que update calcule le déplacement avec accélération + vélocité."""
    component = PhysicBodyComponent()
    component.game_object = mock_game_object

    # Vélocité initiale + accélération
    component.set_velocity(Vector2D(100, 0))
    component.add_force(Vector2D(50, 25))

    # Update avec delta_time = 0.1
    component.update(0.1)

    # Vélocité finale = (100, 0) + (50, 25) * 0.1 = (105, 2.5)
    # Déplacement = (105, 2.5) * 0.1 = (10.5, 0.25)
    mock_game_object.transform.move.assert_called_once()
    displacement_arg = mock_game_object.transform.move.call_args[0][0]
    assert displacement_arg.x == pytest.approx(10.5, abs=0.01)
    assert displacement_arg.y == pytest.approx(0.25, abs=0.01)
