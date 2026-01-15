"""
Composant de corps physique pour gérer les déplacements et forces.
"""

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.math import Vector2D


class PhysicBodyComponent(Component):
    """
    Composant gérant les aspects physiques d'un GameObject.

    Reçoit des intentions de mouvement (vélocité, forces) et applique
    les déplacements sur le Transform du GameObject.
    Le système de collision se charge des limitations.
    """

    def __init__(self, speed: float = 300.0, is_kinematic: bool = False):
        """
        Initialise le composant de corps physique.

        Parameters
        ----------
        speed : float, optional
            Vitesse de déplacement en pixels/seconde. Par défaut 300.0.
        is_kinematic : bool, optional
            Indique si le corps est cinématique (non affecté par la physique). Par défaut False.
        """
        super().__init__()
        self.speed = speed
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
        self.is_kinematic = is_kinematic

    def update(self, delta_time: float) -> None:
        """
        Met à jour la position du GameObject en fonction de la vélocité.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        assert (
            self.game_object is not None
        ), "PhysicBodyComponent doit être attaché à un GameObject"

        # Appliquer l'accélération à la vélocité
        self.velocity += self.acceleration * delta_time

        # Appliquer la vélocité au déplacement
        if self.velocity.magnitude() > 0:
            displacement = self.velocity * delta_time
            self.game_object.transform.move(displacement)

        # Réinitialiser l'accélération (forces ponctuelles)
        self.acceleration = Vector2D(0, 0)

    def set_velocity(self, velocity: Vector2D) -> None:
        """
        Définit la vélocité du corps physique.

        Parameters
        ----------
        velocity : Vector2D
            Vecteur de vélocité en pixels/seconde.
        """
        self.velocity = velocity

    def add_force(self, force: Vector2D) -> None:
        """
        Ajoute une force (accélération) au corps physique.

        Parameters
        ----------
        force : Vector2D
            Force à ajouter (accélération en pixels/seconde²).
        """
        self.acceleration += force

    def stop(self) -> None:
        """
        Arrête complètement le mouvement du corps physique.
        """
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
