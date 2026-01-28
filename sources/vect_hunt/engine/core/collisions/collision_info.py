from dataclasses import dataclass
from typing import List, Optional

from vect_hunt.engine.core.math.vector import Vector2D


@dataclass
class CollisionInfo:
    """
    Contient les informations détaillées d'une collision.

    Attributes
    ----------
    normal : Vector2D
        Normale de collision (unitaire, de A vers B).
    depth : float
        Profondeur de pénétration.
    points : Optional[List[Vector2D]]
        Points de contact de la collision. N'est pas initialisé pour
        lors de la détection, sera calculé lors de la résolution si nécessaire.
    reference_from_a : Optional[bool]
        Indique si la référence de collision est prise depuis A, pour
        les manifolds (collisions box box).
    """

    normal: Vector2D
    depth: float
    points: Optional[List[Vector2D]] = None
    reference_from_a: Optional[bool] = None

    def copy(self) -> "CollisionInfo":
        """
        Crée une copie de l'objet CollisionInfo.

        Returns
        -------
        CollisionInfo
            Une nouvelle instance de CollisionInfo avec les mêmes valeurs.
        """
        return CollisionInfo(
            normal=Vector2D(self.normal.x, self.normal.y),
            depth=self.depth,
            points=[Vector2D(p.x, p.y) for p in self.points]
            if self.points is not None
            else None,
            reference_from_a=self.reference_from_a,
        )