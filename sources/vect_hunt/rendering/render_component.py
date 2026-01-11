from abc import ABC, abstractmethod
from vect_hunt.core import Transform


class RenderComponent(ABC):
    """
    Classe abstraite représentant un composant de rendu.

    Un RenderComponent est responsable de dessiner un GameObject
    en fonction de son Transform, sans logique métier.
    """

    @abstractmethod
    def __init__(self, transform: Transform):
        self.transform = transform

    @abstractmethod
    def render(self, surface, transform: Transform) -> None:
        """
        Dessine l'objet sur la surface donnée.

        Parameters
        ----------
        surface
            Surface de rendu (ex: pygame.Surface).
        transform : Transform
            Transformation spatiale du GameObject.
        """
        raise NotImplementedError
