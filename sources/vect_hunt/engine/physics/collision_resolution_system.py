from typing import TYPE_CHECKING, Optional, Tuple

from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent

if TYPE_CHECKING:
    from vect_hunt.engine.worlds import World
    from vect_hunt.engine.objects import GameObject


class CollisionResolutionSystem:
    """
    Système de correction des collisions. Applique des ajustements de position
    pour résoudre les collisions détectées par le CollisionSystem.

    Dépendant d'un physic body, d'un sytème de collision, et de la physique d'un
    GameObject (masse, friction, rebond...).

    Attributes
    ----------
    world : World
        Monde de jeu associé.
    """

    def __init__(self, world: "World") -> None:
        """
        Initialise le système de résolution des collisions.

        Parameters
        ----------
        world : World
            Le monde dans lequel les objets existent.
        """
        self.world = world

    def update_from_collisions(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], dict],
    ) -> bool:
        """
        Applique la résolution à partir d'un jeu de collisions déjà détectées.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires d'IDs d'objets en collision.
        collision_info : dict[tuple[int, int], dict]
            Informations de collision associées aux paires.

        Returns
        -------
        bool
            True si au moins une correction de collision a été appliquée, False sinon.
        """
        correction_applied = False
        # Résoudre chaque collision
        for id_obj_a, id_obj_b in collisions:
            info_collision = collision_info.get((id_obj_a, id_obj_b))
            if info_collision is None:
                continue

            if self._resolve_collision(id_obj_a, id_obj_b, info_collision):
                correction_applied = True

        return correction_applied

    def _resolve_collision(self, obj_a: int, obj_b: int, collision_info: dict) -> bool:
        """
        Résout une collision entre deux GameObjects avec correction de position
        et annulation de la composante normale de la vélocité, en utilisant
        les infos détaillées.

        Parameters
        ----------
        obj_a : int
            ID du premier objet en collision.
        obj_b : int
            ID du deuxième objet en collision.
        collision_info : dict
            Informations supplémentaires sur la collision (normal, depth, point, ...).

        returns
        -------
        bool
            True si une correction a été appliquée, False sinon.
        """
        # Recupérer les GameObjects et leurs PhysicBodyComponents
        context = self._get_collision_context(obj_a, obj_b)
        if context is None:
            return False

        game_object_a, game_object_b, body_a, body_b = context

        # Résoudre la normale et la profondeur de collision
        normal, depth = self._resolve_normal_and_depth(
            collision_info,
            game_object_a.transform.position,
            game_object_b.transform.position,
        )

        # Si pas de pénétration, ne rien faire
        if depth <= 0:
            return False

        # Appliquer la correction de position
        self._apply_position_correction(
            body_a,
            body_b,
            game_object_a,
            game_object_b,
            normal,
            depth,
        )
        # Appliquer la réponse de vélocité (restitution + friction)
        self._apply_velocity_response(body_a, body_b, normal)

        return True

    def _get_collision_context(
        self,
        obj_a: int,
        obj_b: int,
    ) -> Optional[
        Tuple["GameObject", "GameObject", PhysicBodyComponent, PhysicBodyComponent]
    ]:
        """
        Récupère le contexte de collision (objets et PhysicBody associés).

        Parameters
        ----------
        obj_a : int
            ID du premier objet en collision.
        obj_b : int
            ID du deuxième objet en collision.

        Returns
        -------
        tuple or None
            (game_object_a, game_object_b, body_a, body_b) si disponible,
            sinon None si un PhysicBody manque.
        """
        game_object_a = self.world.game_objects[obj_a]
        game_object_b = self.world.game_objects[obj_b]

        body_a = game_object_a.get_component(PhysicBodyComponent)
        body_b = game_object_b.get_component(PhysicBodyComponent)

        if not body_a or not body_b:
            return None

        return game_object_a, game_object_b, body_a, body_b

    def _resolve_normal_and_depth(
        self,
        collision_info: dict,
        pos_a: Vector2D,
        pos_b: Vector2D,
    ) -> Tuple[Vector2D, float]:
        """
        Résout la normale et la profondeur de collision, avec fallback.

        Parameters
        ----------
        collision_info : dict
            Informations supplémentaires sur la collision (normal, depth, ...).
        pos_a : Vector2D
            Position du premier objet.
        pos_b : Vector2D
            Position du deuxième objet.

        Returns
        -------
        tuple
            (normal, depth) validés, avec valeurs par défaut si absentes.
        """
        normal = collision_info.get("normal")
        depth = collision_info.get("depth")

        if normal is None or depth is None:
            delta = pos_a - pos_b
            if delta.magnitude() == 0:
                normal = Vector2D(1, 0)
            else:
                normal = delta.normalized()
            depth = 1.0

        return normal, depth

    def _apply_position_correction(
        self,
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        normal: Vector2D,
        depth: float,
    ) -> None:
        """
        Corrige la position des objets en fonction de la profondeur de collision.

        Parameters
        ----------
        body_a : PhysicBodyComponent
            PhysicBody du premier objet.
        body_b : PhysicBodyComponent
            PhysicBody du deuxième objet.
        game_object_a : GameObject
            Le premier objet de jeu.
        game_object_b : GameObject
            Le deuxième objet de jeu.
        normal : Vector2D
            Normale de collision (pointant de B vers A).
        depth : float
            Profondeur de pénétration.
        """
        if depth <= 0:
            return

        correction = normal * depth

        is_kinematic_a = body_a.is_kinematic
        is_kinematic_b = body_b.is_kinematic

        if is_kinematic_a and is_kinematic_b:
            return
        if is_kinematic_a:
            game_object_b.transform.move(-1 * correction)
            return
        if is_kinematic_b:
            game_object_a.transform.move(correction)
            return

        # Les deux objets sont dynamiques, partager la correction
        correction = correction * 0.5
        game_object_a.transform.move(correction)
        game_object_b.transform.move(-1 * correction)

    def _apply_velocity_response(
        self,
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        normal: Vector2D,
    ) -> None:
        """
        Applique la réponse de vitesse (restitution + friction) d'une collision.

        Parameters
        ----------
        body_a : PhysicBodyComponent
            PhysicBody du premier objet.
        body_b : PhysicBodyComponent
            PhysicBody du deuxième objet.
        normal : Vector2D
            Normale de collision (pointant de B vers A).
        """
        if normal.magnitude() == 0:
            return
        else:
            normal = normal.normalized()

        contact_material = body_a.material.combine_with(body_b.material)

        # Calcul des masses inverses (0 si cinématique)
        # pour l'application des impulsions
        inv_mass_a = 0.0 if body_a.is_kinematic else 1.0
        inv_mass_b = 0.0 if body_b.is_kinematic else 1.0
        inv_mass_sum = inv_mass_a + inv_mass_b

        if inv_mass_sum == 0.0:
            return

        v_a = body_a.velocity
        v_b = body_b.velocity

        relative_velocity = v_a - v_b
        rel_normal_speed = relative_velocity.dot(normal)

        # Si les objets s'éloignent, ne pas appliquer d'impulsion normale.
        # Epsilon pour éviter les micro-artefacts.
        if rel_normal_speed > 1e-6:
            return

        restitution = contact_material.restitution
        if abs(rel_normal_speed) < contact_material.bounciness_threshold:
            restitution = 0.0

        normal_impulse_magnitude = (
            -(1.0 + restitution) * rel_normal_speed / inv_mass_sum
        )
        normal_impulse = normal * normal_impulse_magnitude

        if not body_a.is_kinematic:
            body_a.velocity = body_a.velocity + normal_impulse
        if not body_b.is_kinematic:
            body_b.velocity = body_b.velocity - normal_impulse

        relative_velocity = body_a.velocity - body_b.velocity
        tangent = relative_velocity - normal * relative_velocity.dot(normal)

        if tangent.magnitude() == 0:
            return

        tangent_dir = tangent.normalized()
        rel_tangent_speed = relative_velocity.dot(tangent_dir)

        friction = contact_material.friction
        tangent_impulse_magnitude = -rel_tangent_speed / inv_mass_sum

        max_friction_impulse = friction * normal_impulse_magnitude
        tangent_impulse_magnitude = max(
            -max_friction_impulse,
            min(tangent_impulse_magnitude, max_friction_impulse),
        )

        tangent_impulse = tangent_dir * tangent_impulse_magnitude

        if not body_a.is_kinematic:
            body_a.velocity = body_a.velocity + tangent_impulse
        if not body_b.is_kinematic:
            body_b.velocity = body_b.velocity - tangent_impulse
