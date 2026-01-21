"""
Module de gestion des ressources.

Charge et gère les assets (images, sons, données, polices).
"""

from .paths import Paths
from .resource_registry import ResourceRegistry

__all__ = [
    "Paths",
    "ResourceRegistry",
]
