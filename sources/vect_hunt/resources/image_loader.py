import pygame
from pathlib import Path
from vect_hunt.resources.paths import IMAGES_DIR

"""
Chargement et mise en cache des images.
"""


class ImageLoader:
    """
    Gestionnaire de chargement d'images.

    Centralise le chargement pygame et évite les rechargements multiples.
    """

    _cache: dict[Path, pygame.Surface] = {}

    @classmethod
    def load(cls, relative_path: str) -> pygame.Surface:
        """
        Charge une image depuis le dossier images.

        Parameters
        ----------
        relative_path : str
            Chemin relatif depuis assets/images

        Returns
        -------
        pygame.Surface
            Surface pygame chargée
        """
        path = IMAGES_DIR / relative_path

        if path not in cls._cache:
            cls._cache[path] = pygame.image.load(path).convert_alpha()

        return cls._cache[path]
