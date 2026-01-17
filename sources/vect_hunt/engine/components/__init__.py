"""
Module des composants du moteur de jeu.

Contient les classes abstraites et concrètes pour le système de composants.
"""

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.components.input_component import InputComponent
from vect_hunt.engine.components.ia_component import IaComponent

__all__ = [
    "Component",
    "RenderComponent",
    "PhysicBodyComponent",
    "InputComponent",
    "IaComponent",
]
