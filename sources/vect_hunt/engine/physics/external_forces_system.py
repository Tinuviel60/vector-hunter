
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.components import PhysicBodyComponent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vect_hunt.engine.worlds.world import World

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
    def apply_gravity(world: "World", delta_time: float) -> None:
        """
        Applique la gravité au corps physique donné.

        Parameters
        ----------
        physic_body : PhysicBodyComponent
            Le composant de corps physique auquel appliquer la gravité.
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        for game_object in world.game_objects.values():
            if not game_object.active:
                continue

            body = game_object.get_component(PhysicBodyComponent)
            if body is None:
                continue
            
            if body.use_gravity and not body.is_kinematic:
                # TODO : Faire de la gravité une propriété du monde ou du système
                gravity_force = Vector2D(0, 9.81) * body.mass * delta_time
                body.add_force(gravity_force)
