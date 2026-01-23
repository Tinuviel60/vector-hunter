from typing import TYPE_CHECKING, Optional, Tuple

from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.physics.collision_info import CollisionInfo

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.scenes.scene import Scene


class CollisionResolutionSystem:
    """
    Système de correction des collisions. Applique des ajustements de position
    pour résoudre les collisions détectées par le CollisionSystem.

    Dépendant d'un physic body, d'un sytème de collision, et de la physique d'un
    GameObject (masse, friction, rebond...).

    Attributes
    ----------
    scene : Scene
        Scène de jeu associé.
    """

    def __init__(self, scene: "Scene") -> None:
        """
        Initialise le système de résolution des collisions.

        Parameters
        ----------
        scene : Scene
            La scène dans laquelle les objets existent.
        """
        self.scene = scene

    def correct_collisions(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
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

    def _resolve_collision(
        self, obj_a: int, obj_b: int, collision_info: CollisionInfo
    ) -> bool:
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
        collision_info : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).

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
        collision_info = self._resolve_collision_info(
            collision_info,
            game_object_a.transform.position,
            game_object_b.transform.position,
        )

        # Si pas de pénétration, ne rien faire
        if collision_info.depth <= 0:
            return False

        # Appliquer la correction de position
        self._apply_position_correction(
            body_a, body_b, game_object_a, game_object_b, collision_info
        )

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
        game_object_a = self.scene.game_objects[obj_a]
        game_object_b = self.scene.game_objects[obj_b]

        body_a = game_object_a.get_component(PhysicBodyComponent)
        body_b = game_object_b.get_component(PhysicBodyComponent)

        if not body_a or not body_b:
            return None

        return game_object_a, game_object_b, body_a, body_b

    def _resolve_collision_info(
        self,
        collision_info: CollisionInfo,
        pos_a: Vector2D,
        pos_b: Vector2D,
    ) -> CollisionInfo:
        """
        Résout la normale et la profondeur de collision, avec fallback.

        Parameters
        ----------
        collision_info : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).
        pos_a : Vector2D
            Position du premier objet.
        pos_b : Vector2D
            Position du deuxième objet.

        Returns
        -------
        tuple
            (normal, depth) validés, avec valeurs par défaut si absentes.
        """

        if collision_info.normal is None or collision_info.depth is None:
            delta = pos_a - pos_b
            if delta.magnitude() == 0:
                collision_info.normal = Vector2D(1, 0)
            else:
                collision_info.normal = delta.normalized()
            collision_info.depth = 1.0

        return collision_info

    def _apply_position_correction(
        self,
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        collision_info: CollisionInfo,
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
        collision_info : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).

        """
        correction = collision_info.normal * collision_info.depth

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

        eps = 1e-9  # TODO : Sortir le epsilon dans une constante globale
        inv_mass_a = 1.0 / body_a.mass if body_a.mass > eps else 0.0
        inv_mass_b = 1.0 / body_b.mass if body_b.mass > eps else 0.0
        inv_mass_sum = inv_mass_a + inv_mass_b

        if inv_mass_sum <= eps:
            return

        # Les deux objets sont dynamiques, partager la correction
        game_object_a.transform.move(correction * (inv_mass_a / inv_mass_sum))
        game_object_b.transform.move(-correction * (inv_mass_b / inv_mass_sum))

    def apply_inpulse_response(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
    ) -> None:
        """
        Applique la réponse d'impulsion (vitesse) pour un ensemble de collisions.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires d'IDs d'objets en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision associées aux paires.
        """

        for id_obj_a, id_obj_b in collisions:
            info_collision = collision_info.get((id_obj_a, id_obj_b))
            if info_collision is None:
                continue

            context = self._get_collision_context(id_obj_a, id_obj_b)
            if context is None:
                continue

            _, _, body_a, body_b = context

            self._apply_velocity_response(body_a, body_b, info_collision.normal)

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
        eps = 1e-9  # TODO : Sortir le epsilon dans une constante globale
        if normal.magnitude_squared() <= eps * eps:
            return
        else:
            normal = normal.normalized()

        contact_material = body_a.material.combine_with(body_b.material)

        # Calcul des masses inverses (0 si cinématique)
        # pour l'application des impulsions
        inv_mass_a = 0.0 if body_a.is_kinematic else (1.0 / body_a.mass)
        inv_mass_b = 0.0 if body_b.is_kinematic else (1.0 / body_b.mass)
        inv_mass_sum = inv_mass_a + inv_mass_b

        if inv_mass_sum <= eps:
            return

        v_a = body_a.velocity
        v_b = body_b.velocity

        relative_velocity = v_a - v_b
        rel_normal_speed = relative_velocity.dot(normal)

        # Si les objets s'éloignent, ne pas appliquer d'impulsion normale.
        if rel_normal_speed > eps:
            return

        restitution = contact_material.restitution
        if abs(rel_normal_speed) < contact_material.bounciness_threshold:
            restitution = 0.0

        # Calcul de l'impulsion normale
        jn = (-(1.0 + restitution) * rel_normal_speed) / inv_mass_sum
        normal_impulse = normal * jn

        # IMPORTANT : appliquer J en Δv via inv_mass
        if not body_a.is_kinematic:
            body_a.apply_impulse(normal_impulse)
        if not body_b.is_kinematic:
            body_b.apply_impulse(-normal_impulse)

        # Recalcul après impulsion normale
        relative_velocity = body_a.velocity - body_b.velocity

        tangent = relative_velocity - normal * relative_velocity.dot(normal)
        if tangent.magnitude_squared() <= eps * eps:
            return

        tangent_dir = tangent.normalized()
        rel_tangent_speed = relative_velocity.dot(tangent_dir)

        jt = (-rel_tangent_speed) / inv_mass_sum

        friction = contact_material.friction
        max_friction_impulse = friction * jn
        jt = max(-max_friction_impulse, min(jt, max_friction_impulse))

        tangent_impulse = tangent_dir * jt

        # IMPORTANT : appliquer Jt en Δv via inv_mass
        if not body_a.is_kinematic:
            body_a.apply_impulse(tangent_impulse)
        if not body_b.is_kinematic:
            body_b.apply_impulse(-tangent_impulse)
