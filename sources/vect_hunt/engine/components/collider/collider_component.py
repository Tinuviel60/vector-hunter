from abc import ABC
from typing import Optional

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.transform.transform import Transform

from vect_hunt.engine.core.geometries import Shape


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
        transform: Optional[Transform] = None,
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
        self.transform = transform if transform is not None else Transform()
        self.solid = solid
        self.nb_collision = 0

    def update(self, delta_time: float) -> None:
        """
        Met a jour le collider si necessaire.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass
