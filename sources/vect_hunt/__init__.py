"""
Vector Hunt - Jeu de tir 2D.

Architecture :
- engine/ : Moteur de jeu réutilisable
- game/ : Gameplay spécifique à Vector Hunt
"""

# Exposer l'API publique
from .engine import (
    # Core
    Vector2D,
    Transform,
    Tag,
    # Physics
    ColliderComponent,
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderSystem,
    # Objects
    GameObject,
    GameObjectFactory,
    # Rendering
    Renderer,
    # Resources
    DataLoader,
    ImageLoader,
    SoundLoader,
    FontLoader,
)

from .game import Game

__version__ = "0.1.0"

__all__ = [
    # Engine
    "Vector2D",
    "Transform",
    "Tag",
    "ColliderComponent",
    "BoxColliderComponent",
    "CircleColliderComponent",
    "ColliderSystem",
    "GameObject",
    "GameObjectFactory",
    "Renderer",
    "DataLoader",
    "ImageLoader",
    "SoundLoader",
    "FontLoader",
    # Game
    "Game",
]
