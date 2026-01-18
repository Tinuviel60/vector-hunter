from abc import abstractmethod
from typing import Optional

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.transform import Transform


class ColliderComponent(Component):
    """
    Classe de base pour les colliders.
    Utilisee dans les systemes de collision pour definir des zones de collision.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject parent du collider.
    transform : Transform
        Transform local du collider.
    solid : bool
        Indique si le collider est solide.
    """

    component_name = "collider"

    def __init__(
        self,
        transform: Optional[Transform] = None,
        solid: bool = True,
    ):
        """
        Definit un collider de base avec un transform et une propriete de solidite.

        Parameters
        ----------
        transform : Transform
            Le transform associe au collider (offset et orientation locaux).
        solid : bool
            Indique si le collider interagit avec d'autres colliders ou non.
        """
        super().__init__()
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

    @abstractmethod
    def get_geometry(self) -> dict:
        """
        Retourne la geometrie specifique du collider.
        Doit etre implemente dans les sous-classes.
        """
        raise NotImplementedError(
            "Cette methode doit etre implementee dans les sous-classes."
        )
