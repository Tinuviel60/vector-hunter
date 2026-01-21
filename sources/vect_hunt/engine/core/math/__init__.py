"""
Module mathématique de base.

Fournit les primitives mathématiques pour le moteur :
- Vector2D : Vecteurs 2D
- Geometry : Fonctions géométriques (SAT, projections...)
- Numeric : utilitaires numériques (clamp, etc.)
"""

from .vector import Vector2D
from .geometry import Geometry
from .numeric import Numeric

__all__ = [
    "Vector2D",
    "Geometry",
    "Numeric",
]
