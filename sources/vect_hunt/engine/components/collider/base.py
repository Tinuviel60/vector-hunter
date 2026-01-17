from typing import Optional, TYPE_CHECKING

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.transform import Transform

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject


class Collider(Component):
    """
    Classe de base pour les colliders.
    Utilisee dans les systemes de collision pour definir des zones de collision.

    Attributes
    ----------
    parent : GameObject | None
        GameObject parent du collider.
    transform : Transform
        Transform local du collider.
    solid : bool
        Indique si le collider est solide.
    """

    def __init__(
        self,
        parent: Optional["GameObject"] = None,
        transform: Optional[Transform] = None,
        solid: bool = True,
    ):
        """
        Definit un collider de base avec un transform et une propriete de solidite.

        Parameters
        ----------
        parent : GameObject, optional
            L'objet de jeu auquel le collider appartient.
        transform : Transform
            Le transform associe au collider (offset et orientation locaux).
        solid : bool
            Indique si le collider interagit avec d'autres colliders ou non.
        """
        super().__init__()
        self.parent = parent
        self.transform = transform if transform is not None else Transform()
        self.solid = solid
        self.nb_collision = 0

    def on_attach(self, game_object: "GameObject") -> None:
        super().on_attach(game_object)
        self.parent = game_object

    def on_detach(self) -> None:
        super().on_detach()
        self.parent = None

    def update(self, delta_time: float) -> None:
        pass

    def get_geometry(self) -> dict:
        """
        Retourne la geometrie specifique du collider.
        Doit etre implemente dans les sous-classes.
        """
        raise NotImplementedError(
            "Cette methode doit etre implementee dans les sous-classes."
        )
