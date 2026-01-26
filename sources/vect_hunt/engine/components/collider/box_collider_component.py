import math
from typing import Any, Optional

from vect_hunt.engine.core.geometries.box_shape import BoxShape
from vect_hunt.engine.core.math.geometry import Geometry
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform

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
        self._cached_scene_corners: list[Vector2D] = []

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

    def get_scene_aabb(self) -> tuple[Vector2D, Vector2D]:
        """
        Calcule l'AABB mondiale du collider en combinant
        le Transform du GameObject parent et le Transform local.

        Returns
        -------
        tuple[Vector2D, Vector2D]
            Coin inférieur gauche et coin supérieur droit de l'AABB mondiale.
        """

        self._compute_cached_values()

        return self._cached_world_aabb

    def get_scene_corners(self) -> list[Vector2D]:
        """
        Obtient les coins du rectangle dans le système de coordonnées de la scène.

        Returns
        -------
        list[Vector2D]
            Liste des coins du rectangle dans le système de coordonnées de la scène.
        """
        self._compute_cached_values()

        return self._cached_scene_corners

    def _compute_cached_values(self) -> None:
        """
        Met à jour les valeurs mises en cache si le Transform parent a changé.
        """
        if self._transform_version == self.parent.transform._version:
            return

        self._cached_scene_corners = self._compute_scene_corners()
        self._cached_world_aabb = self._compute_scene_aabb()

        self._transform_version = self.parent.transform._version

    def _compute_scene_corners(self) -> list[Vector2D]:
        """
        Calcule les coins du rectangle dans le système de coordonnées de la scène.

        Returns
        -------
        list[Vector2D]
            Liste des coins du rectangle dans le système de coordonnées de la scène.
        """
        scene_tr = self.parent.transform.combine(self.transform)
        corners = Geometry.get_scene_corners(self.shape.local_vertices(), scene_tr)
        return corners

    def _compute_scene_aabb(self) -> tuple[Vector2D, Vector2D]:
        """
        Calcule l'AABB mondiale du collider en combinant
        le Transform du GameObject parent et le Transform local.
        """
        scene_corners = self._cached_scene_corners

        min_x = min(corner.x for corner in scene_corners)
        max_x = max(corner.x for corner in scene_corners)
        min_y = min(corner.y for corner in scene_corners)
        max_y = max(corner.y for corner in scene_corners)

        return (Vector2D(min_x, min_y), Vector2D(max_x, max_y))
