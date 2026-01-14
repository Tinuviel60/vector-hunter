"""
Module de gestion des ressources.

Charge et gère les assets (images, sons, données, polices).
"""

from .loaders.data_loader import DataLoader
from .loaders.image_loader import ImageLoader
from .loaders.sound_loader import SoundLoader
from .loaders.font__loader import FontLoader
from .paths import Paths

__all__ = ["DataLoader", "ImageLoader", "SoundLoader", "FontLoader", "Paths"]
