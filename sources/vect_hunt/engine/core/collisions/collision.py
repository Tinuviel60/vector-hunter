from typing import List

from vect_hunt.engine.core.collisions.collision_info import CollisionInfo
from vect_hunt.engine.core.geometries.box_shape import BoxShape
from vect_hunt.engine.core.math.geometry import Geometry
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
            normal = Vector2D(-1.0, 0.0)
            dist = 0.0
        else:
            dist = dist2**0.5
            inv_dist = 1.0 / dist
            normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)

        penetration = radius_sum - dist
        if penetration < Tolerence.COLLISION:
            return None

        # Point de contact côté cercle 2 (sur sa surface, vers l'extérieur)
        contact_point = pos2 + (-normal) * radius2

        return CollisionInfo(normal=normal, depth=penetration, points=[contact_point])

    @staticmethod
    def sat_collision_info(
        corners1: List[Vector2D],
        corners2: List[Vector2D],
    ) -> CollisionInfo | None:
        """
        Détecte une collision SAT entre deux polygones.

        Parameters
        ----------
        corners1 : List[Vector2D]
            Coins du polygone 1.
        corners2 : List[Vector2D]
            Coins du polygone 2.
        Returns
        -------
        dict | None
            Informations de collision (normal, depth) ou None.
        """
        axes: List[tuple[Vector2D, bool]] = []
        for axis in Geometry.get_polygon_normals(corners1):
            axes.append((axis, True))
        for axis in Geometry.get_polygon_normals(corners2):
            axes.append((axis, False))
        penetration = float("inf")
        smallest_axis = None
        axis_from_a = True

        for axis, from_a in axes:
            min1, max1 = Geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = Geometry.project_polygon_on_axis(corners2, axis)
            if not Numeric.intervals_overlap(min1, max1, min2, max2):
                return None

            overlap = min(max1, max2) - max(min1, min2)
            if overlap < penetration:
                penetration = overlap
                smallest_axis = axis
                axis_from_a = from_a

        eps = Tolerence.COLLISION
        if penetration < eps or smallest_axis is None:
            return None

        normal = smallest_axis.normalized()

        center1 = Geometry.get_polygon_center(corners1)
        center2 = Geometry.get_polygon_center(corners2)
        direction = center2 - center1
        if direction.dot(normal) < 0:
            normal = -normal

        points = Manifold.build_contact_manifold(
            corners_a=corners1,
            corners_b=corners2,
            collision_normal=normal,
            penetration_depth=penetration,
            reference_from_a=axis_from_a,
        )
        return CollisionInfo(normal=normal, depth=penetration, points=points)

    @staticmethod
    def circle_box_collision_info(
        circle_pos: Vector2D,
        circle_radius: float,
        box_scene_tr: Transform,
        box_shape: BoxShape,
    ) -> "CollisionInfo | None":
        """
        Détecte une collision entre un cercle et un rectangle orienté.

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
            Informations de collision (normal, depth, point) ou None.
        """

        local_point = box_scene_tr.to_local_point(circle_pos)
        closest_local = box_shape.closest_point_local(local_point)
        closest_scene = box_scene_tr.to_scene_point(closest_local)

        delta = circle_pos - closest_scene
        dist2 = delta.magnitude_squared()

        if dist2 < circle_radius * circle_radius:
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
                    contact_local = Vector2D(sign_x * half_w, local_point.y)
                    penetration = circle_radius + dx
                else:
                    sign_y = 1.0 if local_point.y >= 0.0 else -1.0
                    normal_local = Vector2D(0.0, sign_y)
                    contact_local = Vector2D(local_point.x, sign_y * half_h)
                    penetration = circle_radius + dy

                normal = box_scene_tr.rotation.apply(normal_local)
                contact_point = box_scene_tr.to_scene_point(contact_local)
            else:
                inv_dist = 1.0 / dist
                normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)
                contact_point = closest_scene

            return CollisionInfo(
                normal=normal, depth=penetration, points=[contact_point]
            )
        return None
