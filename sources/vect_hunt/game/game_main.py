# vect_hunt/game/game_main.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import pygame

from vect_hunt.engine.core import TagSystem
from vect_hunt.engine.objects import GameObject, GameObjectFactory
from vect_hunt.engine.rendering import Renderer
from vect_hunt.engine.rendering.font import FontSystem
from vect_hunt.engine.scenes import Scene, SceneFactory
from vect_hunt.engine.simulation import SimulationScheduler

if TYPE_CHECKING:
    from vect_hunt.engine.resources import ResourceRegistry


@dataclass(frozen=True)
class GameWiring:
    """
    Objet de composition contenant les dépendances "moteur" déjà assemblées.

    Cet objet évite d'avoir un gros dict global diffusé partout, et rend
    explicite ce qui est injecté dans Game.

    Attributes
    ----------
    scene : Scene
        Scène active.
    tag_system : TagSystem
        Système de tags/collisions (mapping chargé depuis config).
    simulation_scheduler : SimulationScheduler
        Orchestrateur de la simulation (inputs + systèmes physiques).
    """
    scene: Scene
    tag_system: TagSystem
    simulation_scheduler: SimulationScheduler


class Game:
    """
    Classe principale du jeu.

    Cette classe ne fait pas de lecture de fichiers ni d'accès à l'infrastructure.
    Elle reçoit des objets déjà construits (scene, scheduler, etc.) et orchestre
    update/render.

    Attributes
    ----------
    start_render : bool
        Indique si le rendu a été initialisé.
    gameObjects : dict[str, GameObject]
        Dictionnaire d'objets de gameplay (optionnel / futur usage).
    scene : Scene
        Scène active.
    simulation_scheduler : SimulationScheduler
        Orchestrateur de la simulation.
    renderer : Renderer | None
        Renderer (initialisé via initiate_rendering).
    """

    def __init__(self, wiring: GameWiring, configs: dict[str, dict[str, Any]]) -> None:
        """
        Initialise le jeu avec ses dépendances déjà assemblées.

        Parameters
        ----------
        wiring : GameWiring
            Dépendances moteur prêtes (scene, tag_system, scheduler).
        configs : dict[str, dict[str, Any]]
            Configurations JSON déjà chargées (renderer/fonts/inputs/etc.).
        """
        self.start_render: bool = False
        self.renderer: Renderer | None = None

        self.gameObjects: dict[str, GameObject] = {}

        self.scene: Scene = wiring.scene
        self.tag_system: TagSystem = wiring.tag_system
        self.simulation_scheduler: SimulationScheduler = wiring.simulation_scheduler

        self._configs = configs

    @classmethod
    def from_resources(cls, resources: "ResourceRegistry", level_name: str) -> "Game":
        """
        Construit un Game à partir d'un ResourceRegistry (données en mémoire).

        Cette méthode centralise l'assemblage (factories/systèmes) et évite
        de disperser la logique d'initialisation dans __init__ ou update/render.

        Parameters
        ----------
        resources : ResourceRegistry
            Registre des ressources JSON déjà chargées.
        level_name : str
            Nom du fichier de niveau (ex: "level_00.json").

        Returns
        -------
        Game
            Instance du jeu prête à être utilisée (hors rendu Pygame).
        """
        # 1) Construire TagSystem depuis la config collision (mapping tags/collisions)
        collision_config = resources.configs["collision.json"]
        tag_system = TagSystem(collision_config)

        # 2) Charger la scène via SceneFactory (pas de "pré-scène" temporaire)
        #    On crée d'abord un scheduler avec une scène temporaire minimale,
        #    puis on réinjecte la scène finale dans le scheduler. (Voir note plus bas)
        #
        # TODO : Revenir voir plus tard pour améliorer cette étape.
        # NOTE: Si ton SimulationScheduler peut être instancié sans Scene, ou accepter
        # un setter unique "set_scene(scene)" qui propage proprement, c'est mieux.
        # Ici on reste compatible avec ton moteur actuel.

        # Scène minimale (pour init scheduler/input_system)
        base_units = resources.scenes[level_name]["scene"]["units"]
        bootstrap_scene = Scene.from_data({"units": base_units})

        simulation_scheduler = SimulationScheduler(
            bootstrap_scene,
            input_config=resources.configs["inputs.json"],
            tag_system=tag_system,
        )

        # Factories (utilisent des dicts JSON déjà en mémoire)
        game_object_factory = GameObjectFactory(
            templates=resources.templates,
            materials=resources.materials,
        )
        scene_factory = SceneFactory(
            game_object_factory=game_object_factory,
            scenes=resources.scenes,
        )

        # Scène finale (les GameObjects peuvent recevoir input_system via context)
        final_scene = scene_factory.from_template(
            level_name,
            input_system=simulation_scheduler.input_system,
        )

        # Réinjection propre (garde la compatibilité avec ton code actuel)
        simulation_scheduler.scene = final_scene
        simulation_scheduler.collision_resolution_system.scene = final_scene

        wiring = GameWiring(
            scene=final_scene,
            tag_system=tag_system,
            simulation_scheduler=simulation_scheduler,
        )
        return cls(wiring=wiring, configs=resources.configs)

    def initiate_rendering(self, screen: pygame.Surface) -> None:
        """
        Initialise le rendu graphique du jeu.

        Parameters
        ----------
        screen : pygame.Surface
            Surface Pygame sur laquelle dessiner.
        """
        font_system = FontSystem(self._configs["fonts.json"])
        self.renderer = Renderer(screen, self._configs["renderer.json"], font_system)
        self.start_render = True

    def update(self, delta_time: float) -> None:
        """
        Met à jour la logique du jeu.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière mise à jour (secondes).
        """
        self.simulation_scheduler.update(delta_time)

    def render(self) -> None:
        """
        Dessine l'état courant du jeu.
        """
        if self.renderer is None:
            return
        self.renderer.render(self.scene)
