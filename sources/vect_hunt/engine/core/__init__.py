"""
Module Core du moteur.

Fournit les composants fondamentaux :
- math : primitives mathématiques
- transform : transformation spatiale
- tag : système de tags
"""

from .math import Vector2D, Geometry, hex_to_rgb
from .transform import Position2D, Rotation, Transform
from .tag import Tag
from .tag_system import TagSystem, CAN_COLLIDE, CAN_DESTROY, CAN_PICKUP

__all__ = [
    # Math
    "Vector2D",
    "Geometry",
    "hex_to_rgb",
    # Transform
    "Position2D",
    "Rotation",
    "Transform",
    # Tags
    "Tag",
    "TagSystem",
    "CAN_COLLIDE",
    "CAN_DESTROY",
    "CAN_PICKUP",
]
