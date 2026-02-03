"""
Module mathématique de base.

Fournit les primitives mathématiques pour le moteur :
- Vector2D : Vecteurs 2D
- Geometry : Fonctions géométriques (SAT, projections...)
- Numeric : utilitaires numériques (clamp, etc.)
"""

from .geometry import Geometry
from .manifold import Manifold
from .numeric import Numeric
from .tolerance import Tolerence
from .vector import Vector2D

__all__ = [
    "Vector2D",
    "Geometry",
    "Numeric",
    "Tolerence",
    "Manifold",
]
