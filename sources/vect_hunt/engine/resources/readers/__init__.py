"""
Module de lecteurs de ressources.

Contient les readers pour différents types d'assets.
"""

from .config_reader import ConfigReader
from .material_reader import MaterialReader
from .template_reader import TemplateReader
from .scene_reader import SceneReader

__all__ = [
    "BaseReader",
    "ConfigReader",
    "MaterialReader",
    "TemplateReader",
    "SceneReader",
]
from .base_reader import BaseReader
