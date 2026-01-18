from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.transform import Transform

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject


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
        game_object: Optional["GameObject"] = None,
        transform: Optional[Transform] = None,
        solid: bool = True,
    ):
        """
        Definit un collider de base avec un transform et une propriete de solidite.

        Parameters
        ----------
        game_object : GameObject, optional
            L'objet de jeu auquel le collider appartient.
        transform : Transform
            Le transform associe au collider (offset et orientation locaux).
        solid : bool
            Indique si le collider interagit avec d'autres colliders ou non.
        """
        super().__init__()
        self.game_object = game_object
        self.transform = transform if transform is not None else Transform()
        self.solid = solid
        self.nb_collision = 0

    def on_attach(self, game_object: "GameObject") -> None:
        """
        Appelé lorsque le composant est attaché à un GameObject.

        Parameters
        ----------
        game_object : GameObject
            Le GameObject auquel ce composant est attaché.
        """
        super().on_attach(game_object)
        self.game_object = game_object

    def on_detach(self) -> None:
        """ "
        Appelé lorsque le composant est détaché de son GameObject.

        Parameters
        ----------
        game_object : GameObject
            Le GameObject auquel ce composant était attaché.
        """
        super().on_detach()
        self.game_object = None

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
