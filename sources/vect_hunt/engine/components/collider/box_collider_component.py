import math
from typing import Any, Optional, TYPE_CHECKING

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform

from .collider_component import ColliderComponent

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject


class BoxColliderComponent(ColliderComponent):
    """
    Classe de collider rectangulaire.
    Utilisee dans les systemes de collision pour definir des zones rectangulaires.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    width : float
        Largeur du rectangle.
    height : float
        Hauteur du rectangle.
    center : Vector2D
        Centre du rectangle par rapport au GameObject parent.
    orientation : float
        Orientation du rectangle en radians.
    solid : bool
        Indique si le collider est solide.
    """

    component_name = "box_collider"

    def __init__(
        self,
        game_object: Optional["GameObject"] = None,
        width: float = 10.0,
        height: float = 10.0,
        center: Optional[Vector2D] = None,
        orientation: float = 0.0,
        solid: bool = True,
    ):
        """
        Initialise le BoxColliderComponent avec les dimensions,
        le centre et l'orientation.

        Parameters
        ----------
        parent : GameObject, optional
            Le GameObject auquel ce composant appartient.
        width : float
            Largeur du rectangle.
        height : float
            Hauteur du rectangle.
        center : Vector2D, optional
            Centre du rectangle par rapport au GameObject parent.
        orientation : float
            Orientation du rectangle en radians.
        solid : bool
            Indique si le collider est solide.
        """
        self.width = width
        self.height = height

        if center is None:
            center = Vector2D(0, 0)
        transform = Transform(position=center, rotation=orientation)

        self.transform = transform
        self.cos_orientation = math.cos(orientation)
        self.sin_orientation = math.sin(orientation)
        self.corners: list[Vector2D] = self.calculate_corners()

        super().__init__(game_object, transform, solid)

    @classmethod
    def from_data(
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "BoxColliderComponent":
        """
        Crée un BoxColliderComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        game_object : GameObject
            Le GameObject auquel ce composant sera attaché.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        InputComponent
            Instance du composant créé.
        """
        transform_data = data.get("transform", {})
        position_data = transform_data.get("position", [0, 0])
        rotation = math.radians(transform_data.get("rotation", 0.0))
        center = Vector2D(position_data[0], position_data[1])
        return cls(
            game_object=game_object,
            width=data.get("width", 10.0),
            height=data.get("height", 10.0),
            center=center,
            orientation=rotation,
            solid=data.get("solid", True),
        )

    def get_area(self):
        """
        Calcule et retourne l'aire du rectangle.

        Returns
        -------
        float
            Aire du rectangle.
        """
        return self.width * self.height

    def calculate_corners(self) -> list[Vector2D]:
        """
        Calcule les coins du rectangle en fonction de la position,
        de la taille et de l'orientation.

        Returns
        -------
        list[Vector2D]
            Liste des coins du rectangle dans l'ordre horaire.
        """
        half_width = self.width / 2
        half_height = self.height / 2

        corners = [
            Vector2D(-half_width, -half_height),
            Vector2D(half_width, -half_height),
            Vector2D(half_width, half_height),
            Vector2D(-half_width, half_height),
        ]

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
        Retourne la geometrie specifique du collider.

        Returns
        -------
        dict
            Dictionnaire représentant la géométrie du rectangle.
        """
        return {
            "type": "box",
            "points": self.corners,
        }
