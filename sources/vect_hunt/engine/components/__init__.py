"""
Module des composants du moteur de jeu.

Contient les classes abstraites et concrètes pour le système de composants.
"""

from .component import Component
from .render_component import RenderComponent
from .physic_body_component import PhysicBodyComponent

__all__ = [
    "Component",
    "RenderComponent",
    "PhysicBodyComponent",
]
