from typing import TYPE_CHECKING

from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.physics import CollisionTracker
from vect_hunt.engine.components import PhysicBodyComponent

if TYPE_CHECKING:
    from vect_hunt.engine.worlds.world import World


class CollisionResolutionSystem:
    """
    Système de correction des collisions. Applique des ajustements de position
    pour résoudre les collisions détectées par le CollisionSystem.

    Dépendant d'un physic body, d'un sytème de collision, et de la physique d'un 
    GameObject (masse, friction, rebond...).
    """

    def __init__(self, collision_tracker: CollisionTracker, world: "World") -> None:
        """
        Initialise le système de résolution des collisions.

        Parameters
        ----------
        collision_tracker : CollisionTracker
            Système de suivi des collisions.
        world : World
            Le monde dans lequel les objets existent.
        """
        self.collision_tracker = collision_tracker
        self.world = world

    def update(self, delta_time: float) -> None:
        """
        Met à jour le système de résolution des collisions.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        # Récupérer les collisions détectées
        collisions = self.collision_tracker.get_all_collisions()

        # Résoudre chaque collision
        for id_obj_a, id_obj_b in collisions:
            info_collision = self.collision_tracker.get_collision_info(id_obj_a, id_obj_b)
            assert info_collision is not None, "Les informations de collision doivent être disponibles"
            self._resolve_collision(id_obj_a, id_obj_b, info_collision)

    def _resolve_collision(self, obj_a: int, obj_b: int, collision_info: dict) -> None:
        """
        Résout une collision entre deux GameObjects avec correction de position
        et annulation de la composante normale de la vélocité, en utilisant les infos détaillées.

        Parameters
        ----------
        obj_a : int
            ID du premier objet en collision.
        obj_b : int
            ID du deuxième objet en collision.
        collision_info : dict
            Informations supplémentaires sur la collision (normal, depth, point, ...).
        """
        game_object_a = self.world.game_objects[obj_a]
        game_object_b = self.world.game_objects[obj_b]

        physic_body_a = game_object_a.get_component(PhysicBodyComponent)
        physic_body_b = game_object_b.get_component(PhysicBodyComponent)

        if not physic_body_a or not physic_body_b:
            return

        # --- Correction de position ---
        normal = collision_info.get("normal")
        depth = collision_info.get("depth")
        if normal is None or depth is None:
            # Fallback arbitraire si info manquante
            pos_a = game_object_a.transform.position
            pos_b = game_object_b.transform.position
            delta = pos_a - pos_b
            if delta.magnitude() == 0:
                normal = Vector2D(1, 0)
            else:
                normal = delta.normalized()
            depth = 1.0

        # Correction proportionnelle à la profondeur
            # Correction proportionnelle à la profondeur
            correction = normal * (depth / 2)
            # Gestion des objets kinematic : ne pas déplacer si is_kinematic
            is_kinematic_a = physic_body_a.is_kinematic
            is_kinematic_b = physic_body_b.is_kinematic
            if is_kinematic_a and is_kinematic_b:
                # Aucun déplacement si les deux sont kinematic
                pass
            elif is_kinematic_a:
                # Seul B bouge
                game_object_b.transform.move(-1 * normal * depth)
            elif is_kinematic_b:
                # Seul A bouge
                game_object_a.transform.move(normal * depth)
            else:
                # Les deux bougent
                game_object_a.transform.move(correction)
                game_object_b.transform.move(-1 * correction)

        # --- Annulation de la composante normale de la vélocité ---
        v_a = physic_body_a.velocity
        v_b = physic_body_b.velocity
        v_a_normal = normal * v_a.dot(normal)
        v_b_normal = normal * v_b.dot(normal)
        physic_body_a.velocity = v_a - v_a_normal
        physic_body_b.velocity = v_b - v_b_normal