from vect_hunt.worlds import World
from vect_hunt.rendering import Renderer
from vect_hunt.objects import GameObject, GameObjectFactory
from vect_hunt.core import Vector2D, Tag

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

        self.gameObjects: dict[str, GameObject] = {}
        self.initialize()

        # Créer des objets depuis les templates JSON
        player = GameObjectFactory.from_template(
            "player.json", position=Vector2D(100, 200)
        )
        self.world.add_game_object(player)

        target = GameObjectFactory.from_template(
            "targets/basic.json", position=Vector2D(200, 200)
        )
        self.world.add_game_object(target)

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
        for name, game_object in self.world.game_objects.items():
            # TODO : Revoir la logique de déplacement
            if game_object.has_tag(Tag.PLAYER):
                game_object.move(5 * delta_time, 0)
            else:
                game_object.move(-5 * delta_time, 0)

        self.world.update_collisions(delta_time)

    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render(self.world)
