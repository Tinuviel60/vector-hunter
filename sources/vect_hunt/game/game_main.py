from vect_hunt.engine.scenes import Scene, SceneFactory
from vect_hunt.engine.rendering import Renderer
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.resources.loaders.data_loader import DataLoader
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
        self.renderer: Renderer | None = None

        self.gameObjects: dict[str, GameObject] = {}
        self.initialize()

    # TODO : Ajouter un système de gestion des niveaux/scènes
    # TODO : Sortir la 1ere scene de la
    def initialize(self) -> None:
        """
        Initialise les composants du jeu.
        """
        self.scene = Scene.from_data(
            {"units": DataLoader.load_json("levels/level_00.json")["scene"]["units"]}
        )
        self.simulation_scheduler = SimulationScheduler(self.scene)

        factory = SceneFactory()
        self.scene = factory.from_template(
            "level_00.json",
            input_system=self.simulation_scheduler.input_system,
        )
        self.simulation_scheduler.scene = self.scene
        self.simulation_scheduler.collision_resolution_system.scene = self.scene

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
        if self.renderer is None:
            return
        self.renderer.render(self.scene)
