"""
Configuration centralisée du système de logging pour la simulation.

Ce module doit être appelé UNE SEULE FOIS au démarrage du programme.
Tous les autres modules utilisent simplement logging.getLogger(__name__).
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class NumberedRotatingFileHandler(RotatingFileHandler):
    """
    RotatingFileHandler avec numérotation avant l'extension :
    simulation_0.log, simulation_1.log, etc.

    Attributes
    ----------
    None
    """

    def doRollover(self) -> None:
        """
        Effectue le rollover en renommant les fichiers :
        simulation_0.log -> simulation_1.log, etc.
        """
        if self.stream:
            self.stream.close()

        # Décale les fichiers existants (du plus ancien au plus récent)
        for i in range(self.backupCount - 1, -1, -1):
            sfn = f"{self.baseFilename.rsplit('.', 1)[0]}_{i}.log"
            dfn = f"{self.baseFilename.rsplit('.', 1)[0]}_{i + 1}.log"
            Path(sfn).rename(dfn) if Path(sfn).exists() else None

        # Renomme le fichier courant en _0
        Path(self.baseFilename).rename(f"{self.baseFilename.rsplit('.', 1)[0]}_0.log")

        # Recrée le fichier courant
        self.mode = "w"
        self.stream = self._open()


def setup_logging(
    log_level: int = logging.INFO,
    enable_console: bool = True,
) -> None:
    """
    Configure le système de logging global.

    Parameters
    ----------
    log_level : int
        Niveau minimum des logs (logging.INFO, DEBUG, WARNING, etc.).
    enable_console : bool
        Si True, affiche les logs dans la console en plus des fichiers.
    """

    # ------------------------------------------------------------
    # Résolution du chemin vers ./logs/simulation_logs
    # ------------------------------------------------------------

    project_root = Path(__file__).resolve().parents[2]
    log_dir = project_root / "logs" / "simulation_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Logger racine du projet
    # ------------------------------------------------------------

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Éviter les handlers en double si setup_logging est rappelé
    if root_logger.handlers:
        return

    # ------------------------------------------------------------
    # Format des logs
    # ------------------------------------------------------------

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ------------------------------------------------------------
    # Handler fichier principal
    # ------------------------------------------------------------

    file_handler = NumberedRotatingFileHandler(
        log_dir / "simulation.log",
        maxBytes=5_000_000,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # ------------------------------------------------------------
    # Handler console (optionnel)
    # ------------------------------------------------------------

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    root_logger.info("Logging system initialized")
