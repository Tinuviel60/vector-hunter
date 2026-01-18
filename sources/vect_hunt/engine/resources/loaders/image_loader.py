import pygame
from collections import OrderedDict
from pathlib import Path
from vect_hunt.engine.resources.loaders.base_loader import BaseLoader
from vect_hunt.engine.resources.paths import IMAGES_DIR

"""
Chargement et mise en cache des images.
"""


class ImageLoader(BaseLoader):
    """
    Gestionnaire de chargement d'images.

    Centralise le chargement pygame et évite les rechargements multiples.

    Attributes
    ----------
    None
    """

    _cache: "OrderedDict[Path, pygame.Surface]" = OrderedDict()
    # Taille maximale d'un fichier image (8 Mo)
    _max_bytes = 8 * 1024 * 1024
    # Dimensions maximales autorisees
    _max_width = 4096
    _max_height = 4096
    # Nombre maximal d'entrees en cache
    _max_items = 256

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
        path = cls._resolve_path(
            IMAGES_DIR,
            relative_path,
            allowed_extensions={".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"},
            max_bytes=cls._max_bytes,
        )

        cached = cls._cache_get(path)
        if cached is not cls._MISSING:
            return cached

        surface = pygame.image.load(path).convert_alpha()
        width, height = surface.get_size()
        if width > cls._max_width or height > cls._max_height:
            raise ValueError(
                f"Image trop grande: {width}x{height} (max {cls._max_width}x{cls._max_height})"
            )
        cls._cache_put(path, surface, cls._max_items)
        return surface
