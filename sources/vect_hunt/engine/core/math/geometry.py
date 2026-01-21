from typing import List, Tuple
from .vector import Vector2D
from vect_hunt.engine.core.transform import Rotation


class Geometry:
    """
    Fournit des fonctions géométriques utilitaires pour la détection de collisions
    et d'autres opérations géométriques.

    Attributes
    ----------
    None
    """

    @staticmethod
    def get_polygon_normals(corners: List[Vector2D]) -> List[Vector2D]:
        """
        Calcule les normales unitaires aux arêtes d'un polygone.

        Pour chaque arête du polygone, calcule le vecteur normal (perpendiculaire)
        et le normalise. Ces normales sont utilisées comme axes de projection
        dans l'algorithme SAT (Separating Axis Theorem).

        Parameters
        ----------
        corners : List[Vector2D]
            Liste des coins du polygone dans l'ordre (sens horaire ou anti-horaire).

        Returns
        -------
        List[Vector2D]
            Liste des vecteurs normaux unitaires aux arêtes du polygone.
        """
        normals = []
        num_corners = len(corners)

        for i in range(num_corners):
            # Récupère les deux coins formant l'arête
            p1 = corners[i]
            p2 = corners[(i + 1) % num_corners]  # Boucle au premier coin

            # Vecteur de l'arête
            edge = Vector2D(p2.x - p1.x, p2.y - p1.y)

            # Calcule la normale (perpendiculaire) à l'arête
            normal = edge.normal()

            # Normalise le vecteur normal
            normalized_normal = normal.normalized()
            normals.append(normalized_normal)

        return normals

    @staticmethod
    def project_polygon_on_axis(
        corners: List[Vector2D], axis: Vector2D
    ) -> Tuple[float, float]:
        """
        Projette les coins d'un polygone sur un axe et retourne l'intervalle [min, max].

        La projection d'un point sur un axe est calculée via le produit scalaire.
        Cette fonction est utilisée dans l'algorithme SAT pour détecter si deux
        polygones se chevauchent sur un axe donné.

        Parameters
        ----------
        corners : List[Vector2D]
            Liste des coins du polygone.
        axis : Vector2D
            L'axe de projection (doit être un vecteur unitaire).

        Returns
        -------
        Tuple[float, float]
            Un tuple (min_projection, max_projection) représentant l'intervalle
            de projection du polygone sur l'axe.
        """
        min_proj = float("inf")
        max_proj = float("-inf")

        for corner in corners:
            # Calcule la projection via le produit scalaire
            projection = corner.dot(axis)

            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)

        return (min_proj, max_proj)

    @staticmethod
    def intervals_overlap(min1: float, max1: float, min2: float, max2: float) -> bool:
        """
        Vérifie si deux intervalles [min1, max1] et [min2, max2] se chevauchent.

        Parameters
        ----------
        min1 : float
            Borne inférieure du premier intervalle.
        max1 : float
            Borne supérieure du premier intervalle.
        min2 : float
            Borne inférieure du deuxième intervalle.
        max2 : float
            Borne supérieure du deuxième intervalle.

        Returns
        -------
        bool
            True si les intervalles se chevauchent, False sinon.
        """
        return max1 >= min2 and max2 >= min1

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
        return Geometry.intervals_overlap(
            a_min.x, a_max.x, b_min.x, b_max.x
        ) and Geometry.intervals_overlap(a_min.y, a_max.y, b_min.y, b_max.y)

    @staticmethod
    def to_local(point: Vector2D, position: Vector2D, rotation: Rotation) -> Vector2D:
        """
        Convertit un point scene vers un repere local.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees monde.
        position : Vector2D
            Position du repere local.
        rotation : Rotation
            Rotation du repere local.

        Returns
        -------
        Vector2D
            Point en coordonnees locales.
        """
        return rotation.inverse().apply(point - position)

    @staticmethod
    def to_scene(point: Vector2D, position: Vector2D, rotation: Rotation) -> Vector2D:
        """
        Convertit un point local vers le repere scene.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees locales.
        position : Vector2D
            Position du repere local.
        rotation : Rotation
            Rotation du repere local.

        Returns
        -------
        Vector2D
            Point en coordonnees monde.
        """
        return position + rotation.apply(point)

    @staticmethod
    def get_scene_corners(
        local_corners: List[Vector2D], position: Vector2D, rotation: Rotation
    ) -> List[Vector2D]:
        """
        Transforme des coins locaux vers des coins monde.

        Parameters
        ----------
        local_corners : List[Vector2D]
            Coins en repere local.
        position : Vector2D
            Position monde.
        rotation : Rotation
            Rotation monde.

        Returns
        -------
        List[Vector2D]
            Coins en repere monde.
        """
        return [rotation.apply(corner) + position for corner in local_corners]

    @staticmethod
    def _local_bounds(corners: List[Vector2D]) -> Tuple[float, float, float, float]:
        """
        Calcule les bornes min et max en x et y d'un ensemble de coins locaux.

        Parameters
        ----------
        corners : List[Vector2D]
            Coins en repere local.

        Returns
        -------
        Tuple[float, float, float, float]
            (min_x, max_x, min_y, max_y)
        """
        xs = [p.x for p in corners]
        ys = [p.y for p in corners]
        return min(xs), max(xs), min(ys), max(ys)

    @staticmethod
    def closest_point_on_box(
        point: Vector2D,
        box_position: Vector2D,
        box_rotation: Rotation,
        local_corners: List[Vector2D],
    ) -> Vector2D:
        """
        Calcule le point le plus proche sur un rectangle oriente.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees monde.
        box_position : Vector2D
            Centre du box en monde.
        box_rotation : Rotation
            Rotation du box en monde.
        local_corners : List[Vector2D]
            Coins locaux du box.

        Returns
        -------
        Vector2D
            Point le plus proche en monde.
        """
        local_point = Geometry.to_local(point, box_position, box_rotation)
        min_x, max_x, min_y, max_y = Geometry._local_bounds(local_corners)

        clamped_x = max(min_x, min(max_x, local_point.x))
        clamped_y = max(min_y, min(max_y, local_point.y))

        return Geometry.to_scene(Vector2D(clamped_x, clamped_y), box_position, box_rotation)

    # TODO : Epsilon à gérer en global
    @staticmethod
    def circle_circle_collision_info(
        pos1: Vector2D,
        radius1: float,
        pos2: Vector2D,
        radius2: float,
        min_penetration_depth: float = 1e-9,
    ) -> dict | None:
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
        min_penetration_depth : float, optional
            Profondeur minimale pour valider la collision.

        Returns
        -------
        dict | None
            Informations de collision ou None.
        """
        delta = pos1 - pos2
        dist = delta.magnitude()
        radius_sum = radius1 + radius2

        if dist < radius_sum:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            penetration = radius_sum - dist

            if penetration < min_penetration_depth:
                return None

            return {
                "normal": normal,
                "depth": penetration,
                "point": pos2 + normal * radius2,
            }
        return None

    @staticmethod
    def get_polygon_center(corners: List[Vector2D]) -> Vector2D:
        """
        Calcule le centre (centroïde) d'un polygone.

        Parameters
        ----------
        corners : List[Vector2D]
            Coins du polygone.

        Returns
        -------
        Vector2D
            Centre du polygone.
        """
        sum_x = sum(corner.x for corner in corners)
        sum_y = sum(corner.y for corner in corners)
        num_corners = len(corners)
        return Vector2D(sum_x / num_corners, sum_y / num_corners
                        )
    # TODO : Epsilon à gérer en global
    @staticmethod
    def sat_collision_info(
        corners1: List[Vector2D],
        corners2: List[Vector2D],
        min_penetration_depth: float = 1e-9,
    ) -> dict | None:
        """
        Détecte une collision SAT entre deux polygones.

        Parameters
        ----------
        corners1 : List[Vector2D]
            Coins du polygone 1.
        corners2 : List[Vector2D]
            Coins du polygone 2.
        min_penetration_depth : float, optional
            Profondeur minimale pour valider la collision.

        Returns
        -------
        dict | None
            Informations de collision (normal, depth) ou None.
        """
        axes = Geometry.get_polygon_normals(corners1) + Geometry.get_polygon_normals(
            corners2
        )
        penetration = float("inf")
        smallest_axis = None

        for axis in axes:
            min1, max1 = Geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = Geometry.project_polygon_on_axis(corners2, axis)
            if not Geometry.intervals_overlap(min1, max1, min2, max2):
                return None

            overlap = min(max1, max2) - max(min1, min2)
            if overlap < penetration:
                penetration = overlap
                smallest_axis = axis

        if penetration < min_penetration_depth or smallest_axis is None:
            return None

        normal = smallest_axis.normalized()
        center1 = Geometry.get_polygon_center(corners1)
        center2 = Geometry.get_polygon_center(corners2)
        direction = center1 - center2
        if direction.dot(normal) < 0:
            normal = -1 * normal

        return {"normal": normal, "depth": penetration}


    # TODO : Epsilon à gérer en global
    @staticmethod
    def circle_box_collision_info(
        circle_pos: Vector2D,
        circle_radius: float,
        box_position: Vector2D,
        box_rotation: Rotation,
        local_corners: List[Vector2D],
        min_penetration_depth: float = 1e-9,
        reverse_normal: bool = False,
    ) -> dict | None:
        """
        Détecte une collision entre un cercle et un rectangle orienté.

        Parameters
        ----------
        circle_pos : Vector2D
            Centre du cercle.
        circle_radius : float
            Rayon du cercle.
        box_position : Vector2D
            Centre du box.
        box_rotation : Rotation
            Rotation du box.
        local_corners : List[Vector2D]
            Coins locaux du box.
        min_penetration_depth : float, optional
            Profondeur minimale pour valider la collision.
        reverse_normal : bool, optional
            Inverse la normale si True.

        Returns
        -------
        dict | None
            Informations de collision (normal, depth, point) ou None.
        """
        closest = Geometry.closest_point_on_box(
            circle_pos, box_position, box_rotation, local_corners
        )
        delta = circle_pos - closest
        dist = delta.magnitude()

        if dist < circle_radius:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            if reverse_normal:
                normal = -1 * normal
            penetration = circle_radius - dist
            if penetration < min_penetration_depth:
                return None
            return {"normal": normal, "depth": penetration, "point": closest}
        return None
