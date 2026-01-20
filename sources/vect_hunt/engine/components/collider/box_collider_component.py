import math
from typing import Any, Optional

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform
from vect_hunt.engine.core.geometries import BoxShape


from .collider_component import ColliderComponent


class BoxColliderComponent(ColliderComponent):
    """
    Classe de collider rectangulaire.
    Utilisee dans les systemes de collision pour definir des zones rectangulaires.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    shape : BoxShape
        Forme box portée par le collider.
    center : Vector2D
        Centre du rectangle par rapport au GameObject parent.
    orientation : float
        Orientation du rectangle en radians.
    solid : bool
        Indique si le collider est solide.
    """

    component_name = "box_collider"
    shape: BoxShape

    def __init__(
        self,
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
        if center is None:
            center = Vector2D(0, 0)

        transform = Transform(position=center, rotation=orientation)
        shape = BoxShape(width=width, height=height)
        super().__init__(shape=shape, transform=transform, solid=solid)

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "BoxColliderComponent":
        """
        Crée un BoxColliderComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
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
            width=data.get("width", 10.0),
            height=data.get("height", 10.0),
            center=center,
            orientation=rotation,
            solid=data.get("solid", True),
        )
