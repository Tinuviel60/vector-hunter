from typing import TYPE_CHECKING

from vect_hunt.worlds import World
from vect_hunt.rendering import Renderer

if TYPE_CHECKING:
    import pygame


class Game:
    """
    Main game class that handles initialization, update loop, and rendering.
    """

    def __init__(self):
        """
        Initialize le jeu pour la partie.

        """
        self.start_render: bool = False
        self.initialize()

    def initialize(self) -> None:
        """
        Initialise les composants du jeu.
        """
        # TODO: Initialize game components, load assets, etc.
        self.world = World()

        # On affecte un renderer au jeu

    def initiate_rendering(self, screen: pygame.Surface) -> None:
        """
        Démarre le rendu graphique du jeu.

        Parameters:
        -----------
        screen : pygame.Surface
            La surface Pygame où le jeu sera rendu.
        """
        self.renderer = Renderer(screen)
        self.start_render = True

    def update(self, delta_time: float) -> None:
        """
        Met à jour la logique du jeu.

        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour (en secondes).
        """
        # TODO: Update game state, entities, physics, etc.
        pass

    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render(self.world)
