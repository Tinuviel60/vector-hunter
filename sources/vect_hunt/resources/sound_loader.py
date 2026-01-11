import pygame
from pathlib import Path
from vect_hunt.resources.paths import SOUNDS_DIR

"""
Chargement et mise en cache des sons.
"""


class SoundLoader:
    _cache: dict[Path, pygame.mixer.Sound] = {}

    @classmethod
    def load(cls, relative_path: str) -> pygame.mixer.Sound:
        path = SOUNDS_DIR / relative_path

        if path not in cls._cache:
            cls._cache[path] = pygame.mixer.Sound(path)

        return cls._cache[path]
