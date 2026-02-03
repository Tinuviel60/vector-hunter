from typing import List, Tuple

from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform


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
            normal.normalize()
            normals.append(normal)

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
    def get_scene_corners(
        local_corners: List[Vector2D], scene_tr: Transform
    ) -> List[Vector2D]:
        """
        Transforme des coins locaux vers des coins monde.

        Parameters
        ----------
        local_corners : List[Vector2D]
            Coins en repere local.
        scene_tr : Transform
            Transform du repere monde.

        Returns
        -------
        List[Vector2D]
            Coins en repere monde.
        """
        return [
            scene_tr.rotation.apply(corner) + scene_tr.position
            for corner in local_corners
        ]

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
        return Vector2D(sum_x / num_corners, sum_y / num_corners)
