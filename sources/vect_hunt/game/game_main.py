from vect_hunt.engine.worlds import World
from vect_hunt.engine.rendering import Renderer
from vect_hunt.engine.objects import GameObject, GameObjectFactory
from vect_hunt.engine.core import Vector2D

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

    def initialize(self) -> None:
        """
        Initialise les composants du jeu.
        """
        self.world = World()

        # Créer le joueur via template avec InputComponent intégré
        player = GameObjectFactory.from_template(
            "player.json",
            position=Vector2D(100, 200),
            input_system=self.world.input_system,
        )
        self.world.add_game_object(player)

        # Créer un ennemi via template
        enemy = GameObjectFactory.from_template(
            "targets/basic.json", position=Vector2D(600, 200)
        )
        self.world.add_game_object(enemy)

        # Créer un obstacle via template
        obstacle = GameObjectFactory.from_template(
            "walls/standard.json", position=Vector2D(400, 300)
        )
        self.world.add_game_object(obstacle)

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
        # Mettre à jour le monde (inputs + GameObjects + collisions)
        self.world.update(delta_time)
        self.world.update_collisions(delta_time)
        self.world.collision_resolution_system.update(delta_time)

    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render(self.world)
