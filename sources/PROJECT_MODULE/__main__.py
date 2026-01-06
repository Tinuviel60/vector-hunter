import logging

from .logging_config import setup_logging

logger = logging.getLogger(__name__)

PROFILING = True

if PROFILING:
    import cProfile
    import pstats

    TICK_LIMIT = 10
    REPORT_NB = 40

"""

"""

setup_logging(
    log_level=logging.WARNING,  # DEBUG, INFO, WARNING
    enable_console=True,
)

def main():
    """
   
    """


    while running:
       # Perform main loop operations here

        if PROFILING:
            global TICK_LIMIT
            TICK_LIMIT -= 1
            if TICK_LIMIT <= 0:
                running = False


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(REPORT_NB)
