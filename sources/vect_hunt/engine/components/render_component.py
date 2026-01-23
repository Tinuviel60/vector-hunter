from abc import abstractmethod
from vect_hunt.engine.components.component import Component


class RenderComponent(Component):
    """
    Classe abstraite représentant un composant de rendu.

    Un RenderComponent est responsable de dessiner un GameObject
    en fonction de son Transform, sans logique métier.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    """

    component_name = "render"

    def __init__(self):
        """
        Initialise le composant de rendu.
        """
        super().__init__()

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Les composants de rendu n'ont généralement pas de logique dans update.

        Le rendu est géré par le Renderer via la méthode render().

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        raise NotImplementedError

    @abstractmethod
    def render(self, surface) -> None:
        """
        Dessine l'objet sur la surface donnée.

        Utilise self.parent.transform pour obtenir la position,
        rotation et échelle du GameObject.

        Parameters
        ----------
        surface
            Surface de rendu (ex: pygame.Surface).
        """
        raise NotImplementedError
