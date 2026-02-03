import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Tuple, cast

from vect_hunt.engine.core.collisions import Collision
from vect_hunt.engine.core.math.numeric import Numeric
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.collisions.collision_info import CollisionInfo

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.physics.physic_material import PhysicMaterial
    from vect_hunt.engine.scenes.scene import Scene
    from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
    from vect_hunt.engine.components.collider.collider_component import ColliderComponent

logger = logging.getLogger(__name__)


@dataclass
class _ContactImpulse:
    """Conteneur pour les impulsions de contact normales et tangentielles."""

    jn: float = 0.0
    jt: float = 0.0
    tangent_axis: Optional["Vector2D"] = None
    position: "Vector2D" = field(default_factory=lambda: Vector2D(0.0, 0.0))


_ContactKey = tuple[int, int, int]


@dataclass(frozen=True)
class _ContactKinematics:
    """Conteneur d'information cinématique pour un point de contact unique.

    Ce conteneur stocke les bras de levier en espace monde et la vitesse relative
    calculée au point de contact. Il existe pour garder le code du solveur
    d'impulsions lisible et explicite.

    Attributes
    ----------
    lever_arm_a : Vector2D
        Vecteur du centre de masse du corps A (monde) au point de contact (monde).
    lever_arm_b : Vector2D
        Vecteur du centre de masse du corps B (monde) au point de contact (monde).
    relative_velocity : Vector2D
        Vitesse relative au point de contact (vB_point - vA_point).
    normal_velocity : float
        Vitesse relative projetée sur la normale du contact.
    """

    lever_arm_a: Vector2D
    lever_arm_b: Vector2D
    relative_velocity: Vector2D
    normal_velocity: float


class CollisionResolutionSystem:
    """Système de correction des collisions.

    Applique des ajustements de position pour résoudre les collisions détectées
    par le CollisionSystem. Dépendant d'un physic body, d'un sytème de collision,
    et de la physique d'un GameObject (masse, friction, rebond...).

    Attributes
    ----------
    scene : Scene
        Scène de jeu associé.
    """

    def __init__(self, scene: "Scene") -> None:
        """Initialise le système de résolution des collisions.

        Parameters
        ----------
        scene : Scene
            La scène dans laquelle les objets existent.
        """
        self.scene = scene
        # Permet de mettre en cache les impuslions pour le warm starting
        self._contact_impulses: dict[_ContactKey, _ContactImpulse] = {}

    def correct_collisions(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
    ) -> bool:
        """Applique la résolution à partir d'un jeu de collisions déjà détectées.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires d'IDs de colliders en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision associées aux paires.

        Returns
        -------
        bool
            True si au moins une correction de collision a été appliquée, False sinon.
        """
        correction_applied = False

        # Résoudre chaque collision
        for col_id_a, col_id_b in collisions:
            info = collision_info.get((col_id_a, col_id_b))
            if info is None:
                continue
            if self._resolve_collision(col_id_a, col_id_b, info):
                correction_applied = True

        return correction_applied

    def _resolve_collision(
        self,
        col_id_a: int,
        col_id_b: int,
        collision_info: CollisionInfo,
    ) -> bool:
        """Résout une collision entre deux colliders avec correction de position,
        en utilisant les infos détaillées.

        Parameters
        ----------
        col_id_a : int
            ID du premier collider en collision.
        col_id_b : int
            ID du deuxième collider en collision.
        collision_info : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).

        returns
        -------
        bool
            True si une correction a été appliquée, False sinon.
        """
        # Recupérer les Collider et leurs PhysicBodyComponents
        context = self._get_collision_context(col_id_a, col_id_b)
        if context is None:
            return False

        col_a, col_b, parent_a, parent_b, body_a, body_b = context

        # Si pas de pénétration, ne rien faire
        if collision_info.depth <= 0:
            return False

        # Appliquer la correction de la normal
        correction_applied = self._apply_position_correction(
            body_a,
            body_b,
            parent_a,
            parent_b,
            collision_info,
        )

        return correction_applied

    def _get_collision_context(
        self,
        col_id_a: int,
        col_id_b: int,
    ) -> Optional[
        Tuple[
            "ColliderComponent",
            "ColliderComponent",
            "GameObject",
            "GameObject",
            "PhysicBodyComponent",
            "PhysicBodyComponent",
        ]
    ]:
        """Récupère le contexte de collision (colliders et PhysicBody associés).

        Parameters
        ----------
        col_id_a : int
            ID du premier collider en collision.
        col_id_b : int
            ID du deuxième collider en collision.

        Returns
        -------
        tuple or None
            (collider_a, collider_b, parent_a, parent_b, body_a, body_b) si disponible,
            sinon None si un PhysicBody manque.
        """
        collider_a = cast("ColliderComponent", self.scene.components.get(col_id_a))
        collider_b = cast("ColliderComponent", self.scene.components.get(col_id_b))

        if not collider_a or not collider_b:
            return None

        parent_a = collider_a.parent
        parent_b = collider_b.parent

        body_a = cast(
            "PhysicBodyComponent | None", parent_a.get_component("physic_body")
        )
        body_b = cast(
            "PhysicBodyComponent | None", parent_b.get_component("physic_body")
        )

        if not body_a or not body_b:
            return None

        return collider_a, collider_b, parent_a, parent_b, body_a, body_b

    def _resolve_collision_info(
        self,
        info_collision: CollisionInfo,
        col_a: "ColliderComponent",
        col_b: "ColliderComponent",
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
    ) -> CollisionInfo:
        """Oriente et nettoie la normale pour garantir une convention A -> B.

        Stratégie
        ----------
        - On n'édite pas CollisionInfo in-place.
        - On oriente la normale avec COM->COM (corps composé), fallback sur centre
          collider si COM trop proche.
        """
        info = info_collision.copy()

        eps = Tolerence.COLLISION
        eps2 = eps * eps
        if info.normal.magnitude_squared() <= eps2:
            info.normal = Vector2D(1.0, 0.0)
            return info

        info.normal.normalize()

        # COM -> COM (corps composé)
        parent_a = col_a.parent
        parent_b = col_b.parent
        com_a = parent_a.transform.to_scene_point(body_a.mass_center)
        com_b = parent_b.transform.to_scene_point(body_b.mass_center)
        delta = com_b - com_a

        # Fallback si COM trop proche (cas ambigu)
        if delta.magnitude_squared() <= Tolerence.GENERAL * Tolerence.GENERAL:
            pos_a = col_a.get_scene_transform().position
            pos_b = col_b.get_scene_transform().position
            delta = pos_b - pos_a

        dot = info.normal.dot(delta)
        if dot < 0.0:
            info.normal = -info.normal
            if info.reference_from_a is not None:
                info.reference_from_a = not info.reference_from_a

        if info.points is None or len(info.points) == 0:
            info.points = Collision.generate_contact_points(col_a, col_b, info)

        return info

    def _apply_position_correction(
        self,
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        collision_info: CollisionInfo,
    ) -> bool:
        """Corrige la position des objets en fonction de la profondeur de collision.

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
        slop = 0.2
        percent = 0.2

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

    def resolve_all_collision_info(
        self,
        collisions: set[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
    ) -> dict[tuple[int, int], CollisionInfo]:
        """Résout toutes les informations de collision pour un ensemble de collisions.

        Parameters
        ----------
        collisions : set[tuple[int, int]]
            Paires d'IDs d'objets en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision associées aux paires.

        Returns
        -------
        dict[tuple[int, int], CollisionInfo]
            Informations de collision mises à jour associées aux paires.
        """
        for col_id_a, col_id_b in collisions:
            info = collision_info.get((col_id_a, col_id_b))
            if info is None:
                continue

            context = self._get_collision_context(col_id_a, col_id_b)
            if context is None:
                continue

            col_a, col_b, parent_a, parent_b, body_a, body_b = context

            # Résoudre la normale, la profondeur de collision et calculer les points
            info = self._resolve_collision_info(info, col_a, col_b, body_a, body_b)
            collision_info[(col_id_a, col_id_b)] = info

        return collision_info

    def apply_impulse_response(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
        collider_is_new_contact: set[tuple[int, int]],
        delta_time: float,
    ) -> bool:
        """Applique la réponse d'impulsion pour un ensemble de collisions.

        Utilise 1 à 2 points de contact. Génère aussi de la rotation via l'impulsion
        appliquée au point.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires d'IDs d'objets en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision associées aux paires.
        collider_is_new_contact : set[tuple[int, int]]
            Nouvelles collisions détectées cette frame.
        delta_time : float
            Pas de temps de la frame (secondes).
        reverse_point : bool
            Inverse l'ordre des points de contact pour la résolution.
        """
        impulsion_max = 0.0

        for col_id_a, col_id_b in collisions:
            pair_col = (col_id_a, col_id_b)
            info = collision_info.get(pair_col)
            if info is None:
                continue

            context = self._get_collision_context(col_id_a, col_id_b)
            if context is None:
                continue

            col_a, col_b, parent_a, parent_b, body_a, body_b = context

            if info.points is None or len(info.points) == 0 or info.depth <= 0:
                continue

            is_new_contact = pair_col in collider_is_new_contact

            impulsion = self._apply_velocity_response(
                pair_col,
                parent_a,
                parent_b,
                body_a,
                body_b,
                info,
                is_new_contact,
                delta_time,
            )

            if impulsion > impulsion_max:
                impulsion_max = impulsion

        return impulsion_max > 1  # TODO : Valeurs arbitraire à retravailler

    def _apply_velocity_response(
        self,
        pair_col: tuple[int, int],
        game_object_a: "GameObject",
        game_object_b: "GameObject",
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        info_collision: CollisionInfo,
        is_new_contact: bool,
        delta_time: float,
    ) -> float:
        """Applique restitution + friction d'une collision en utilisant les points
        de contact.

        Parameters
        ----------
        pair_col : tuple[int, int]
            La paire d'IDs des colliders en collision.
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
        is_new_contact: bool
            Indique si la collision est nouvelle cette frame.
        delta_time : float
            Pas de temps de la frame (secondes).

        Returns
        -------
        float
            La magnitude maximale de l'impulsion appliquée.
        """
        if info_collision.points is None or len(info_collision.points) == 0:
            return 0.0

        # Convention: la normale et les points doivent déjà être "résolus" (A->B)
        normal = info_collision.normal.normalized()
        contact_material = body_a.material.combine_with(body_b.material)

        # Si les deux corps sont cinématiques, ne rien faire
        if (
            body_a.invert_mass()
            + body_b.invert_mass()
            + body_a.invert_inertia()
            + body_b.invert_inertia()
        ) <= Tolerence.GENERAL:
            return 0.0

        # COM monde
        com_a = game_object_a.transform.to_scene_point(body_a.mass_center)
        com_b = game_object_b.transform.to_scene_point(body_b.mass_center)

        max_delta_impulse = 0.0
        nb_contacts = len(info_collision.points)

        for contact_index, point in enumerate(info_collision.points):
            impulsion = self.solve_contact_point(
                body_a=body_a,
                body_b=body_b,
                com_a=com_a,
                com_b=com_b,
                contact_point=point,
                normal=normal,
                depth=info_collision.depth,
                delta_time=delta_time,
                material=contact_material,
                nb_contacts=nb_contacts,
                pair_col=pair_col,
                id_contact=contact_index,
                is_new_contact=is_new_contact,
            )

            if impulsion > max_delta_impulse:
                max_delta_impulse = impulsion

        return max_delta_impulse

    def _compute_penetration_bias(
        self,
        depth: float,
        delta_time: float,
        slop: float,
        beta: float,
        max_bias: float,
    ) -> float:
        """Calcule le bias de pénétration de Baumgarte utilisé pour corriger la
        pénétration.

        Ce biais agit comme une vélocité de fermeture supplémentaire le long de la
        normale de contact, pour forcer le solveur à générer une impulsion de
        séparation lorsque les objets sont déjà en pénétration.

        Parameters
        ----------
        depth : float
            Profondeur de pénétration (pixels). Doit être >= 0 pour un contact valide.
        delta_time : float
            Pas de temps de la frame (secondes).
        slop : float
            Tolérance de pénétration autorisée (pixels). La profondeur en dessous de
            cette valeur est ignorée.
        beta : float
            Facteur de biais (sans dimension). Les valeurs typiques sont dans
            [0.1, 0.3].
        max_bias : float
            Biais maximal autorisé (pixels/secondes).

        Returns
        -------
        float
            Vélocité de correction à appliquer le long de la normale
            (pixels/secondes).
        """
        if delta_time <= Tolerence.GENERAL:
            return 0.0

        allowed = max(0.0, depth - slop)
        if allowed <= Tolerence.GENERAL:
            return 0.0

        bias = (beta / delta_time) * allowed
        return min(bias, max_bias)

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
        material: "PhysicMaterial",
        nb_contacts: int,
        pair_col: Tuple[int, int],
        id_contact: int,
        is_new_contact: bool,
    ) -> float:
        """Résout un point de contact via impulsions séquentielles avec cache
        (warm starting).

        Implémentation
        --------------
        - On lit (jn_accum, jt_accum) depuis le cache pour ce contact.
        - On calcule des *deltas* (delta_jn, delta_jt) à appliquer à cette itération.
        - On met à jour les accumulateurs et on applique les deltas aux corps.
        - Le cache stocke les accumulateurs (solution courante).

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
        material : PhysicMaterial
            Matériau physique combiné des deux corps.
        nb_contacts : int
            Nombre de points de contact dans cette collision.
        pair_col : Tuple[int, int]
            Identifiant unique de la paire de corps en collision.
        contact_index: int
            Index du point de contact dans la liste des contacts.
        is_new_contact : bool
            Défini si c'est une nouvelle collision.

        Returns:
        --------
        tuplefloat
            La magnitude maximum appliqué.
        """
        # Cache key
        col_id_a, col_id_b = pair_col
        contact_key: _ContactKey = (col_id_a, col_id_b, id_contact)

        cached = self._contact_impulses.get(contact_key)
        if cached is None:
            cached = _ContactImpulse(0.0, 0.0, position=contact_point)
        else:
            cached.position = contact_point

        # Cinématique au point
        kin = self._compute_contact_kinematics(
            body_a, body_b, com_a, com_b, contact_point, normal
        )

        # Bias (Baumgarte) pour forcer la séparation
        slop_px = 0.5  # TODO : ajuster avec l'echelle ?
        beta = 0.1
        max_bias = 3.0
        bias = self._compute_penetration_bias(depth, delta_time, slop_px, beta, max_bias)
        bias_per_contact = bias / max(1, nb_contacts)

        # Restitution (sur nouveau contact et uniquement si fermeture)
        restitution = material.restitution
        if not is_new_contact:
            restitution = 0.0
        else:
            # Si séparation déjà en cours, ne pas appliquer de restitution
            if kin.normal_velocity > 0.0:
                restitution = 0.0

            # Réduit la restitution si en dessous du seuil
            if kin.normal_velocity > -material.bounce_velocity_threshold:
                restitution = 0.0

        # Masse effective normale
        k_n = self._compute_effective_mass(
            body_a.invert_mass(),
            body_b.invert_mass(),
            body_a.invert_inertia(),
            body_b.invert_inertia(),
            kin.lever_arm_a,
            kin.lever_arm_b,
            normal,
        )

        if k_n <= Tolerence.GENERAL:
            return 0.0

        # -------------------------
        # 1) Impulsion normale (delta + accumulateur)
        # -------------------------
        vn = kin.normal_velocity

        # Terme "bounce" (restitution) uniquement en fermeture
        vn_target = 0.0
        if vn < 0.0:
            vn_target = -restitution * vn

        # Forme standard: Δjn = (bounce + bias - vn) / k_n
        # (intuition: on veut compenser vn, + ajouter separation via bias)
        delta_jn = (vn_target + bias_per_contact - vn) / k_n

        # Accumulation avec contrainte unilatérale jn >= 0
        old_jn = cached.jn
        cached.jn = max(0.0, old_jn + delta_jn)
        delta_jn = cached.jn - old_jn

        if delta_jn > Tolerence.GENERAL:
            self._apply_impulses_at_contact(
                body_a, body_b, contact_point, normal * delta_jn
            )

        # Recalcule des contacts cinématiques après impulsion de la normal
        kin = self._compute_contact_kinematics(
            body_a, body_b, com_a, com_b, contact_point, normal
        )

        tangent = self._compute_tangent_axis(kin.relative_velocity, normal)
        if tangent is None:
            self._contact_impulses[contact_key] = cached
            return abs(delta_jn)

        cached.tangent_axis = tangent

        vt = kin.relative_velocity.dot(tangent)

        # Masse effective tangentielle
        k_t = self._compute_effective_mass(
            body_a.invert_mass(),
            body_b.invert_mass(),
            body_a.invert_inertia(),
            body_b.invert_inertia(),
            kin.lever_arm_a,
            kin.lever_arm_b,
            tangent,
        )

        if k_t <= Tolerence.GENERAL:
            self._contact_impulses[contact_key] = cached
            return abs(delta_jn)

        # -------------------------
        # 2) Impulsion de friction (accumulateur + clamp Coulomb)
        # -------------------------

        # Candidat accumulateur: jt' = jt_old - vt / k_t
        old_jt = cached.jt
        jt_candidate = old_jt - (vt / k_t)

        # Choix statique vs dynamique via le seuil Coulomb
        mu_s = material.static_friction
        mu_d = material.dynamic_friction
        max_static = mu_s * cached.jn

        if abs(jt_candidate) <= max_static:
            jt_new = jt_candidate
        else:
            max_dynamic = mu_d * cached.jn
            jt_new = Numeric.clamp(jt_candidate, -max_dynamic, max_dynamic)

        cached.jt = jt_new
        delta_jt = jt_new - old_jt

        if abs(delta_jt) > Tolerence.GENERAL:
            self._apply_impulses_at_contact(
                body_a, body_b, contact_point, tangent * delta_jt
            )

        self._contact_impulses[contact_key] = cached
        return max(abs(delta_jn), abs(delta_jt))

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
        Calcule la

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

        v_a_point = body_a.velocity + (
            lever_arm_a.normal() * body_a.angular_velocity
        )
        v_b_point = body_b.velocity + (
            lever_arm_b.normal() * body_b.angular_velocity
        )

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
        """calcule l'impulsion normale pour annuler la vélocité normale.

        Cette impulsion peut inclure un facteur de restitution pour simuler le rebond.

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
        if k_normal <= Tolerence.GENERAL:
            return 0.0

        # Rebond uniquement si fermeture
        bounce = 0.0
        if rel_normal_velocity < 0.0:
            bounce = -(1.0 + restitution) * rel_normal_velocity

        # puis soustraire le biais de pénétration pour forcer la séparation.
        target = bounce + bias
        jn = target / k_normal

        return max(0.0, jn)

    def _compute_tangent_axis(
        self, rel_velocity: "Vector2D", normal: "Vector2D"
    ) -> Optional["Vector2D"]:
        """Calcule l'axe tangent normalisé à partir de la vélocité relative.

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
        static_friction: float,
        dynamic_friction: float,
        normal_impulse_cached: float,
    ) -> float:
        """Calcule la magnitude de l'impulsion de friction le long de l'axe tangent.

        Modèle
        ------
        - Impulsion "idéale" : jt_ideal = -vt / k_t
        - Si |jt_ideal| <= mu_static * jn : adhérence (friction statique)
        - Sinon : glissement, clamp avec mu_dynamic * jn

        Parameters
        ----------
        rel_tangent_velocity : float
            Vélocité tangentielle relative au contact (vt).
        k_tangent : float
            Dénominateur de la masse effective le long de l'axe tangent.
        static_friction : float
            Coefficient de friction statique (mu_s).
        dynamic_friction : float
            Coefficient de friction dynamique (mu_d).
        normal_impulse_cached : float
            Magnitude de l'impulsion normale déjà calculée (jn).

        Returns
        -------
        float
            Magnitude de l'impulsion tangentielle jt (peut être négative).
        """
        if k_tangent <= Tolerence.GENERAL:
            return 0.0

        jt_ideal = -rel_tangent_velocity / k_tangent
        max_friction = static_friction * normal_impulse_cached

        if abs(jt_ideal) <= max_friction:
            return jt_ideal

        max_friction = dynamic_friction * normal_impulse_cached
        return Numeric.clamp(jt_ideal, -max_friction, max_friction)

    def _apply_impulses_at_contact(
        self,
        body_a: "PhysicBodyComponent",
        body_b: "PhysicBodyComponent",
        contact_point: "Vector2D",
        impulse: "Vector2D",
    ) -> None:
        """Applique une impulsion aux deux corps au point de contact.

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
        """Calcule le dénominateur de la masse effective pour l'impulsion.

        Cette valeur est utilisée pour déterminer l'effet de la masse et de
        l'inertie sur la réponse à une impulsion appliquée à un point. Cela
        représente la contribution combinée de la masse linéaire et de l'inertie
        rotative des deux corps impliqués dans la collision.

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
            Vecteur de position du point d'application par rapport au centre de masse
            du corps A.
        lever_arm_b : Vector2D
            Vecteur de position du point d'application par rapport au centre de masse
            du corps B.
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

    def warm_start_contacts(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
        warm_start_factor: float = 1.0,
    ) -> None:
        """Applique le warm starting à partir du cache d'impulsions.

        Cette méthode doit être appelée AVANT les itérations d'impulsions.
        Elle applique l'impulsion totale (jn, jt) stockée de la frame précédente,
        afin d'accélérer la convergence et stabiliser les piles.

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires de colliders en collision pour cette frame.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Informations de collision résolues (normale orientée, points existants).
        warm_start_factor : float, optional
            Facteur multiplicatif appliqué aux impulsions cachées (0..1).
            Valeurs typiques : 0.7 à 1.0.
        """
        warm_start_factor = Numeric.clamp(warm_start_factor, 0.0, 1.0)

        for col_id_a, col_id_b in collisions:
            pair_col = (col_id_a, col_id_b)
            info = collision_info.get(pair_col)

            if info is None or info.depth <= 0.0 or not info.points:
                continue

            context = self._get_collision_context(col_id_a, col_id_b)
            if context is None:
                continue

            _, _, parent_a, parent_b, body_a, body_b = context
            normal = info.normal.normalized()

            # Centres de masse monde
            com_a = parent_a.transform.to_scene_point(body_a.mass_center)
            com_b = parent_b.transform.to_scene_point(body_b.mass_center)
            
            # Attribution des points corrects pour avoir un warms startings stables
            assigned = self._assign_contact_points_to_cache_slots(
                col_id_a=col_id_a,
                col_id_b=col_id_b,
                points=list(info.points),
                max_contacts=2,
            )

            print('parent_a:', parent_a.name, 'parent_b:', parent_b.name, "points asssigned:", assigned)

            logger.debug(
                "[WS] %s vs %s raw_points=%s assigned=%s",
                parent_a.name,
                parent_b.name,
                info.points,
                [(idx, p) for idx, p in assigned],
            )

            for contact_index, point in assigned:
                contact_key: _ContactKey = (col_id_a, col_id_b, contact_index)
                cached = self._contact_impulses.get(contact_key)
                if cached is None:
                    continue

                contact_key: _ContactKey = (col_id_a, col_id_b, contact_index)
                cached = self._contact_impulses.get(contact_key)

                if cached is None:
                    continue

                # Recalcule la tangente comme dans le solveur
                kin = self._compute_contact_kinematics(body_a, body_b, com_a, com_b, point, normal)
                tangent = self._compute_tangent_axis(kin.relative_velocity, normal)

                # Si on a une tangente, stabiliser son sens par rapport à la frame précédente
                if tangent is not None and cached.tangent_axis is not None:
                    if tangent.dot(cached.tangent_axis) < 0.0:
                        tangent = -tangent
                        cached.jt = -cached.jt

                # Appliquer l'impulsion warm start
                jn_ws = cached.jn * warm_start_factor
                jt_ws = cached.jt * warm_start_factor

                impulse = normal * jn_ws
                if tangent is not None:
                    impulse += tangent * jt_ws
                    cached.tangent_axis = tangent
                else:
                    cached.tangent_axis = None

                # Appliquer l'impulsion totale mise en cache
                self._apply_impulses_at_contact(body_a, body_b, point, impulse)

    def build_active_contact_keys(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
    ) -> set[_ContactKey]:
        """Construit l'ensemble des clés de contact actives pour cette frame.

        Notes
        -----
        - Utilise la convention actuelle : 1 à 2 points de contact par collision.
        - Les clés sont (col_id_a, col_id_b, contact_index).

        Parameters
        ----------
        collisions : list[tuple[int, int]]
            Paires de colliders en collision.
        collision_info : dict[tuple[int, int], CollisionInfo]
            Infos de collision contenant les points.

        Returns
        -------
        set[_ContactKey]
            Ensemble des clés actives.
        """
        active_keys: set[_ContactKey] = set()

        for col_id_a, col_id_b in collisions:
            info = collision_info.get((col_id_a, col_id_b))

            if info is None or not info.points or info.depth <= 0.0:
                continue

            for contact_index in range(len(info.points)):
                active_keys.add((col_id_a, col_id_b, contact_index))

        return active_keys

    def prune_contact_cache(self, active_keys: set[_ContactKey]) -> None:
        """Purge le cache d'impulsions pour ne garder que les contacts actifs.

        Parameters
        ----------
        active_keys : set[_ContactKey]
            Ensemble des clés de contact encore actives pour cette frame.
        """
        if not self._contact_impulses:
            return

        self._contact_impulses = {
            k: v for k, v in self._contact_impulses.items() if k in active_keys
        }

    def _assign_contact_points_to_cache_slots(
        self,
        col_id_a: int,
        col_id_b: int,
        points: list["Vector2D"],
        max_contacts: int = 2,
    ) -> list[tuple[int, "Vector2D"]]:
        """Attribue les points de contact courants aux slots de cache (0/1).

        Objectif
        --------
        Stabiliser l'identité des contacts d'une frame à l'autre pour le warm start,
        en matchant les points courants sur les positions mises en cache.

        Règles
        ------
        - Si 2 points et 2 caches (idx 0 et 1): choisir direct vs swap selon le coût
          (somme des distances² aux positions cachées) minimal.
        - Si 1 point: l'associer au slot le plus proche (si cache existant), sinon slot 0.
        - Si 2 points et 1 cache: le point le plus proche récupère ce slot, l'autre va
          sur l'autre slot disponible.
        - Si aucun cache: conserver l'ordre courant (slots 0..n-1).

        Notes
        -----
        - Cette attribution ne modifie pas `points` in-place.
        - Retourne une liste de couples (slot_index, point) ordonnée par slot_index.

        Parameters
        ----------
        col_id_a : int
            ID du collider A.
        col_id_b : int
            ID du collider B.
        points : list[Vector2D]
            Points de contact courants (1..N).
        max_contacts : int, optional
            Nombre maximum de points gérés (par défaut 2).

        Returns
        -------
        list[tuple[int, Vector2D]]
            Liste des points associés à des slots (0/1).
        """
        if not points:
            return []

        # On ne gère que 2 contacts (ton moteur actuel).
        pts = points[:max_contacts]
        n = len(pts)

        key0: _ContactKey = (col_id_a, col_id_b, 0)
        key1: _ContactKey = (col_id_a, col_id_b, 1)
        c0 = self._contact_impulses.get(key0)
        c1 = self._contact_impulses.get(key1)

        has0 = c0 is not None
        has1 = c1 is not None

        # Aucun cache: garder l'ordre courant
        if not has0 and not has1:
            return [(i, pts[i]) for i in range(n)]

        # 1 point: choisir le slot le plus proche si possible
        if n == 1:
            p = pts[0]
            if has0 and has1:
                d0 = (p - c0.position).magnitude_squared()
                d1 = (p - c1.position).magnitude_squared()
                slot = 0 if d0 <= d1 else 1
                return [(slot, p)]
            if has0:
                return [(0, p)]
            # has1 uniquement
            return [(1, p)]

        # 2 points
        p0, p1 = pts[0], pts[1]

        # 2 caches -> choisir direct vs swap
        if has0 and has1:
            direct = (p0 - c0.position).magnitude_squared() + (p1 - c1.position).magnitude_squared()
            swap = (p0 - c1.position).magnitude_squared() + (p1 - c0.position).magnitude_squared()

            if swap < direct:
                return [(0, p1), (1, p0)]
            return [(0, p0), (1, p1)]

        # 1 cache: associer le point le plus proche à ce slot
        elif has0 and not has1:
            d0 = (p0 - c0.position).magnitude_squared()
            d1 = (p1 - c0.position).magnitude_squared()
            if d0 <= d1:
                return [(0, p0), (1, p1)]
            return [(0, p1), (1, p0)]

        elif not has0 and has1:
            d0 = (p0 - c1.position).magnitude_squared()
            d1 = (p1 - c1.position).magnitude_squared()
            if d0 <= d1:
                return [(1, p0), (0, p1)]
            return [(1, p1), (0, p0)]
        # Sécurité, ne devriat pas se déclencher
        else:
            logger.warning("Assignation des points mal gérée, cas inattendu.")
            return []