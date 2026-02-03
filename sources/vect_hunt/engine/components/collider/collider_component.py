from abc import ABC

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.geometries.shape import Shape
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform


class ColliderComponent(Component, ABC):
    """
    Classe de base pour les colliders.
    Utilisee dans les systemes de collision pour definir des zones de collision.

    Le collider porte :
    - un Transform local (offset / rotation locale)
    - une Shape (géométrie locale pure)
    - un flag solid/trigger

    La géométrie (coins, aire, aabb, etc.) est déléguée à la Shape.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    shape : Shape
        Forme géométrique locale associée au collider.
    transform : Transform
        Transform local du collider.
    solid : bool
        True = collision solide, False = trigger.
    """

    component_name = "collider"

    def __init__(
        self,
        shape: Shape,
        transform: Transform,
        solid: bool = True,
    ):
        """
        Definit un collider de base avec un transform et une propriete de solidite.

        Parameters
        ----------
        shape : Shape
            La forme géométrique locale associée au collider.
        transform : Transform
            Le transform associe au collider (offset et orientation locale).
        solid : bool
            Indique si le collider déclenche des collisions ou des triggers.
        """
        super().__init__()
        self.shape = shape
        self.transform = transform
        self.solid = solid
        self.nb_collision = 0
        self._aabb_version = -1
        self._cached_world_aabb: tuple[Vector2D, Vector2D] = (
            Vector2D(0, 0),
            Vector2D(0, 0),
        )

    def update(self, delta_time: float) -> None:
        """
        Met a jour le collider si necessaire.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass

    def get_scene_aabb(self) -> tuple[Vector2D, Vector2D]:
        """
        Calcule l'AABB mondiale du collider en combinant
        le Transform du GameObject parent et le Transform local.

        Returns
        -------
        tuple[Vector2D, Vector2D]
            Les coins min et max de l'AABB mondiale.
        """

        raise NotImplementedError("get_scene_aabb must be implemented in subclasses.")

    def get_scene_transform(self) -> Transform:
        """
        Calcule la position mondiale du collider en combinant
        le Transform du GameObject parent et le Transform local.

        Returns
        -------
        Transform
            Le transform mondiale du collider.
        """
        scene_transform = self.parent.transform.combine(self.transform)
        return scene_transform
