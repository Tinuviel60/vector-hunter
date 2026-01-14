"""
Module mathématique de base.

Fournit les primitives mathématiques pour le moteur :
- Vector2D : Vecteurs 2D
- Geometry : Fonctions géométriques (SAT, projections...)
- Fonctions utilitaires : hex_to_rgb, clamp, normalize...
"""

from .vector import Vector2D
from .geometry import Geometry
from .numeric import (
    hex_to_rgb,
    clamp,
    normalize,
    normalize_ratio,
    normalize_log,
    normalize_ratio_log,
    exponential_scale,
    gaussian_between,
)

__all__ = [
    "Vector2D",
    "Geometry",
    "hex_to_rgb",
    "clamp",
    "normalize",
    "normalize_ratio",
    "normalize_log",
    "normalize_ratio_log",
    "exponential_scale",
    "gaussian_between",
]
