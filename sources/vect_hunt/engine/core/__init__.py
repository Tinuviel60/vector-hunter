"""
Module Core du moteur.

Fournit les composants fondamentaux :
- math : primitives mathématiques
- transform : transformation spatiale
- tag : système de tags
"""

from .math import Vector2D, Geometry, Numeric
from .render_ops import RenderOps
from .transform import Position2D, Rotation, Transform
from .tag import Tag
from .tag_system import TagSystem

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
