from typing import TYPE_CHECKING, Optional

from .vector import Vector2D
from .transform import Transform

if TYPE_CHECKING:
    from vect_hunt.objects import GameObject

import math


class Collider:
    """
    Classe de base pour les colliders.
    Utilisée dans les systèmes de collision pour définir des zones de collision.
    """

    def __init__(
        self,
        parent: "GameObject",
        transform: Optional[Transform] = None,
        solid: bool = True,
    ):
        """
        Définit un collider de base avec un transform et une propriété de solidité.

        Parameters
        ----------
        parent : GameObject
            L'objet de jeu auquel le collider appartient.
        transform : Transform
            Le transform associé au collider.
        solid : bool
            Indique si le collider interagit avec d'autres colliders ou non.
        """
        self.parent = parent
        self.transform = transform if transform is not None else Transform()
        self.solid = solid

    def get_geometry(self) -> dict:
        """
        Retourne la géométrie spécifique du collider.
        Doit être implémentée dans les sous-classes.

        Returns
        -------
        dict
            La géométrie spécifique du collider.
        """
        raise NotImplementedError(
            "Cette méthode doit être implémentée dans les sous-classes."
        )


class BoxCollider(Collider):
    """
    Classe de collider rectangulaire.
    Utilisée dans les systèmes de collision pour définir des zones rectangulaires.
    """

    def __init__(
        self,
        parent: "GameObject",
        width: float = 10.0,
        height: float = 10.0,
        center: Optional[Vector2D] = None,
        orientation: float = 0.0,
        solid: bool = True,
    ):
        """
        Initialise un BoxCollider avec une largeur, une hauteur et une orientation.

        Parameters
        ----------
        parent : GameObject
            L'objet de jeu auquel le collider appartient.
        width : float
            La largeur du BoxCollider.
        height : float
            La hauteur du BoxCollider.
        center : Vector2D
            Le centre du BoxCollider.
        orientation : float
            L'orientation du BoxCollider en radians. Par défaut à 0.
        solid : bool
            Indique si le collider interagit avec d'autres colliders ou non.
        """
        self.width = width
        self.height = height

        if center is None:
            center = Vector2D(0, 0)
        transform = Transform(position=center, rotation=orientation)

        # Initialiser les attributs nécessaires AVANT d'appeler super()
        self.transform = transform
        self.cos_orientation = math.cos(orientation)
        self.sin_orientation = math.sin(orientation)
        self.corners: list[Vector2D] = self.calculate_corners()

        # Maintenant on peut appeler super() qui va calculer l'AABB
        super().__init__(parent, transform, solid)

    def get_area(self):
        """
        Calcule l'aire du BoxCollider.

        Returns
        -------
        float
            L'aire du rectangle.
        """
        return self.width * self.height

    def calculate_corners(self) -> list[Vector2D]:
        """
        Calcule les coordonnées des coins du BoxCollider.

        Returns
        -------
        List[Vector2D]
            Une liste des coins du BoxCollider dans l'ordre suivant :
            [top-left, top-right, bottom-right, bottom-left]
        """
        half_width = self.width / 2
        half_height = self.height / 2

        # Calcul des coins avant rotation
        # Note: Les coins vont exactement à +/- half_width et +/- half_height
        # pour que le box corresponde visuellement au cercle inscrit
        corners = [
            Vector2D(-half_width, -half_height),  # top-left (pygame Y inversé)
            Vector2D(half_width, -half_height),  # top-right
            Vector2D(half_width, half_height),  # bottom-right
            Vector2D(-half_width, half_height),  # bottom-left
        ]

        # Rotation des coins autour du centre
        rotated_corners = []
        cos_angle = self.cos_orientation
        sin_angle = self.sin_orientation

        for corner in corners:
            rotated_x = corner.x * cos_angle - corner.y * sin_angle
            rotated_y = corner.x * sin_angle + corner.y * cos_angle
            rotated_corners.append(
                Vector2D(
                    rotated_x + self.transform.position.x,
                    rotated_y + self.transform.position.y,
                )
            )

        return rotated_corners

    def get_geometry(self) -> dict:
        """
        Retourne la géométrie spécifique du BoxCollider.

        Returns
        -------
        dict
            La géométrie spécifique du BoxCollider.
        """

        return {
            "type": "box",
            "points": self.corners,
        }


class CircleCollider(Collider):
    """
    Classe de collider circulaire.
    Utilisée dans les systèmes de collision pour définir des zones circulaires.
    """

    def __init__(
        self,
        parent: "GameObject",
        center: Optional[Vector2D] = None,
        radius: float = 5.0,
        solid: bool = True,
    ):
        """
        Initialise un CircleCollider avec un rayon.

        Parameters
        ----------
        parent : GameObject
            L'objet de jeu auquel le collider appartient.
        center : Vector2D
            Le centre du CircleCollider.
        radius : float
            Le rayon du CircleCollider.
        """

        if center is None:
            center = Vector2D(0, 0)
        transform = Transform(center)
        self.radius = radius

        super().__init__(parent, transform, solid)

    def get_area(self):
        """
        Calcule l'aire du CircleCollider.

        Returns
        -------
        float
            L'aire du cercle.
        """
        return math.pi * (self.radius**2)

    def get_geometry(self) -> dict:
        """
        Retourne la géométrie spécifique du CircleCollider.

        Returns
        -------
        dict
            La géométrie spécifique du CircleCollider.
        """
        return {
            "type": "circle",
            "center": self.transform.position,
            "radius": self.radius,
        }
