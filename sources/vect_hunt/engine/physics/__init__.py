"""
Module physique du moteur.

Gère les collisions et la détection de collision.
"""

from .collider import Collider, BoxCollider, CircleCollider
from .collider_system import ColliderSystem
from .collision_tracker import CollisionTracker

__all__ = [
    "Collider",
    "BoxCollider",
    "CircleCollider",
    "ColliderSystem",
    "CollisionTracker",
]
