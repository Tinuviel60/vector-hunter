from typing import TYPE_CHECKING

from vect_hunt.worlds import World
from vect_hunt.rendering import Renderer
from vect_hunt.objects import GameObject
from vect_hunt.core import *


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

        self.initialize_game_objects("Object1", position=Vector2D(200, 200))
        self.initialize_game_objects("Object2", position=Vector2D(400, 200))
        self.initialize_game_objects("Object3", position=Vector2D(200, 400))
        self.initialize_game_objects("Object4", position=Vector2D(400, 400))

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

    def initialize_game_objects(
        self,
        name: str = "Object",
        position: Vector2D = Vector2D(0, 0),
        rotation: float = 0.0,
    ):
        """
        Initialise et ajoute un GameObject simple au monde.

        Parameters
        ----------
        name : str
            Nom de l'objet.
        position : Vector2D
            Position initiale de l'objet.
        rotation : float
            Rotation initiale de l'objet en degrés.
        """
        transform = Transform(position, rotation)
        collider = CircleCollider()
        collider2 = BoxCollider(Vector2D(0, 0))

        gameObject = GameObject(name, transform)
        gameObject.add_collider(collider)
        gameObject.add_collider(collider2)

        self.world.add_game_object(gameObject)
