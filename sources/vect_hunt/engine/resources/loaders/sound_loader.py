from collections import OrderedDict
from pathlib import Path

import pygame
from vect_hunt.engine.resources.loaders.base_loader import BaseLoader
from vect_hunt.engine.resources.paths import SOUNDS_DIR

"""
Chargement et mise en cache des sons.
"""


class SoundLoader(BaseLoader):
    """
    Gestionnaire de chargement des sons.

    Attributes
    ----------
    None
    """

    _cache: "OrderedDict[Path, pygame.mixer.Sound]" = OrderedDict()
    # Taille maximale d'un fichier son (10 Mo)
    _max_bytes = 10 * 1024 * 1024
    # Duree maximale en secondes
    _max_seconds = 360.0
    # Nombre maximal d'entrees en cache
    _max_items = 128

    @classmethod
    def load(cls, relative_path: str) -> pygame.mixer.Sound:
        path = cls._resolve_path(
            SOUNDS_DIR,
            relative_path,
            allowed_extensions={".wav", ".ogg", ".mp3"},
            max_bytes=cls._max_bytes,
        )

        cached = cls._cache_get(path)
        if cached is not cls._MISSING:
            return cached

        sound = pygame.mixer.Sound(path)
        duration = sound.get_length()
        if duration > cls._max_seconds:
            raise ValueError(
                f"Son trop long: {duration:.2f}s (max {cls._max_seconds}s)"
            )
        cls._cache_put(path, sound, cls._max_items)
        return sound
