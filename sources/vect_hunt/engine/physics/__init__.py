"""
Module physique du moteur.

Gère les collisions et la détection de collision.
"""

from vect_hunt.engine.components.collider import (
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderComponent,
)
from .collider_system import ColliderSystem
from .collision_tracker import CollisionTracker
from .physic_material import PhysicMaterial
from .external_forces_system import ExternalForcesSystem

__all__ = [
    "ColliderComponent",
    "BoxColliderComponent",
    "CircleColliderComponent",
    "ColliderSystem",
    "CollisionTracker",
    "PhysicMaterial",
    "ExternalForcesSystem",
]
