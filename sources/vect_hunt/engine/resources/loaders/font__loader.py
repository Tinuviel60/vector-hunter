import pygame
from pathlib import Path
from vect_hunt.engine.resources.paths import FONTS_DIR

"""
Chargement et mise en cache des polices de caractères.
"""


class FontLoader:
    """
    Gestionnaire de chargement des polices.

    Les polices sont identifiées par leur chemin relatif
    et leur taille, car pygame génère une instance par taille.

    Attributes
    ----------
    None
    """

    _cache: dict[tuple[Path, int], pygame.font.Font] = {}

    @classmethod
    def load(cls, relative_path: str, size: int) -> pygame.font.Font:
        """
        Charge une police depuis le dossier fonts.

        Parameters
        ----------
        relative_path : str
            Chemin relatif depuis assets/font
        size : int
            Taille de la police

        Returns
        -------
        pygame.font.Font
            Instance de la police chargée
        """
        path = FONTS_DIR / relative_path
        key = (path, size)

        if key not in cls._cache:
            cls._cache[key] = pygame.font.Font(path, size)

        return cls._cache[key]
