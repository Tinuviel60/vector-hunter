import math
from typing import Any, Optional, TYPE_CHECKING

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform

from .base import Collider

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject


class CircleCollider(Collider):
    """
    Classe de collider circulaire.
    Utilisee dans les systemes de collision pour definir des zones circulaires.
    """

    def __init__(
        self,
        parent: Optional["GameObject"] = None,
        center: Optional[Vector2D] = None,
        radius: float = 5.0,
        solid: bool = True,
    ):
        if center is None:
            center = Vector2D(0, 0)
        transform = Transform(center)
        self.radius = radius

        super().__init__(parent, transform, solid)

    @classmethod
    def from_data(
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "CircleCollider":
        transform_data = data.get("transform", {})
        position_data = transform_data.get("position", [0, 0])
        center = Vector2D(position_data[0], position_data[1])
        return cls(
            parent=game_object,
            center=center,
            radius=data.get("radius", 5.0),
            solid=data.get("solid", True),
        )

    def get_area(self):
        return math.pi * (self.radius**2)

    def get_geometry(self) -> dict:
        return {
            "type": "circle",
            "center": self.transform.position,
            "radius": self.radius,
        }
