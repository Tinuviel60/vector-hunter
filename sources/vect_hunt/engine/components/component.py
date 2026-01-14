from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject


class Component(ABC):
    """
    Classe abstraite de base pour tous les composants attachables à un GameObject.

    Un Component représente une capacité ou un comportement spécifique
    (rendu, physique, input, IA, etc.).

    Il est attaché à un unique GameObject et peut réagir aux événements
    du cycle de vie de l'objet (update, collisions, triggers).
    """

    def __init__(self) -> None:
        """
        Initialise le composant.

        Le GameObject sera assigné lors de l'appel à on_attach().
        """
        self.game_object: "GameObject | None" = None
        self.active: bool = True

    def on_attach(self, game_object: "GameObject") -> None:
        """
        Appelé lorsque le composant est attaché à un GameObject.

        Assigne le GameObject et permet des initialisations supplémentaires
        dans les sous-classes.

        Parameters
        ----------
        game_object : GameObject
            Le GameObject auquel ce composant est attaché.
        """
        self.game_object = game_object

    def on_detach(self) -> None:
        """
        Appelé lors du détachement du composant.

        Libère la référence au GameObject et permet du nettoyage
        supplémentaire dans les sous-classes.
        """
        self.game_object = None

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Mise à jour du composant appelée chaque frame.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass

    def on_collision(self, other: "GameObject") -> None:
        """
        Appelé lors d'une collision persistante.
        """
        pass

    def on_enter_collision(self, other: "GameObject") -> None:
        """
        Appelé au début d'une collision.
        """
        pass

    def on_exit_collision(self, other: "GameObject") -> None:
        """
        Appelé à la fin d'une collision.
        """
        pass

    def on_trigger(self, other: "GameObject") -> None:
        """
        Appelé lors d'un trigger persistante.
        """
        pass

    def on_enter_trigger(self, other: "GameObject") -> None:
        """
        Appelé au début d'un trigger.
        """
        pass

    def on_exit_trigger(self, other: "GameObject") -> None:
        """
        Appelé à la fin d'un trigger.
        """
        pass
