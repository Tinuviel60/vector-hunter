"""
Module des composants du moteur de jeu.

Contient les classes abstraites et concrètes pour le système de composants.
"""

from .component import Component
from .physic_body_component import PhysicBodyComponent
from .render_component import RenderComponent

__all__ = [
    "Component",
    "RenderComponent",
    "PhysicBodyComponent",
]
