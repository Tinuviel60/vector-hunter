from vect_hunt.engine.scenes import Scene
from vect_hunt.engine.rendering import Renderer
from vect_hunt.engine.objects import GameObject, GameObjectFactory
from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.simulation import SimulationScheduler

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
    scene : Scene
        Scène de jeu contenant les objets.
    simulation_scheduler : SimulationScheduler
        Orchestrateur de la simulation.
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
        self.scene = Scene()
        self.simulation_scheduler = SimulationScheduler(self.scene)

        factory = GameObjectFactory()

        # Creer le joueur via template avec InputComponent integre
        player = factory.from_template(
            "player.json",
            position=Vector2D(100, 200),
            input_system=self.simulation_scheduler.input_system,
        )
        self.scene.add_game_object(player)

        # Creer un ennemi via template
        enemy = factory.from_template("targets/basic.json", position=Vector2D(600, 200))
        self.scene.add_game_object(enemy)

        # Creer un obstacle via template
        obstacle = factory.from_template(
            "walls/standard.json", position=Vector2D(400, 300)
        )
        self.scene.add_game_object(obstacle)

        # Creer une caisse via template
        crate = factory.from_template("objects/crate.json", position=Vector2D(400, 100))
        self.scene.add_game_object(crate)

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
        self.simulation_scheduler.update(delta_time)

    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render(self.scene)
