import math
from typing import List, Tuple
from vect_hunt.core import Position2D, Vector2D

"""
Module contenant les fonctions géométriques pour les calculs de collision.
"""


def get_polygon_normals(corners: List[Position2D]) -> List[Vector2D]:
    """
    Calcule les normales unitaires aux arêtes d'un polygone.

    Pour chaque arête du polygone, calcule le vecteur normal (perpendiculaire)
    et le normalise. Ces normales sont utilisées comme axes de projection
    dans l'algorithme SAT (Separating Axis Theorem).

    Parameters
    ----------
    corners : List[Position2D]
        Liste des coins du polygone dans l'ordre (sens horaire ou anti-horaire).

    Returns
    -------
    List[Vector2D]
        Liste des vecteurs normaux unitaires aux arêtes du polygone.

    Examples
    --------
    >>> corners = [Position2D(0, 0), Position2D(1, 0), Position2D(1, 1), Position2D(0, 1)]
    >>> normals = get_polygon_normals(corners)
    >>> len(normals)
    4
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

def project_polygon_on_axis(
    corners: List[Position2D], axis: Vector2D
) -> Tuple[float, float]:
    """
    Projette les coins d'un polygone sur un axe et retourne l'intervalle [min, max].

    La projection d'un point sur un axe est calculée via le produit scalaire.
    Cette fonction est utilisée dans l'algorithme SAT pour détecter si deux
    polygones se chevauchent sur un axe donné.

    Parameters
    ----------
    corners : List[Position2D]
        Liste des coins du polygone.
    axis : Vector2D
        L'axe de projection (doit être un vecteur unitaire).

    Returns
    -------
    Tuple[float, float]
        Un tuple (min_projection, max_projection) représentant l'intervalle
        de projection du polygone sur l'axe.

    Examples
    --------
    >>> corners = [Position2D(0, 0), Position2D(2, 0), Position2D(2, 1), Position2D(0, 1)]
    >>> axis = Vector2D(1, 0)  # Axe horizontal
    >>> project_polygon_on_axis(corners, axis)
    (0.0, 2.0)
    """
    min_proj = float("inf")
    max_proj = float("-inf")

    for corner in corners:
        # Convertit Position2D en Vector2D pour utiliser dot()
        corner_vector = Vector2D(corner.x, corner.y)

        # Calcule la projection via le produit scalaire
        projection = corner_vector.dot(axis)

        min_proj = min(min_proj, projection)
        max_proj = max(max_proj, projection)

    return (min_proj, max_proj)


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

    Examples
    --------
    >>> intervals_overlap(0, 2, 1, 3)
    True
    >>> intervals_overlap(0, 1, 2, 3)
    False
    """
    return max1 >= min2 and max2 >= min1


def distance_squared(p1: Position2D, p2: Position2D) -> float:
    """
    Calcule la distance au carré entre deux points.

    Utilise la distance au carré plutôt que la distance réelle pour éviter
    l'opération coûteuse de racine carrée. Idéal pour les comparaisons de distances.

    Parameters
    ----------
    p1 : Position2D
        Le premier point.
    p2 : Position2D
        Le deuxième point.

    Returns
    -------
    float
        La distance au carré entre les deux points.

    Examples
    --------
    >>> p1 = Position2D(0, 0)
    >>> p2 = Position2D(3, 4)
    >>> distance_squared(p1, p2)
    25.0
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return dx * dx + dy * dy
