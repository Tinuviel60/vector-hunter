import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core.collisions.collision_info import CollisionInfo
from vect_hunt.engine.core.math.numeric import Numeric
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.physics.physic_material import PhysicMaterial
    from vect_hunt.engine.scenes.scene import Scene

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ContactKinematics:
    """
    Hold kinematic data for a single contact point.

    This container stores world-space lever arms and the relative velocity
    computed at the contact point. It exists to keep the impulse solver code
    readable and explicit.

    Attributes
    ----------
    lever_arm_a : Vector2D
        Vector from body A center of mass (world) to the contact point (world).
    lever_arm_b : Vector2D
        Vector from body B center of mass (world) to the contact point (world).
    relative_velocity : Vector2D
        Relative velocity at contact point (vB_point - vA_point).
    normal_velocity : float
        Relative velocity projected on the contact normal.
    """

    lever_arm_a: "Vector2D"
    lever_arm_b: "Vector2D"
    relative_velocity: "Vector2D"
    normal_velocity: float


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

            if self._resolve_collision(
                id_obj_a,
                id_obj_b,
                info_collision,
            ):
                correction_applied = True

        return correction_applied

    def _resolve_collision(
        self,
        obj_a: int,
        obj_b: int,
        collision_info: CollisionInfo,
    ) -> bool:
        """
        Résout une collision entre deux GameObjects avec correction de position,
        en utilisant les infos détaillées.

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
        correction_applied = self._apply_position_correction(
            body_a,
            body_b,
            game_object_a,
            game_object_b,
            collision_info,
        )

        return correction_applied

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

        # if collision_info.normal is None or collision_info.depth is None:
        #     delta = pos_a - pos_b
        #     if delta.magnitude() == 0:
        #         collision_info.normal = Vector2D(1, 0)
        #     else:
        #         collision_info.normal = delta.normalized()
        #     collision_info.depth = 1.0

        return collision_info

    def _apply_position_correction(
        self,
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        collision_info: CollisionInfo,
    ) -> bool:
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

        Returns
        -------
        bool
            True si une correction a été appliquée, False sinon.
        """
        slop = Tolerence.COLLISION / 1000
        percent = 0.6
        corrected_depth = max(0.0, collision_info.depth - slop) * percent

        collision_eps = Tolerence.COLLISION
        normal = collision_info.normal.normalized()
        correction = normal * corrected_depth
        if correction.magnitude_squared() <= collision_eps * collision_eps:
            return False

        if body_a.is_kinematic and body_b.is_kinematic:
            return False

        # Corriger la position si un des deux est cinématique
        if body_a.is_kinematic:
            game_object_b.transform.move(correction)

            return True
        if body_b.is_kinematic:
            game_object_a.transform.move(-correction)
            return True

        # Corriger la position en fonction des masses pour les deux dynamiques
        general_eps = Tolerence.GENERAL
        inv_mass_a = body_a.invert_mass()
        inv_mass_b = body_b.invert_mass()
        inv_mass_sum = inv_mass_a + inv_mass_b

        if inv_mass_sum <= general_eps:
            return False

        # Les deux objets sont dynamiques, partager la correction
        game_object_a.transform.move(-correction * (inv_mass_a / inv_mass_sum))
        game_object_b.transform.move(correction * (inv_mass_b / inv_mass_sum))

        return True

    def apply_impulse_response(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
        delta_time: float,
    ) -> bool:
        """
        Applique la réponse d'impulsion pour un ensemble de collisions.
        Utilise 1 à 2 points de contact.
        Génère aussi de la rotation via l'impulsion appliquée au point.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires d'IDs d'objets en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision associées aux paires.
        delta_time : float
            Pas de temps de la frame (secondes).
        reverse_point : bool
            Inverse l'ordre des points de contact pour la résolution.
        """

        impulsion_max = 0.0
        for id_obj_a, id_obj_b in collisions:
            info_collision = collision_info.get((id_obj_a, id_obj_b))
            if info_collision is None:

                continue

            context = self._get_collision_context(id_obj_a, id_obj_b)
            if context is None:
                continue

            game_object_a, game_object_b, body_a, body_b = context

            impulsion = self._apply_velocity_response(
                game_object_a, game_object_b, body_a, body_b, info_collision, delta_time
            )
            if impulsion > impulsion_max:
                impulsion_max = impulsion

        return impulsion_max > 5.0  # TODO : Valeurs arbitraire à retravailler

    def _apply_velocity_response(
        self,
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        info_collision: CollisionInfo,
        delta_time: float,
    ) -> float:
        """
        Applique restitution + friction d'une collision en utilisant
        les points de contact.

        Parameters
        ----------
        game_object_a : GameObject
            Le premier objet de jeu.
        game_object_b : GameObject
            Le deuxième objet de jeu.
        body_a : PhysicBodyComponent
            PhysicBody du premier objet.
        body_b : PhysicBodyComponent
            PhysicBody du deuxième objet.
        info_collision : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).
        delta_time : float
            Pas de temps de la frame (secondes).
        reverse_point : bool
            Inverse l'ordre des points de contact pour la résolution.

        """

        if len(info_collision.points) == 0:
            return 0.0

        collision_eps = Tolerence.COLLISION
        general_eps = Tolerence.GENERAL
        if info_collision.normal.magnitude_squared() <= collision_eps * collision_eps:
            return 0.0

        normal = info_collision.normal.normalized()
        contact_material = body_a.material.combine_with(body_b.material)

        # Calcul des masses inverses (0 si cinématique)
        # pour l'application des impulsions
        inv_mass_a = body_a.invert_mass()
        inv_mass_b = body_b.invert_mass()
        inv_inertia_a = body_a.invert_inertia()
        inv_inertia_b = body_b.invert_inertia()

        # Si les deux corps sont cinématiques, ne rien faire
        if (inv_mass_a + inv_mass_b + inv_inertia_a + inv_inertia_b) <= general_eps:
            return 0.0

        tr_a = game_object_a.transform
        tr_b = game_object_b.transform

        com_a = tr_a.to_scene_point(body_a.mass_center)
        com_b = tr_b.to_scene_point(body_b.mass_center)

        impulsion_max = 0.0
        for point in info_collision.points:
            impulsion = self.solve_contact_point(
                body_a=body_a,
                body_b=body_b,
                com_a=com_a,
                com_b=com_b,
                contact_point=point,
                normal=normal,
                depth=info_collision.depth,
                delta_time=delta_time,
                inv_mass_a=inv_mass_a,
                inv_mass_b=inv_mass_b,
                inv_inertia_a=inv_inertia_a,
                inv_inertia_b=inv_inertia_b,
                material=contact_material,
            )
            if impulsion > impulsion_max:
                impulsion_max = impulsion

        return impulsion_max

    def _compute_penetration_bias(
        self, depth: float, delta_time: float, slop: float, beta: float
    ) -> float:
        """
        Calcule le bias de pénétration de Baumgarte utilisé
        pour corriger la pénétration.

        Ce biais agit comme une vélocité de fermeture supplémentaire
        le long de la normale de contact, pour forcer le solveur
        à générer une impulsion de séparation lorsque les objets sont déjà
        en pénétration.

        Parameters
        ----------
        depth : float
            Profondeur de pénétration (pixels). Doit être >= 0 pour un contact valide.
        delta_time : float
            Pas de temps de la frame (secondes).
        slop : float
            Tolérance de pénétration autorisée (pixels).
            La profondeur en dessous de cette valeur est ignorée.
        beta : float
            Facteur de biais (sans dimension).
            Les valeurs typiques sont dans [0.1, 0.3].

        Returns
        -------
        float
            Vélocité de correction à appliquer le long de la normale (pixels/secondes).
        """
        if delta_time <= Tolerence.GENERAL:
            return 0.0

        allowed = max(0.0, depth - slop)
        if allowed <= Tolerence.GENERAL:
            return 0.0

        return (beta / delta_time) * allowed

    def solve_contact_point(
        self,
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        com_a: "Vector2D",
        com_b: "Vector2D",
        contact_point: "Vector2D",
        normal: "Vector2D",
        depth: float,
        delta_time: float,
        inv_mass_a: float,
        inv_mass_b: float,
        inv_inertia_a: float,
        inv_inertia_b: float,
        material: "PhysicMaterial",
    ) -> float:
        """
        Résoud l'impulsion (normale + friction) pour un seul point de contact.

        Cette fonction effectue :
        - le calcul de la vélocité relative au contact (incluant la rotation)
        - le calcul de l'impulsion normale et son application
        - le recalcul de la vélocité relative
        - le calcul de l'impulsion de friction et son application

        Parameters
        ----------
        body_a : PhysicBodyComponent
            Corps physique A.
        body_b : PhysicBodyComponent
            Corps physique B.
        com_a : Vector2D
            Centre de masse de A en espace monde.
        com_b : Vector2D
            Centre de masse de B en espace monde.
        contact_point : Vector2D
            Point de contact en espace monde.
        normal : Vector2D
            Normale de collision, normalisée, pointant de A vers B.
        depth : float
            Profondeur de pénétration (pixels).
        delta_time : float
            Pas de temps de la frame (secondes).
        inv_mass_a : float
            Masse inverse du corps A.
        inv_mass_b : float
            Masse inverse du corps B.
        inv_inertia_a : float
            Inertie inverse du corps A.
        inv_inertia_b : float
            Inertie inverse du corps B.
        material : PhysicMaterial
            Matériau physique combiné des deux corps.
        """
        kin = self._compute_contact_kinematics(
            body_a, body_b, com_a, com_b, contact_point, normal
        )

        # Calcul du bias de pénétration, pour forcer la séparation
        slop_px = 0.5  # commence à 0.5 px (à ajuster selon ton échelle)
        beta = 0.2  # commence à 0.2

        bias = self._compute_penetration_bias(depth, delta_time, slop_px, beta)

        # If separating, do nothing
        if kin.normal_velocity > 0.0 and bias <= Tolerence.GENERAL:
            return 0.0

        # Reduit la restitution si en dessous du seuil
        restitution = material.restitution
        if kin.normal_velocity > -material.bounce_velocity_threshold:
            restitution = 0.0

        k_n = self._compute_effective_mass(
            inv_mass_a,
            inv_mass_b,
            inv_inertia_a,
            inv_inertia_b,
            kin.lever_arm_a,
            kin.lever_arm_b,
            normal,
        )
        if k_n <= Tolerence.GENERAL:
            return 0.0

        jn = self._compute_normal_impulse(kin.normal_velocity, restitution, k_n, bias)

        if jn > Tolerence.GENERAL:
            impulse_n = normal * jn
            self._apply_impulses_at_contact(body_a, body_b, contact_point, impulse_n)

        # Recalcul de la cinématique après impulsion normale
        kin = self._compute_contact_kinematics(
            body_a, body_b, com_a, com_b, contact_point, normal
        )

        tangent = self._compute_tangent_axis(kin.relative_velocity, normal)
        if tangent is None:
            return jn

        vt = kin.relative_velocity.dot(tangent)

        k_t = self._compute_effective_mass(
            inv_mass_a,
            inv_mass_b,
            inv_inertia_a,
            inv_inertia_b,
            kin.lever_arm_a,
            kin.lever_arm_b,
            tangent,
        )
        if k_t <= Tolerence.GENERAL:
            return jn

        jt = self._compute_friction_impulse(vt, k_t, material.friction, jn)
        if abs(jt) > Tolerence.GENERAL:
            impulse_t = tangent * jt
            self._apply_impulses_at_contact(body_a, body_b, contact_point, impulse_t)

        return max(abs(jn), abs(jt))

    def _compute_contact_kinematics(
        self,
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        com_a: "Vector2D",
        com_b: "Vector2D",
        contact_point: "Vector2D",
        normal: "Vector2D",
    ) -> _ContactKinematics:
        """
        Compute relative velocity at the contact point.

        This includes both linear and angular contributions, so that impulses
        produce correct translation and rotation.

        Parameters
        ----------
        body_a : PhysicBodyComponent
            Physics body A.
        body_b : PhysicBodyComponent
            Physics body B.
        com_a : Vector2D
            Center of mass of A in world space.
        com_b : Vector2D
            Center of mass of B in world space.
        contact_point : Vector2D
            Contact point in world space.
        normal : Vector2D
            Collision normal, normalized, pointing from A to B.

        Returns
        -------
        ContactKinematics
            Kinematic data for the contact point.
        """
        lever_arm_a = contact_point - com_a
        lever_arm_b = contact_point - com_b

        v_a_point = body_a.velocity + (lever_arm_a.normal() * body_a.angular_velocity)
        v_b_point = body_b.velocity + (lever_arm_b.normal() * body_b.angular_velocity)
        relative_velocity = v_b_point - v_a_point
        normal_velocity = relative_velocity.dot(normal)

        return _ContactKinematics(
            lever_arm_a=lever_arm_a,
            lever_arm_b=lever_arm_b,
            relative_velocity=relative_velocity,
            normal_velocity=normal_velocity,
        )

    def _compute_normal_impulse(
        self,
        rel_normal_velocity: float,
        restitution: float,
        k_normal: float,
        bias: float = 0.0,
    ) -> float:
        """
        calcule l'impulsion normale pour annuler la vélocité normale.

        Cette impulsion peut inclure un facteur de restitution pour simuler
        le rebond.

        Parameters
        ----------
        rel_normal_velocity : float
            Vélocité relative le long de la normale au point de contact.
        restitution : float
            Coefficient de restitution (0 = inélastique, 1 = élastique).
        k_normal : float
            Dénominateur de la masse effective le long de l'axe normal.
        bias : float
            Vélocité de correction de pénétration (optionnelle).

        Returns
        -------
        float
            Magnitude de l'impulsion normale jn (>= 0).
        """
        if k_normal <= 0.0:
            return 0.0

        # Appliquer restitution uniquement sur la vitesse relative,
        # puis soustraire le biais de pénétration pour forcer la séparation.
        desired = (1.0 + restitution) * rel_normal_velocity - bias
        jn = -desired / k_normal

        if jn < Tolerence.GENERAL:
            jn = 0.0
        return jn

    def _compute_tangent_axis(
        self, rel_velocity: "Vector2D", normal: "Vector2D"
    ) -> Optional["Vector2D"]:
        """
        Calcule l'axe tangent normalisé à partir de la vélocité relative.

        La tangente est la composante de la vélocité relative orthogonale à la normale.
        Si la vitesse tangentielle est trop faible, retourne None.

        Parameters
        ----------
        rel_velocity : Vector2D
            Vélocité relative au point de contact.
        normal : Vector2D
            Collision normalisé (A -> B).

        Returns
        -------
        Optional[Vector2D]
            Axe tangent normalisé, ou None si la tangente est trop faible.
        """
        tangent = rel_velocity - normal * rel_velocity.dot(normal)

        if tangent.magnitude_squared() <= Tolerence.GENERAL * Tolerence.GENERAL:
            return None

        return tangent.normalized()

    def _compute_friction_impulse(
        self,
        rel_tangent_velocity: float,
        k_tangent: float,
        friction: float,
        normal_impulse: float,
    ) -> float:
        """
        Calcule la magnitude de l'impulsion de friction le long de l'axe tangent.

        Utilise un modèle simple de friction de Coulomb : |jt| <= mu * jn.

        Parameters
        ----------
        rel_tangent_velocity : float
            Vélocité tangentielle relative au contact.
        k_tangent : float
            Dénominateur de la masse effective le long de l'axe tangent.
        friction : float
            Coefficient de friction mu (>= 0).
        normal_impulse : float
            Magnitude de l'impulsion normale déjà calculée jn.

        Returns
        -------
        float
            Magnitude de l'impulsion tangentielle jt (peut être négative).
        """
        if k_tangent <= Tolerence.GENERAL:
            return 0.0

        jt = -rel_tangent_velocity / k_tangent

        max_friction = friction * normal_impulse
        jt = Numeric.clamp(jt, -max_friction, max_friction)
        return jt

    def _apply_impulses_at_contact(
        self,
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        contact_point: "Vector2D",
        impulse: "Vector2D",
    ) -> None:
        """
        Applique une impulsion aux deux corps au point de contact.

        Parameters
        ----------
        body_a : PhysicBodyComponent
            Corps physique A.
        body_b : PhysicBodyComponent
            Corps physique B.
        contact_point : Vector2D
            Point de contact en coordonnées de la scène.
        impulse : Vector2D
            Impulsion à appliquer.
        """
        body_a.apply_impulse_at_point(-impulse, contact_point)
        body_b.apply_impulse_at_point(impulse, contact_point)

    def _compute_effective_mass(
        self,
        inv_mass_a: float,
        inv_mass_b: float,
        inv_inertia_a: float,
        inv_inertia_b: float,
        lever_arm_a: Vector2D,
        lever_arm_b: Vector2D,
        axis: Vector2D,
    ) -> float:
        """
        Calcule le dénominateur de la masse effective pour l'impulsion.
        Cette valeur est utilisée pour déterminer l'effet de la masse
        et de l'inertie sur la réponse à une impulsion appliquée à un point.

        Cela représente la contribution combinée de la masse linéaire
        et de l'inertie rotative des deux corps impliqués dans la collision.

        Parameters
        ----------
        inv_mass_a : float
            Masse inverse du corps A.
        inv_mass_b : float
            Masse inverse du corps B.
        inv_inertia_a : float
            Inertie inverse du corps A.
        inv_inertia_b : float
            Inertie inverse du corps B.
        lever_arm_a : Vector2D
            Vecteur de position du point d'application par rapport
            au centre de masse du corps A.
        lever_arm_b : Vector2D
            Vecteur de position du point d'application par rapport
            au centre de masse du corps B.
        axis : Vector2D
            Axe le long duquel l'impulsion est appliquée (normalisé).

        Returns
        -------
        float
            Masse effective le long de l'axe donné.
        """
        lever_arm_cross_a = lever_arm_a.cross(axis)
        lever_arm_cross_b = lever_arm_b.cross(axis)

        inv_mass = inv_mass_a + inv_mass_b
        inertia_mass_a = (lever_arm_cross_a * lever_arm_cross_a) * inv_inertia_a
        inertia_mass_b = (lever_arm_cross_b * lever_arm_cross_b) * inv_inertia_b

        effective_mass = inv_mass + inertia_mass_a + inertia_mass_b

        # Tolerence générale (1e-9) ou de collision (1e-3) ?
        if effective_mass <= Tolerence.GENERAL:
            return 0.0
        return effective_mass
