import math
import pytest

from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.components.ia_component import IaComponent
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.objects import GameObject


# --------------------
# Setup
# --------------------
@pytest.fixture
def game_object_with_ia():
    """GameObject avec IaComponent et PhysicBodyComponent attachés."""
    obj = GameObject("Enemy")
    physic_body = PhysicBodyComponent(speed=150.0)
    ia_comp = IaComponent(top_left=Vector2D(0, 0), bottom_right=Vector2D(800, 600))
    obj.add_component(physic_body)
    obj.add_component(ia_comp)
    return obj


# --------------------
# Intégration IaComponent ↔ PhysicBodyComponent ↔ Transform
# --------------------
def test_ia_component_sets_velocity_based_on_forward_direction(game_object_with_ia):
    """
    Test d'intégration : vérifie que IaComponent génère une vélocité
    basée sur la direction forward du Transform.
    """
    game_object = game_object_with_ia

    # Position au centre, direction vers le bas (rotation 0)
    game_object.transform.translate(Vector2D(400, 300))
    game_object.transform.set_rotation(0)

    # Update l'IA
    ia_comp = game_object.get_component(IaComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    ia_comp.update(0.016)

    # La direction forward avec rotation 0 est (0, -1) donc vers le haut
    # Vélocité attendue = (0, -1) * 150.0 = (0, -150)
    assert physic_body.velocity.x == pytest.approx(0.0, abs=0.01)
    assert physic_body.velocity.y == pytest.approx(-150.0, abs=0.01)


@pytest.mark.parametrize(
    "rotation, expected_vx, expected_vy",
    [
        (0, 0, -150),  # Haut
        (math.pi / 2, 150, 0),  # Droite
        (math.pi, 0, 150),  # Bas
        (-math.pi / 2, -150, 0),  # Gauche
    ],
)
def test_ia_respects_transform_rotation(
    game_object_with_ia, rotation, expected_vx, expected_vy
):
    """
    Test d'intégration : vérifie que la vélocité générée par l'IA
    correspond à la rotation du Transform.
    """
    game_object = game_object_with_ia

    # Position au centre avec rotation spécifique
    game_object.transform.translate(Vector2D(400, 300))
    game_object.transform.set_rotation(rotation)

    # Update l'IA
    ia_comp = game_object.get_component(IaComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    ia_comp.update(0.016)

    # Vérifie la vélocité
    assert physic_body.velocity.x == pytest.approx(expected_vx, abs=0.1)
    assert physic_body.velocity.y == pytest.approx(expected_vy, abs=0.1)


def test_ia_reflects_on_boundary_and_updates_rotation(game_object_with_ia):
    """
    Test d'intégration : vérifie que l'IA modifie la rotation du Transform
    quand elle détecte un rebond sur les limites.
    """
    game_object = game_object_with_ia

    # Position très proche du bord gauche (1px), direction gauche
    # Limites du fixture: (0, 0) à (800, 600)
    # Convention: rotation 0 = haut, π/2 = droite, π = bas, -π/2 = gauche
    game_object.transform.translate(Vector2D(1, 300))
    game_object.transform.set_rotation(-math.pi / 2)  # Gauche (-1, 0)

    initial_rotation = game_object.transform.rotation.angle

    # Update l'IA - future_position sera < 0, donc réflexion
    ia_comp = game_object.get_component(IaComponent)
    ia_comp.update(0.016)

    # La rotation devrait avoir changé (réflexion: π/2 → -π/2)
    new_rotation = game_object.transform.rotation.angle
    assert new_rotation != pytest.approx(initial_rotation, abs=0.01)


# --------------------
# Intégration complète : IA → PhysicBody → Transform → Déplacement
# --------------------
def test_full_ia_to_movement_integration(game_object_with_ia):
    """
    Test d'intégration complet : IA → PhysicBody → Transform → Déplacement.
    """
    game_object = game_object_with_ia

    # Position initiale au centre
    game_object.transform.translate(Vector2D(400, 300))
    initial_position = game_object.transform.position

    # Update IA et PhysicBody
    ia_comp = game_object.get_component(IaComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    ia_comp.update(0.1)  # IA génère vélocité
    physic_body.update(0.1)  # PhysicBody applique déplacement

    # Vérifie qu'un déplacement a eu lieu
    new_position = game_object.transform.position
    displacement = (new_position - initial_position).magnitude()

    # Déplacement attendu = 150.0 * 0.1 = 15.0
    assert displacement == pytest.approx(15.0, abs=0.1)


def test_ia_boundary_reflection_multiple_updates(game_object_with_ia):
    """
    Test d'intégration : vérifie que l'IA rebondit correctement sur plusieurs frames.
    """
    game_object = game_object_with_ia
    ia_comp = game_object.get_component(IaComponent)
    physic_body = game_object.get_component(PhysicBodyComponent)

    # Position proche du bord supérieur, direction vers le haut
    game_object.transform.translate(Vector2D(400, 100))
    game_object.transform.set_rotation(math.pi)  # Haut

    # Plusieurs updates pour forcer le rebond
    for _ in range(5):
        ia_comp.update(0.016)
        physic_body.update(0.016)

    # Vérifie que l'objet est toujours dans les limites
    position = game_object.transform.position
    assert 0 <= position.x <= 800
    assert 0 <= position.y <= 600
