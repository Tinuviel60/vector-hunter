from typing import List, Optional, Tuple

from vect_hunt.engine.components.collider.box_collider_component import (
    BoxColliderComponent,
)
from vect_hunt.engine.components.collider.circle_collider_component import (
    CircleColliderComponent,
)
from vect_hunt.engine.components.collider.collider_component import ColliderComponent
from vect_hunt.engine.core.collisions.collision_info import CollisionInfo
from vect_hunt.engine.core.geometries.box_shape import BoxShape
from vect_hunt.engine.core.math.manifold import Manifold
from vect_hunt.engine.core.math.numeric import Numeric
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform


class Collision:
    """
    Classe utilitaire pour les collisions.
    """

    @staticmethod
    def aabb_overlap(
        a_min: Vector2D, a_max: Vector2D, b_min: Vector2D, b_max: Vector2D
    ) -> bool:
        """
        Vérifie si deux AABB se superposent.

        Parameters
        ----------
        a_min : Vector2D
            Borne min AABB 1.
        a_max : Vector2D
            Borne max AABB 1.
        b_min : Vector2D
            Borne min AABB 2.
        b_max : Vector2D
            Borne max AABB 2.

        Returns
        -------
        bool
            True si les AABB se superposent, False sinon.
        """
        return Numeric.intervals_overlap(
            a_min.x, a_max.x, b_min.x, b_max.x
        ) and Numeric.intervals_overlap(a_min.y, a_max.y, b_min.y, b_max.y)

    @staticmethod
    def circle_circle_collision_info(
        pos1: Vector2D,
        radius1: float,
        pos2: Vector2D,
        radius2: float,
    ) -> "CollisionInfo | None":
        """
        Détecte une collision entre deux cercles.

        Les points de contact ne sont pas calculés ici.

        Parameters
        ----------
        pos1 : Vector2D
            Centre du premier cercle.
        radius1 : float
            Rayon du premier cercle.
        pos2 : Vector2D
            Centre du second cercle.
        radius2 : float
            Rayon du second cercle.

        Returns
        -------
        CollisionInfo | None
            Informations de collision ou None.
        """
        delta = pos2 - pos1
        radius_sum = radius1 + radius2
        radius_sum2 = radius_sum * radius_sum

        dist2 = delta.magnitude_squared()
        if dist2 >= radius_sum2:
            return None

        # Cas collision : on calcule la distance réelle une seule fois
        if dist2 <= Tolerence.GENERAL:
            # Centres (quasi) confondus : normale arbitraire mais stable
            normal = Vector2D(1.0, 0.0)
            dist = 0.0
        else:
            dist = dist2**0.5
            inv_dist = 1.0 / dist
            normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)

        penetration = radius_sum - dist
        if penetration < Tolerence.COLLISION:
            return None

        return CollisionInfo(normal=normal, depth=penetration)

    @staticmethod
    def _project_4_points_on_axis(
        corners: List[Vector2D],
        axis: Vector2D,
    ) -> tuple[float, float]:
        """
        Projette 4 points sur un axe (optimisé rectangle).

        Parameters
        ----------
        corners : List[Vector2D]
            4 coins du rectangle.
        axis : Vector2D
            Axe normalisé.

        Returns
        -------
        tuple[float, float]
            Intervalle [min, max] de projection.
        """

        values = [v.dot(axis) for v in corners]
        return min(values), max(values)

    @staticmethod
    def circle_box_collision_info(
        circle_pos: Vector2D,
        circle_radius: float,
        box_scene_tr: Transform,
        box_shape: BoxShape,
    ) -> "CollisionInfo | None":
        """
        Détecte une collision entre un cercle et un rectangle orienté.

        Les points de contact ne sont pas calculés ici.

        Parameters
        ----------
        circle_pos : Vector2D
            Centre du cercle.
        circle_radius : float
            Rayon du cercle.
        box_scene_tr : Transform
            Transform du box.
        box_shape: BoxShape
            Forme du box.

        Returns
        -------
        CollisionInfo | None
            Informations de collision (normal, depth) ou None.
        """

        local_point = box_scene_tr.to_local_point(circle_pos)
        closest_local = box_shape.closest_point_local(local_point)
        closest_scene = box_scene_tr.to_scene_point(closest_local)

        delta = circle_pos - closest_scene
        dist2 = delta.magnitude_squared()

        radius2 = circle_radius * circle_radius
        if dist2 >= radius2:
            return None

        dist = dist2**0.5
        penetration = circle_radius - dist
        if penetration < Tolerence.COLLISION:
            return None

        if dist2 <= Tolerence.GENERAL:
            # Centre du cercle dans le box : sortir par la face la plus proche.
            half_w = box_shape.width * 0.5
            half_h = box_shape.height * 0.5
            dx = half_w - abs(local_point.x)
            dy = half_h - abs(local_point.y)

            if dx <= dy:
                sign_x = 1.0 if local_point.x >= 0.0 else -1.0
                normal_local = Vector2D(sign_x, 0.0)
                penetration = circle_radius + dx
            else:
                sign_y = 1.0 if local_point.y >= 0.0 else -1.0
                normal_local = Vector2D(0.0, sign_y)
                penetration = circle_radius + dy

            normal = box_scene_tr.rotation.apply(normal_local)
        else:
            inv_dist = 1.0 / dist
            normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)

        return CollisionInfo(normal=normal, depth=penetration)

    @staticmethod
    def generate_contact_points(
        col_a: "ColliderComponent",
        col_b: "ColliderComponent",
        info: CollisionInfo,
    ) -> List[Vector2D]:
        """
        Génère les points de contact pour une paire de colliders.

        Cette fonction est destinée à être appelée APRÈS que la détection
        de collision ait déjà produit un CollisionInfo valide (normal + profondeur).

        Parameters
        ----------
        col_a : ColliderComponent
            Le premier collider.
        col_b : ColliderComponent
            Le second collider.
        info : CollisionInfo
            Les informations de collision entre les deux colliders.

        Returns
        -------
        List[Vector2D]
            Une liste de 0 à 2 points de contact en coordonnées monde.
        """
        # Pas de points si pas de collision exploitable
        if info.depth <= Tolerence.COLLISION:
            raise ValueError("generate_contact_points appelé sans collision valide.")

        # Normal sécurisée
        if info.normal.magnitude_squared() <= Tolerence.COLLISION * Tolerence.COLLISION:
            raise ValueError("La normale de collision doit être non nulle.")

        # --- Box / Box -> Manifold clipping ---
        if isinstance(col_a, BoxColliderComponent) and isinstance(
            col_b, BoxColliderComponent
        ):
            corners_a = col_a.get_scene_corners()
            corners_b = col_b.get_scene_corners()

            if info.reference_from_a is None:
                raise ValueError(
                    "reference_from_a doit être défini pour les collisions box/box."
                )

            return Manifold.build_contact_manifold(
                corners_a=corners_a,
                corners_b=corners_b,
                collision_normal=info.normal,
                reference_from_a=info.reference_from_a,
            )

        # --- Circle / Circle ---
        if isinstance(col_a, CircleColliderComponent) and isinstance(
            col_b, CircleColliderComponent
        ):
            # Contact point unique : sur la ligne des centres, côté A.
            pos_a = col_a.get_scene_transform().position
            pos_b = col_b.get_scene_transform().position

            # Si centres confondus, on prend un point arbitraire stable
            delta = pos_b - pos_a
            if delta.magnitude_squared() <= Tolerence.GENERAL * Tolerence.GENERAL:
                return [pos_a]

            # Point sur le cercle A dans la direction de B
            return [pos_a + info.normal * col_a.shape.radius]

        # --- Circle / Box (dans les deux sens) ---
        if isinstance(col_a, CircleColliderComponent) and isinstance(
            col_b, BoxColliderComponent
        ):
            return Collision._contact_circle_box(
                circle=col_a, box=col_b, normal_ab=info.normal
            )

        if isinstance(col_a, BoxColliderComponent) and isinstance(
            col_b, CircleColliderComponent
        ):
            # normal est A->B, donc ici A=box, B=circle,  mais la routine
            # attend circle puis box, donc on inverse le sens de la normale.
            return Collision._contact_circle_box(
                circle=col_b, box=col_a, normal_ab=-info.normal
            )

        # Pas géré : pas de points
        return []

    @staticmethod
    def _contact_circle_box(
        circle: CircleColliderComponent,
        box: BoxColliderComponent,
        normal_ab: Vector2D,
    ) -> List[Vector2D]:
        """
        Génère les points de contact pour une collision cercle/box.

        Parameters
        ----------
        circle : CircleColliderComponent
            Le collider cercle.
        box : BoxColliderComponent
            Le collider box.
        normal_ab : Vector2D
            Normale de collision.

        Returns
        -------
        List[Vector2D]
            Liste de points de contact en coordonnées monde.
        """
        # Point le plus proche sur la box, en monde
        box_tr = box.get_scene_transform()
        circle_pos = circle.get_scene_transform().position

        local_point = box_tr.to_local_point(circle_pos)
        closest_local = box.shape.closest_point_local(local_point)
        closest_world = box_tr.to_scene_point(closest_local)

        # Contact point côté cercle : centre + normal * radius (normal circle->box)
        contact = circle_pos + normal_ab.normalized() * circle.shape.radius

        # Si le cercle est profondément dedans, closest_world peut être plus stable
        if (closest_world - contact).magnitude_squared() <= (
            Tolerence.COLLISION * Tolerence.COLLISION
        ):
            return [closest_world]

        return [contact]

    @staticmethod
    def sat_box_box_collision_info(
        corners_a: List[Vector2D],
        corners_b: List[Vector2D],
    ) -> Optional[CollisionInfo]:
        """
        Detect OBB vs OBB collision using SAT and return a stable CollisionInfo.

        This implementation is designed to be compatible with a clipping manifold:
        - axes are unit (overlaps comparable)
        - normal is oriented from A to B
        - depth is in pixels (world units)
        - reference_from_a indicates which polygon produced the minimum axis

        Parameters
        ----------
        corners_a : List[Vector2D]
            4 corners of box A (CW or CCW, but must be cyclic order).
        corners_b : List[Vector2D]
            4 corners of box B.

        Returns
        -------
        Optional[CollisionInfo]
            CollisionInfo(normal, depth, reference_from_a) if colliding, else None.
        """
        if len(corners_a) != 4 or len(corners_b) != 4:
            raise ValueError("sat_box_box_collision_info expects 4 corners per box.")

        # Centres (used only to orient the normal A -> B)
        center_a = Collision._centroid_4(corners_a)
        center_b = Collision._centroid_4(corners_b)
        ab = center_b - center_a

        # SAT candidate axes: 2 unique normals per rectangle (unit)
        axes: List[Tuple[Vector2D, bool]] = []
        axes.extend(Collision._box_unique_axes_unit(corners_a, from_a=True))
        axes.extend(Collision._box_unique_axes_unit(corners_b, from_a=False))

        best: Optional[CollisionInfo] = None

        for axis_unit, from_a in axes:
            min_a, max_a = Collision._project_4(corners_a, axis_unit)
            min_b, max_b = Collision._project_4(corners_b, axis_unit)

            overlap = Collision._interval_overlap(min_a, max_a, min_b, max_b)
            if overlap is None:
                return None

            # Filter tiny overlaps (prevents "sticky" contacts due to float noise)
            if overlap < Tolerence.COLLISION:
                return None

            if best is None:
                best = CollisionInfo(normal=axis_unit, depth=overlap, reference_from_a=from_a)
                continue

            # Choose minimal penetration; tie-break for stability
            if Collision._is_better_axis(overlap, axis_unit, best.depth, best.normal):
                best = CollisionInfo(normal=axis_unit, depth=overlap, reference_from_a=from_a)

        if best is None:
            return None

        # Orient normal from A to B (required by your manifold contract)
        normal = best.normal
        if normal.dot(ab) < 0.0:
            normal = -normal

        return CollisionInfo(
            normal=normal,
            depth=best.depth,
            reference_from_a=best.reference_from_a,
        )

    @staticmethod
    def _box_unique_axes_unit(corners: List[Vector2D], from_a: bool) -> List[Tuple[Vector2D, bool]]:
        """
        Extract the 2 unique unit axes for an OBB (normals of two adjacent edges).

        Parameters
        ----------
        corners : List[Vector2D]
            4 corners in cyclic order.
        from_a : bool
            True if the axes belong to A, else belong to B.

        Returns
        -------
        List[Tuple[Vector2D, bool]]
            [(axis0_unit, from_a), (axis1_unit, from_a)]
        """
        eps2 = Tolerence.GENERAL * Tolerence.GENERAL

        e0 = corners[1] - corners[0]
        e1 = corners[2] - corners[1]

        # Edge normals (not unit)
        a0 = e0.normal()
        a1 = e1.normal()

        axis0 = Collision._safe_normalize(a0, eps2)
        axis1 = Collision._safe_normalize(a1, eps2)

        return [(axis0, from_a), (axis1, from_a)]

    @staticmethod
    def _safe_normalize(v: Vector2D, eps2: float) -> Vector2D:
        """
        Safely normalize a vector.

        Parameters
        ----------
        v : Vector2D
            Vector to normalize.
        eps2 : float
            Squared epsilon threshold.

        Returns
        -------
        Vector2D
            Unit vector, or (1,0) fallback if norm too small.
        """
        mag2 = v.magnitude_squared()
        if mag2 <= eps2:
            return Vector2D(1.0, 0.0)
        inv = 1.0 / (mag2 ** 0.5)
        return Vector2D(v.x * inv, v.y * inv)

    @staticmethod
    def _project_4(corners: List[Vector2D], axis_unit: Vector2D) -> Tuple[float, float]:
        """
        Project 4 corners on a unit axis.

        Parameters
        ----------
        corners : List[Vector2D]
            4 points.
        axis_unit : Vector2D
            Unit axis.

        Returns
        -------
        Tuple[float, float]
            (min_proj, max_proj)
        """
        p0 = corners[0].dot(axis_unit)
        p1 = corners[1].dot(axis_unit)
        p2 = corners[2].dot(axis_unit)
        p3 = corners[3].dot(axis_unit)
        return min(p0, p1, p2, p3), max(p0, p1, p2, p3)

    @staticmethod
    def _interval_overlap(a_min: float, a_max: float, b_min: float, b_max: float) -> Optional[float]:
        """
        Compute overlap of 1D intervals.

        Parameters
        ----------
        a_min : float
            Interval A min.
        a_max : float
            Interval A max.
        b_min : float
            Interval B min.
        b_max : float
            Interval B max.

        Returns
        -------
        Optional[float]
            Overlap >= 0 if overlapping, else None.
        """
        if a_max < b_min or b_max < a_min:
            return None
        return min(a_max, b_max) - max(a_min, b_min)

    @staticmethod
    def _is_better_axis(
        candidate_penetration: float,
        candidate_axis: Vector2D,
        best_penetration: float,
        best_axis: Vector2D,
    ) -> bool:
        """
        Decide whether candidate SAT axis is better than the current best.

        Strategy
        ----------
        - Prefer strictly smaller penetration.
        - If almost equal (within an epsilon), prefer the axis that is more stable
        across frames: i.e., the one more aligned with the current best axis.

        This reduces face flipping when the box is near a corner-case configuration.

        Parameters
        ----------
        candidate_penetration : float
            Penetration along candidate axis.
        candidate_axis : Vector2D
            Candidate unit axis.
        best_penetration : float
            Current best penetration.
        best_axis : Vector2D
            Current best unit axis.

        Returns
        -------
        bool
            True if candidate should replace best.
        """
        # Epsilon for "equal penetration" comparisons
        pen_eps = max(Tolerence.COLLISION, 1e-6)

        if candidate_penetration + pen_eps < best_penetration:
            return True

        # If near tie, keep the axis closer to the existing one (stability)
        if abs(candidate_penetration - best_penetration) <= pen_eps:
            # Candidate "wins" only if it is significantly more aligned
            # than the best axis (rare). Usually we keep the current best.
            alignment_gain = candidate_axis.dot(best_axis)
            return alignment_gain > 0.999  # very strict: almost identical

        return False

    @staticmethod
    def _centroid_4(corners: List[Vector2D]) -> Vector2D:
        """
        Compute centroid of a 4-corner polygon.

        Parameters
        ----------
        corners : List[Vector2D]
            4 corners.

        Returns
        -------
        Vector2D
            Polygon centroid (average of points).
        """
        return Vector2D(
            (corners[0].x + corners[1].x + corners[2].x + corners[3].x) * 0.25,
            (corners[0].y + corners[1].y + corners[2].y + corners[3].y) * 0.25,
        )
