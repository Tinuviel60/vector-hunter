"""
Module physique du moteur.

Gère les collisions et la détection de collision.
"""

from .collision_tracker import CollisionTracker
from .physic_material import PhysicMaterial, CombineMode

__all__ = [
    "CollisionTracker",
    "PhysicMaterial",
    "CombineMode",
]
