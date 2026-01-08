import logging

import pygame

from vect_hunt.game import Game
from .logging_config import setup_logging

logger = logging.getLogger(__name__)

PROFILING = False

if PROFILING:
    import cProfile
    import pstats

    TICK_LIMIT = 10
    REPORT_NB = 40

"""
Configuration globale de l'application et mise en place de 
la boucle principale du jeu.

Paramètres graphiques et de simulation:
- WINDOW_WIDTH: Largeur de la fenêtre en pixels
- WINDOW_HEIGHT: Hauteur de la fenêtre en pixels

- FPS: Fréquence de rendu graphique en frames par seconde
- SIM_DT: Pas de temps de la simulation en secondes
"""

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60  # Fréquence de rendu graphique (frames par seconde)
SIM_DT = 1 / FPS  # Pas de temps de la simulation (secondes)

setup_logging(
    log_level=logging.WARNING,  # DEBUG, INFO, WARNING
    enable_console=True,
)


def main() -> None:
    """
    Fonction principale de l'application.
    Initialise Pygame, crée la fenêtre,
    et lance la boucle principale du jeu.
    """

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Vector Hunter")
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

        # Temps réel écoulé depuis la dernière frame (en secondes)
        frame_time = clock.tick(FPS) / 1000.0

        # Accumuler le temps réel
        accumulator += frame_time

        if accumulator > SIM_DT * 4:
            logger.warning(
                "Temps d'execution trop long, limitation de l'accumulateur | accumulator=%f | frame_time=%f",
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
