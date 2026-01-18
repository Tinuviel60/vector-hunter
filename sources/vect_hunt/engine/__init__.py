"""
Moteur de jeu Vector Hunt.

Moteur 2D réutilisable pour créer des jeux.
Fournit les systèmes de base : rendu, physique, input, ressources...
"""

# Core
from .core import (
    Vector2D,
    Geometry,
    Transform,
    Rotation,
    Position2D,
    Tag,
    TagSystem,
    hex_to_rgb,
)

# Physics
from .physics import (
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderComponent,
    ColliderSystem,
)

# Objects
from .objects import GameObject, GameObjectFactory

# Input
from .input import InputAction, ActionType, ActionState, InputSystem, InputTracker

# Rendering
from .rendering import Renderer, RenderComponent
from vect_hunt.engine.components.rendering import BasicShapeComponent, SpriteComponent
from .rendering.font import FontStyle, FontSystem

# Resources
from .resources import DataLoader, ImageLoader, SoundLoader, FontLoader, Paths

# Worlds
from .worlds import World

__all__ = [
    # Core
    "Vector2D",
    "Geometry",
    "Transform",
    "Rotation",
    "Position2D",
    "Tag",
    "TagSystem",
    "hex_to_rgb",
    # Physics
    "ColliderComponent",
    "BoxColliderComponent",
    "CircleColliderComponent",
    "ColliderSystem",
    # Objects
    "GameObject",
    "GameObjectFactory",
    # Input
    "InputAction",
    "ActionType",
    "ActionState",
    "InputSystem",
    "InputTracker",
    # Rendering
    "Renderer",
    "RenderComponent",
    "BasicShapeComponent",
    "SpriteComponent",
    "FontStyle",
    "FontSystem",
    # Resources
    "DataLoader",
    "ImageLoader",
    "SoundLoader",
    "FontLoader",
    "Paths",
    # Worlds
    "World",
]
