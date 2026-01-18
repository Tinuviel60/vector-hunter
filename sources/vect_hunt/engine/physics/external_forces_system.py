from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vect_hunt.engine.scenes.scene import Scene


class ExternalForcesSystem:
    """
    Classe représentant un système de gestion des forces externes
    appliquées aux corps physiques.
    """

    def __init__(self):
        """
        Initialise le système de forces externes.
        """
        pass

    @staticmethod
    def apply_gravity(scene: "Scene", delta_time: float) -> None:
        """
        Applique la gravité au corps physique donné.

        Parameters
        ----------
        physic_body : PhysicBodyComponent
            Le composant de corps physique auquel appliquer la gravité.
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        for game_object in scene.game_objects.values():
            if not game_object.active:
                continue

            body = game_object.get_component(PhysicBodyComponent)
            if body is None:
                continue

            if body.use_gravity and not body.is_kinematic:
                # TODO : Faire de la gravité une propriété de la scène ou du système
                units = scene.units
                gravity_m_s2 = units.get("gravity_m_s2", 9.81)
                pixels_per_meter = units.get("pixels_per_meter", 100.0)
                gravity_accel = Vector2D(0, gravity_m_s2 * pixels_per_meter)
                body.add_acceleration(gravity_accel)
