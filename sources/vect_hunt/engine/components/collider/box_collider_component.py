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

        # Cache pour le coins en coordonnées scène
        self._corner_version = -1
        self._cached_scene_corners: list[Vector2D] = []

        # Axe en cache
        self._cached_axis_u: Vector2D = Vector2D(1.0, 0.0)  # axe local X en scène
        self._cached_axis_v: Vector2D = Vector2D(0.0, 1.0)  # axe local Y en scène

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
        Obtient l'AABB du rectangle dans le système de coordonnées de la scène.
        Ne calcule pas les coins.

        Returns
        -------
        tuple[Vector2D, Vector2D]
            Coin inférieur gauche et coin supérieur droit de l'AABB mondiale.
        """
        parent_version = self.parent.transform._version
        if self._aabb_version == parent_version:
            return self._cached_world_aabb

        # Transform scène complet (parent + local collider)
        scene_transform = self.parent.transform.combine(self.transform)

        # Centre scène
        scene_center = scene_transform.position

        # Axes unitaires scène : rotation appliquée aux axes locaux
        axis_u = scene_transform.rotation.apply(Vector2D.right())
        axis_v = scene_transform.rotation.apply(Vector2D.top())
        # Note: adapte Vector2D.top() si ton "up" est (0, -1) vs (0, +1).

        # Demi-extents (en local)
        half_w = self.shape.width * 0.5
        half_h = self.shape.height * 0.5

        # Projection des demi-extents sur X/Y monde via valeurs absolues
        ex = abs(axis_u.x) * half_w + abs(axis_v.x) * half_h
        ey = abs(axis_u.y) * half_w + abs(axis_v.y) * half_h

        min_point = Vector2D(scene_center.x - ex, scene_center.y - ey)
        max_point = Vector2D(scene_center.x + ex, scene_center.y + ey)

        self._cached_axis_u = axis_u
        self._cached_axis_v = axis_v
        self._cached_world_aabb = (min_point, max_point)
        self._aabb_version = parent_version

        return self._cached_world_aabb

    def get_scene_corners(self) -> list[Vector2D]:
        """
        Obtient les coins du rectangle dans le système de coordonnées de la scène.

        Returns
        -------
        list[Vector2D]
            Liste des coins du rectangle dans le système de coordonnées de la scène.
        """
        if self._corner_version == self.parent.transform._version:
            return self._cached_scene_corners

        scene_tr = self.parent.transform.combine(self.transform)
        self._cached_scene_corners = Geometry.get_scene_corners(
            self.shape.local_vertices(), scene_tr
        )

        self._corner_version = self.parent.transform._version

        return self._cached_scene_corners
