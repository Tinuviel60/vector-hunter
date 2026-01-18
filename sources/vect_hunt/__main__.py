import logging
import pygame
from vect_hunt.game import Game
from vect_hunt.engine.resources.loaders import DataLoader
from vect_hunt.engine.resources.paths import Paths
from vect_hunt.engine.simulation import GameLoop
from .logging_config import setup_logging

# Import dynamique des components
from vect_hunt.engine.utils.component_loader import load_all_components

logger = logging.getLogger(__name__)

"""
Configuration globale de l'application et mise en place de
la boucle principale du jeu.

Les paramètres graphiques et de simulation sont chargés depuis
assets/data/configs/app.json
"""


def bootstrap() -> dict:
    """
    Charge la configuration et prépare le logging.

    Returns
    -------
    dict
        Configuration de l'application.
    """
    app_config = DataLoader.load_json("configs/app.json")
    log_level_str = app_config["logging"]["level"]
    log_level = getattr(logging, log_level_str, logging.WARNING)
    setup_logging(
        log_level=log_level,
        enable_console=app_config["logging"]["enable_console"],
    )
    return app_config


def main(app_config: dict) -> None:
    """
    Fonction principale de l'application.
    Initialise Pygame, crée la fenêtre,
    et lance la boucle principale du jeu.

    Parameters
    ----------
    app_config : dict
        Configuration de l'application.
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

        game = Game()
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
    finally:
        pygame.quit()


if __name__ == "__main__":
    # Lancer l'application principale
    app_config = bootstrap()
    main(app_config)
