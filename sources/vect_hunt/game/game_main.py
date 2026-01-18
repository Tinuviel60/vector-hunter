from vect_hunt.engine.worlds import World
from vect_hunt.engine.rendering import Renderer
from vect_hunt.engine.objects import GameObject, GameObjectFactory
from vect_hunt.engine.core import Vector2D

import pygame


class Game:
    """
    Classe principale du jeu.

    Gère l'initialisation, la boucle d'update, et le rendu.

    Attributes
    ----------
    start_render : bool
        Indique si le rendu a été initialisé.
    gameObjects : dict[str, GameObject]
        Dictionnaire des objets de jeu du gameplay.
    world : World
        Monde de jeu contenant les systèmes et objets.
    renderer : Renderer | None
        Renderer associé, défini après initiate_rendering.
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

        factory = GameObjectFactory()

        # Creer le joueur via template avec InputComponent integre
        player = factory.from_template(
            "player.json",
            position=Vector2D(100, 200),
            input_system=self.world.input_system,
        )
        self.world.add_game_object(player)

        # Creer un ennemi via template
        enemy = factory.from_template("targets/basic.json", position=Vector2D(600, 200))
        self.world.add_game_object(enemy)

        # Creer un obstacle via template
        obstacle = factory.from_template(
            "walls/standard.json", position=Vector2D(400, 300)
        )
        self.world.add_game_object(obstacle)

        # Creer une caisse via template
        crate = factory.from_template("objects/crate.json", position=Vector2D(100, 300))
        self.world.add_game_object(crate)

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

        Parameters:
        -----------
        delta_time : float
            Le temps écoulé depuis la dernière mise à jour (en secondes).
        """
        # Mettre à jour le monde (inputs + GameObjects + collisions)
        self.world.update(delta_time)

        self.world.external_forces_system.apply_gravity(self.world, delta_time)

        # Détecter les collisions une fois pour les événements
        self.world.update_collisions(delta_time)

        max_passes = 6  # TODO : Mettre dans un json de config
        passes = 0

        # Itérer plusieurs fois pour une meilleure résolution des collisions
        for _ in range(max_passes):
            passes += 1
            collisions, _, collision_info = (
                self.world.collider_system.detect_collisions(self.world)
            )
            moved = self.world.collision_resolution_system.update_from_collisions(
                list(collisions),
                collision_info,
            )
            if not moved:
                break

    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render(self.world)
