"""
Module physique du moteur.

Gère les collisions et la détection de collision.
"""

from .collider import Collider, BoxCollider, CircleCollider
from .collider_system import ColliderSystem
from .collision_tracker import CollisionTracker
from .physic_material import PhysicMaterial
from .external_forces_system import ExternalForcesSystem

__all__ = [
    "Collider",
    "BoxCollider",
    "CircleCollider",
    "ColliderSystem",
    "CollisionTracker",
    "PhysicMaterial",
    "ExternalForcesSystem",
]
