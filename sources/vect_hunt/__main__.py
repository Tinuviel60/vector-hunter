import logging

import pygame

from vect_hunt.game import Game
from vect_hunt.engine.resources import DataLoader
from .logging_config import setup_logging

logger = logging.getLogger(__name__)

# Charger la configuration de l'application
app_config = DataLoader.load_json("configs/app.json")

# Configuration du profiling
PROFILING = app_config["profiling"]["enabled"]

if PROFILING:
    import cProfile
    import pstats

    TICK_LIMIT = app_config["profiling"]["tick_limit"]
    REPORT_NB = app_config["profiling"]["report_lines"]

"""
Configuration globale de l'application et mise en place de
la boucle principale du jeu.

Les paramètres graphiques et de simulation sont chargés depuis
assets/data/configs/app.json
"""

# Extraire les paramètres depuis la config
WINDOW_WIDTH = app_config["window"]["width"]
WINDOW_HEIGHT = app_config["window"]["height"]
WINDOW_TITLE = app_config["window"]["title"]
FPS = app_config["simulation"]["fps"]
SIM_DT = app_config["simulation"]["fixed_timestep"]

# Convertir le niveau de log string en constante logging
log_level_str = app_config["logging"]["level"]
log_level = getattr(logging, log_level_str, logging.WARNING)

setup_logging(
    log_level=log_level,
    enable_console=app_config["logging"]["enable_console"],
)


def main() -> None:
    """
    Fonction principale de l'application.
    Initialise Pygame, crée la fenêtre,
    et lance la boucle principale du jeu.
    """

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    game = Game()
    game.initiate_rendering(screen)

    running = True
    accumulator = 0.0  # Accumulateur de temps réel

    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Transmettre les événements à l'InputSystem
            game.world.input_system.process_event(event)

        # Temps réel écoulé depuis la dernière frame (en secondes)
        frame_time = clock.tick(FPS) / 1000.0

        # Accumuler le temps réel
        accumulator += frame_time

        if accumulator > SIM_DT * 4:
            logger.warning(
                "Temps d'execution trop long, limitation de l'accumulateur | "
                "accumulator=%f | frame_time=%f",
                accumulator,
                frame_time,
            )
            accumulator = (
                SIM_DT * 4
            )  # Limiter l'accumulateur pour éviter les spirales de la mort

        while accumulator >= SIM_DT:
            # Mettre à jour la simulation avec un pas de temps fixe
            game.update(SIM_DT)
            accumulator -= SIM_DT

        # Rendu graphique
        game.render()

        # Utiliser pour stopper la boucle lors du profiling
        if PROFILING:
            global TICK_LIMIT
            TICK_LIMIT -= 1
            if TICK_LIMIT <= 0:
                running = False


if __name__ == "__main__":
    # Lancer l'application principale avec ou sans profiling
    if not PROFILING:
        main()
    else:
        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(REPORT_NB)
