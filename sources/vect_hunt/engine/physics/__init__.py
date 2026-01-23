"""
Module physique du moteur.

Gère les collisions et la détection de collision.
"""

from .collision_tracker import CollisionTracker
from .physic_material import CombineMode, PhysicMaterial

__all__ = [
    "CollisionTracker",
    "PhysicMaterial",
    "CombineMode",
]
