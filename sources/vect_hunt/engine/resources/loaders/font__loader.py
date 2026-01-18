import pygame
from collections import OrderedDict
from pathlib import Path
from vect_hunt.engine.resources.loaders.base_loader import BaseLoader
from vect_hunt.engine.resources.paths import FONTS_DIR

"""
Chargement et mise en cache des polices de caractères.
"""


class FontLoader(BaseLoader):
    """
    Gestionnaire de chargement des polices.

    Les polices sont identifiées par leur chemin relatif
    et leur taille, car pygame génère une instance par taille.

    Attributes
    ----------
    None
    """

    _cache: "OrderedDict[tuple[Path, int], pygame.font.Font]" = OrderedDict()
    # Taille maximale d'un fichier de police (2 Mo)
    _max_bytes = 2 * 1024 * 1024
    # Nombre maximal d'entrees en cache
    _max_items = 64

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
        path = cls._resolve_path(
            FONTS_DIR,
            relative_path,
            allowed_extensions={".ttf", ".otf"},
            max_bytes=cls._max_bytes,
        )
        key = (path, size)

        cached = cls._cache_get(key)
        if cached is not cls._MISSING:
            return cached

        font = pygame.font.Font(path, size)
        cls._cache_put(key, font, cls._max_items)
        return font
