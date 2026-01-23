from dataclasses import dataclass
from typing import List

from vect_hunt.engine.core.math.vector import Vector2D


@dataclass
class CollisionInfo:
    """
    Contient les informations détaillées d'une collision.

    Attributes
    ----------
    normal : Vector2D
        Normale de collision (unitaire, de B vers A).
    depth : float
        Profondeur de pénétration.
    points : List[Vector2D]
        Points de contact de la collision.

    """

    normal: Vector2D
    depth: float
    points: List[Vector2D]
