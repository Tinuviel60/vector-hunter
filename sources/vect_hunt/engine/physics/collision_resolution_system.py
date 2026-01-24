import logging
from typing import TYPE_CHECKING, Optional, Tuple

from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.math.numeric import Numeric
from vect_hunt.engine.core.math.geometry import Geometry
from vect_hunt.engine.physics.collision_info import CollisionInfo

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.scenes.scene import Scene

logger = logging.getLogger(__name__)

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
            body_a,
            body_b,
            game_object_a,
            game_object_b,
            collision_info,
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
        slop = Tolerence.COLLISION * 2.0
        percent = 0.6
        corrected_depth = max(0.0, collision_info.depth - slop) * percent

        collision_eps = Tolerence.COLLISION * 0.1
        correction = collision_info.normal * corrected_depth
        if correction.magnitude_squared() <= collision_eps * collision_eps:
            return

        if body_a.is_kinematic and body_b.is_kinematic:
            return
        if body_a.is_kinematic:
            game_object_b.transform.move(correction)
            return
        if body_b.is_kinematic:
            game_object_a.transform.move(-correction)
            return

        general_eps = Tolerence.GENERAL
        inv_mass_a = 1.0 / body_a.mass if body_a.mass > general_eps else 0.0
        inv_mass_b = 1.0 / body_b.mass if body_b.mass > general_eps else 0.0
        inv_mass_sum = inv_mass_a + inv_mass_b

        if inv_mass_sum <= general_eps:
            return

        # Les deux objets sont dynamiques, partager la correction
        game_object_a.transform.move(-correction * (inv_mass_a / inv_mass_sum))
        game_object_b.transform.move(correction * (inv_mass_b / inv_mass_sum))

    def _compute_baumgarte_bias(
        self,
        depth: float,
        delta_time: float,
        slop: float = 0.01,
        baumgarte_scalar: float = 0.2,
    ) -> float:
        """
        Calcule le biais de Baumgarte pour la correction de position, afin de 
        stabiliser les collisions au fil du temps.

        Parameters
        ----------
        depth : float
            Profondeur de pénétration.
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        slop : float
            Marge de tolérance avant d'appliquer le biais (par défaut 0.01
        baumgarte_scalar : float
            Coefficient de Baumgarte (par défaut 0.2).

        Returns
        -------
        float
            Le biais de Baumgarte à appliquer.
        """
        if delta_time <= 0:
            return 0.0
        penetration_error = max(0.0, depth - slop)
        return (baumgarte_scalar / delta_time) * penetration_error
    
    def apply_impulse_response(
        self,
        collisions: list[tuple[int, int]],
        collision_info: dict[tuple[int, int], CollisionInfo],
        reverse_point: bool = True,
    ) -> None:
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
        """
        for id_obj_a, id_obj_b in collisions:
            info_collision = collision_info.get((id_obj_a, id_obj_b))
            if info_collision is None:

                continue

            context = self._get_collision_context(id_obj_a, id_obj_b)
            if context is None:
                continue

            _, _, body_a, body_b = context

            self._apply_velocity_response(body_a, body_b, info_collision, reverse_point)

    def _apply_velocity_response(
        self,
        body_a: PhysicBodyComponent,
        body_b: PhysicBodyComponent,
        info_collision: CollisionInfo,
        reverse_point: bool = True,
    ) -> None:
        """
        Applique restitution + friction d'une collision en utilisant 
        les points de contact.

        Parameters
        ----------
        body_a : PhysicBodyComponent
            PhysicBody du premier objet.
        body_b : PhysicBodyComponent
            PhysicBody du deuxième objet.
        info_collision : CollisionInfo
            Informations supplémentaires sur la collision (normal, depth, points).
        """

        if len(info_collision.points) == 0:
            return
        
        collision_eps = Tolerence.COLLISION
        general_eps = Tolerence.GENERAL
        if info_collision.normal.magnitude_squared() <= collision_eps * collision_eps:
            return

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
            return
        
        tr_a = body_a.parent.transform
        tr_b = body_b.parent.transform
        
        com_a = Geometry.to_scene(body_a.mass_center, tr_a.position, tr_a.rotation)
        com_b = Geometry.to_scene(body_b.mass_center, tr_b.position, tr_b.rotation)

        share = 1.0 / float(len(info_collision.points)) 

        # --- Paramètres "stabilité" ---
        # Seuil de "quasi repos" pour activer friction statique (à ajuster selon tes unités px/s)
        static_speed_threshold = 0.5
        # Approximations: mu_static > mu_dynamic
        mu_dynamic = float(contact_material.friction)
        mu_static = mu_dynamic * 1.75

        # Éviter les micro rebonds au repos (à ajuster selon tes unités px/s)
        bounce_speed_threshold = float(getattr(contact_material, "bounciness_threshold", 0.0))
        min_bounce_threshold = 1.0
        effective_bounce_threshold = max(bounce_speed_threshold, min_bounce_threshold)

        # Appliquer l'impulsion pour chaque point de contact
        points = list(info_collision.points)

        tangent_axis = normal.normal()  # axe tangent au plan de contact
        points.sort(key=lambda p: p.dot(tangent_axis))
        if reverse_point:
            points = points[::-1]
        for point in points:
            rot_a = point - com_a
            rot_b = point - com_b

            velocity_a = self._velocity_at_point(body_a, rot_a)
            velocity_b = self._velocity_at_point(body_b, rot_b)

            relative_velocity = velocity_b - velocity_a
            rel_normal_speed = relative_velocity.dot(normal)

            # Si les objets s'éloignent, ne pas appliquer d'impulsion normale.
            if rel_normal_speed > collision_eps:
                continue

            # clamp au repos
            resting_normal_threshold = 0.5
            if abs(rel_normal_speed) < resting_normal_threshold:
                rel_normal_speed = 0.0

            # Calcul des masses inverses effectives
            denom_n = self._effective_mass_denominator(
                inv_mass_a,
                inv_mass_b,
                inv_inertia_a,
                inv_inertia_b,
                rot_a,
                rot_b,
                normal
            )
            if denom_n <= general_eps:
                continue
            
            restitution = contact_material.restitution
            if abs(rel_normal_speed) < effective_bounce_threshold:
                restitution = 0.0

            jn_raw = (-(1.0 + restitution) * rel_normal_speed) / denom_n
            jn_raw = max(0.0, jn_raw)  # Empêcher l'impulsion de traction
            jn = jn_raw * share  # Partager l'impulsion entre les points de contact
            impulse_normal = normal * jn

            self._apply_impulse_at_point(body_a, -impulse_normal, rot_a)
            self._apply_impulse_at_point(body_b, impulse_normal, rot_b)

            # Friction (recalcule après impulsion normale)
            va2 = self._velocity_at_point(body_a, rot_a)
            vb2 = self._velocity_at_point(body_b, rot_b)
            rv2 = vb2 - va2

            tangent = rv2 - normal * rv2.dot(normal)
            if tangent.magnitude_squared() <= collision_eps * collision_eps:
                continue

            tangent_dir = tangent.normalized()
            rel_tangent_speed = rv2.dot(tangent_dir)
            
            resting_tangent_threshold = 0.5
            if abs(rel_tangent_speed) < resting_tangent_threshold:
                rel_tangent_speed = 0.0
                
            denom_t = self._effective_mass_denominator(
                inv_mass_a,
                inv_mass_b,
                inv_inertia_a,
                inv_inertia_b,
                rot_a,
                rot_b,
                tangent_dir
            )
            if denom_t <= general_eps:
                continue

            jt_raw = (-rel_tangent_speed) / denom_t
            jt = jt_raw * share  # Partager l'impulsion entre les points de contact



            # --- Stick-slip (friction statique) ---
            # Si on est quasi au repos en tangentiel, on autorise une friction plus forte
            # pour "coller" le contact, sinon friction dynamique classique.
            use_static = abs(rel_tangent_speed) < static_speed_threshold
            mu = mu_static if use_static else mu_dynamic

            # Cône de friction : |jt| <= mu * jn
            # On se base sur jn_raw (avant share) puis on applique share de façon cohérente.
            max_jt = mu * jn_raw * share
            jt = Numeric.clamp(jt, -max_jt, max_jt)

            impulse_t = tangent_dir * jt

            self._apply_impulse_at_point(body_a, -impulse_t, rot_a)
            self._apply_impulse_at_point(body_b, impulse_t, rot_b)

    def _effective_mass_denominator(
        self,
        inv_mass_a: float,
        inv_mass_b: float,
        inv_inertia_a: float,
        inv_inertia_b: float,
        rot_a: Vector2D,
        rot_b: Vector2D,
        direction: Vector2D,
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
        rot_a : Vector2D
            Vecteur du centre de masse au point de contact pour A.
        rot_b : Vector2D
            Vecteur du centre de masse au point de contact pour B.
        direction : Vector2D
            Direction de l'impulsion (normale ou tangentielle).
        
        Returns
        -------
        float
            Le dénominateur de la masse effective.
        """
        term_a = inv_mass_a
        term_b = inv_mass_b

        cross_a = rot_a.cross(direction)
        cross_b = rot_b.cross(direction)

        term_a += inv_inertia_a * cross_a * cross_a
        term_b += inv_inertia_b * cross_b * cross_b

        return term_a + term_b
    
    @staticmethod
    def _apply_impulse_at_point(
        body: PhysicBodyComponent, 
        impulse: Vector2D, 
        r: Vector2D
    ) -> None:
        """
        Applique une impulsion à un corps à un point donné,
        générant à la fois une modification de la vélocité linéaire
        et une modification de la vélocité angulaire.

        Formules :
        - Vélocité linéaire : v += impulse / mass
        - Vélocité angulaire : ω += (r * impulse) / inertia

        Parameters
        ----------
        body : PhysicBodyComponent
            Le corps physique auquel l'impulsion est appliquée.
        impulse : Vector2D
            L'impulsion à appliquer.
        r : Vector2D
            Vecteur du centre de masse au point d'application de l'impulsion.
        """
        if body.is_kinematic:
            return

        body.apply_impulse(impulse)

        if body.inertia <= Tolerence.GENERAL:
            return

        torque_impulse = r.cross(impulse)
        body.angular_velocity += torque_impulse / body.inertia

    @staticmethod
    def _velocity_at_point(
        body: PhysicBodyComponent,
        r: Vector2D
    ) -> Vector2D:
        """
        Calcule la vélocité d'un point sur le corps,
        en tenant compte de la vélocité linéaire et de la rotation.

        Formule :
        v_point = v_linear + ω * r

        Parameters
        ----------
        body : PhysicBodyComponent
            Le corps physique.
        r : Vector2D
            Vecteur du centre de masse au point d'intérêt.

        Returns
        -------
        Vector2D
            La vélocité au point spécifié.
        """
        perpendicular_r = r.normal()  # Rotation de 90 degrés pour le produit vectoriel 2D
        rotational_velocity = perpendicular_r * body.angular_velocity
        return body.velocity + rotational_velocity
