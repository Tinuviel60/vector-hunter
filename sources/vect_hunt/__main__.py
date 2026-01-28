# vect_hunt/__main__.py

import cProfile
import logging
import pstats
import time
from pathlib import Path
from typing import Any

import pygame
from vect_hunt.engine.resources.paths import Paths
from vect_hunt.engine.resources.readers.config_reader import ConfigReader
from vect_hunt.engine.resources.readers.material_reader import MaterialReader
from vect_hunt.engine.resources.readers.scene_reader import SceneReader
from vect_hunt.engine.resources.readers.template_reader import TemplateReader
from vect_hunt.engine.resources.resource_registry import ResourceRegistry
from vect_hunt.engine.simulation.game_loop import GameLoop
from vect_hunt.engine.utils.component_loader import load_all_components
from vect_hunt.game.game_main import Game
from vect_hunt.logging_config import setup_logging

logger = logging.getLogger(__name__)

"""
Point d'entrée de l'application.

- Charge la configuration et configure le logging
- Charge les ressources JSON en mémoire (registry)
- Charge dynamiquement les composants (plugins)
- Initialise Pygame, instancie le jeu et lance la boucle principale
"""


def bootstrap() -> dict[str, Any]:
    """
    Charge la configuration de l'application et configure le logging.

    Parameters
    ----------
    None

    Returns
    -------
    dict[str, Any]
        Configuration de l'application (chargée depuis app.json).
    """
    app_config = ConfigReader().load("app.json")

    log_level_str = app_config["logging"]["level"]
    log_level = getattr(logging, log_level_str, logging.WARNING)

    setup_logging(
        log_level=log_level,
        enable_console=app_config["logging"]["enable_console"],
    )
    return app_config


def build_resource_registry() -> ResourceRegistry:
    """
    Construit un registre typé des ressources JSON chargées au démarrage.

    L'objectif est de centraliser la lecture des fichiers (assets/data)
    dans le bootstrap, et d'injecter ensuite des structures de données
    (pas des Readers) dans le jeu et le moteur.

    Parameters
    ----------
    None

    Returns
    -------
    ResourceRegistry
        Registre des ressources JSON (configs, templates, scenes, materials).
    """
    return ResourceRegistry(
        configs=ConfigReader().configs,
        templates=TemplateReader().configs,
        scenes=SceneReader().configs,
        materials=MaterialReader().configs,
    )


def _run_with_cprofile(run_callable, profile_dir: str = "profiles") -> None:
    """
    Exécute une fonction en l'entourant d'un profilage cProfile,
    et écrit un fichier .prof.

    Parameters
    ----------
    run_callable : callable
        Fonction à exécuter (typiquement loop.run).
    profile_dir : str, optional
        Dossier de sortie des profils.

    Returns
    -------
    None
    """
    output_dir = Path(profile_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    profile_path = output_dir / f"cprofile-{timestamp}.prof"

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        run_callable()
    finally:
        profiler.disable()
        profiler.dump_stats(str(profile_path))

        # Affiche un top console pour lecture rapide
        stats = pstats.Stats(profiler).strip_dirs()
        stats.sort_stats("cumtime")  # temps cumulé = bon pour trouver le vrai goulet
        print("\n==== cProfile TOP (cumtime) ====")
        stats.print_stats(30)

        print(f"\nProfil sauvegardé : {profile_path}")
        print("Analyse détaillée : python -m pstats -s cumtime <fichier.prof>")
        print("Ou visuel : snakeviz <fichier.prof> (si installé)\n")


def main(app_config: dict[str, Any], resources: ResourceRegistry) -> None:
    """
    Lance l'application : init Pygame, instancie le jeu, et exécute la boucle.

    Parameters
    ----------
    app_config : dict[str, Any]
        Configuration de l'application (fenêtre, simulation, etc.).
    resources : ResourceRegistry
        Registre des ressources JSON en mémoire.
    """
    # Charger dynamiquement tous les components du moteur et du jeu
    load_all_components([str(Paths.COMPONENTS_DIR), str(Paths.GAME_DIR)])

    window_width = app_config["window"]["width"]
    window_height = app_config["window"]["height"]
    window_title = app_config["window"]["title"]
    fps = app_config["simulation"]["fps"]
    sim_dt = app_config["simulation"]["fixed_timestep"]

    pygame.init()
    try:
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(window_title)
        clock = pygame.time.Clock()

        # Créer le jeu déjà "assemblé" (scene + scheduler, etc.)
        game = Game.from_resources(
            resources=resources,
            level_name="level_10.json",
        )

        # Le rendu dépend de Pygame : initialisation après set_mode()
        game.initiate_rendering(screen)

        loop = GameLoop(
            game=game,
            scheduler=game.simulation_scheduler,
            clock=clock,
            fps=fps,
            sim_dt=sim_dt,
            logger=logger,
        )
        loop.run()
        #_run_with_cprofile(loop.run)
    finally:
        pygame.quit()


if __name__ == "__main__":
    app_config = bootstrap()
    resources = build_resource_registry()
    main(app_config, resources)
