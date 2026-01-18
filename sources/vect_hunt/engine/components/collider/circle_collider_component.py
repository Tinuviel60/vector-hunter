import math
from typing import Any, Optional, TYPE_CHECKING

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform

from .collider_component import ColliderComponent

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject


class CircleColliderComponent(ColliderComponent):
    """
    Classe de collider circulaire.
    Utilisee dans les systemes de collision pour definir des zones circulaires.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    radius : float
        Rayon du cercle.
    center : Vector2D
        Centre du cercle par rapport au GameObject parent.
    solid : bool
        Indique si le collider est solide.
    """

    component_name = "circle_collider"

    def __init__(
        self,
        game_object: Optional["GameObject"] = None,
        center: Optional[Vector2D] = None,
        radius: float = 5.0,
        solid: bool = True,
    ):
        if center is None:
            center = Vector2D(0, 0)
        transform = Transform(center)
        self.radius = radius

        super().__init__(game_object, transform, solid)

    @classmethod
    def from_data(
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "CircleColliderComponent":
        """
        Crée un CircleColliderComponent à partir de données sérialisées.

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
        center = Vector2D(position_data[0], position_data[1])
        return cls(
            game_object=game_object,
            center=center,
            radius=data.get("radius", 5.0),
            solid=data.get("solid", True),
        )

    def get_area(self):
        """
        Calcule et retourne l'aire du cercle.

        Returns
        -------
        float
            Aire du cercle.
        """
        return math.pi * (self.radius**2)

    def get_geometry(self) -> dict:
        """
        Retourne la géométrie du collider sous forme de dictionnaire.

        Returns
        -------
        dict
            Dictionnaire représentant la géométrie du cercle.
        """
        return {
            "type": "circle",
            "center": self.transform.position,
            "radius": self.radius,
        }
