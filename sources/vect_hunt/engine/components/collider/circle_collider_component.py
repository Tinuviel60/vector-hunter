from typing import Any, Optional

from vect_hunt.engine.core.geometries.circle_shape import CircleShape
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform

from .collider_component import ColliderComponent


class CircleColliderComponent(ColliderComponent):
    """
    Collider circulaire.
    Utilisée dans les systèmes de collision pour définir des zones circulaires.

    Wrapper pratique autour d'une CircleShape pour :
    - sérialisation JSON
    - component_name explicite
    - validations spécifiques

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    shape : CircleShape
        Forme cercle locale associée au collider.
    transform : Transform
        Transform local du collider.
    solid : bool
        True = collision solide, False = trigger.
    """

    component_name = "circle_collider"
    shape: CircleShape

    def __init__(
        self,
        center: Optional[Vector2D] = None,
        radius: float = 5.0,
        solid: bool = True,
    ):
        if center is None:
            center = Vector2D(0, 0)

        transform = Transform(center)
        shape = CircleShape(radius=radius)
        super().__init__(shape=shape, transform=transform, solid=solid)

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "CircleColliderComponent":
        """
        Crée un CircleColliderComponent à partir de données sérialisées.

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
        center = Vector2D(position_data[0], position_data[1])

        return cls(
            center=center,
            radius=data.get("radius", 5.0),
            solid=data.get("solid", True),
        )

    def get_scene_aabb(self) -> tuple[Vector2D, Vector2D]:
        if self._transform_version == self.parent.transform._version:
            return self._cached_world_aabb

        scene_center = self.get_scene_transform().position
        radius = self.shape.radius

        min_x = scene_center.x - radius
        min_y = scene_center.y - radius
        max_x = scene_center.x + radius
        max_y = scene_center.y + radius

        self._cached_world_aabb = (Vector2D(min_x, min_y), Vector2D(max_x, max_y))
        self._transform_version = self.parent.transform._version

        return self._cached_world_aabb
