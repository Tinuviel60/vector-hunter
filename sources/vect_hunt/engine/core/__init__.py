"""
Module Core du moteur.

Fournit les composants fondamentaux :
- math : primitives mathématiques
- transform : transformation spatiale
- tag : système de tags
"""

from .math import Geometry, Numeric, Vector2D
from .render_ops import RenderOps
from .tag import Tag
from .tag_system import TagSystem
from .transform import Position2D, Rotation, Transform

__all__ = [
    # Math
    "Vector2D",
    "Geometry",
    "Numeric",
    "RenderOps",
    # Transform
    "Position2D",
    "Rotation",
    "Transform",
    # Tags
    "Tag",
    "TagSystem",
]
