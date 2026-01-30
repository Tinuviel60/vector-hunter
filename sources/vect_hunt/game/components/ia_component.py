"""
Composant d'intelligence artificielle pour les ennemis.
"""

from typing import Any, TYPE_CHECKING, cast

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.math.vector import Vector2D

if TYPE_CHECKING:
    from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
    from vect_hunt.game.components.attributes_component import AttributesComponent


class IaComponent(Component):
    """
    Composant gérant l'intelligence artificielle d'un ennemi.

    Prend des décisions de mouvement et génère des intentions
    qui seront transmises au PhysicBodyComponent.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    top_left : Vector2D
        Limite supérieure gauche de la zone de mouvement.
    bottom_right : Vector2D
        Limite inférieure droite de la zone de mouvement.
    """

    component_name = "ia"

    def __init__(
        self,
        top_left: Vector2D = Vector2D(100, 100),
        bottom_right: Vector2D = Vector2D(700, 500),
    ):
        """
        Initialise le composant d'IA.

        Parameters
        ----------
        top_left : Vector2D, optional
            Limite supérieure gauche de la zone de mouvement.
        bottom_right : Vector2D, optional
            Limite inférieure droite de la zone de mouvement.
        """
        super().__init__()
        self.top_left = top_left
        self.bottom_right = bottom_right

    @classmethod
    def from_data(cls, data: dict[str, Any], context: dict[str, Any]) -> "IaComponent":
        """
        Crée un IaComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        InputComponent
            Instance du composant créé.
        """
        top_left = data.get("top_left", [100, 100])
        bottom_right = data.get("bottom_right", [700, 500])
        return cls(
            Vector2D(top_left[0], top_left[1]),
            Vector2D(bottom_right[0], bottom_right[1]),
        )

    def update(self, delta_time: float) -> None:
        """
        Met à jour l'IA et génère les intentions de mouvement.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        self.make_decision(delta_time)

    def make_decision(self, delta_time: float) -> None:
        """
        Prend des décisions de mouvement pour l'ennemi.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        self.move_in_limits(delta_time)

    def move_in_limits(self, delta_time: float) -> None:
        """
        Génère une intention de mouvement dans les limites définies.

        Simplifié : se déplace dans la direction actuelle et rebondit sur les bords.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        # TODO : Sortir les components requis dans l'init ou via système de dépendances
        # Récupérer le PhysicBodyComponent
        physic_body = cast("PhysicBodyComponent | None", self.parent.get_component("physic_body"))
        if not physic_body:
            return

        # Récupérer le PhysicBodyComponent
        attributes = cast("AttributesComponent | None", self.parent.get_component("attributes"))
        if not attributes:
            return

        # Récupérer la direction actuelle
        direction = self.parent.transform.forward()

        # Calculer la vélocité en utilisant la vitesse du corps physique
        velocity = direction * attributes.speed

        # Vérifier si on va sortir des limites
        future_position = self.parent.transform.position + velocity * delta_time

        collision_normal = None

        # Vérifier les limites et calculer la normale de collision
        min_x = min(self.top_left.x, self.bottom_right.x)
        max_x = max(self.top_left.x, self.bottom_right.x)
        min_y = min(self.top_left.y, self.bottom_right.y)
        max_y = max(self.top_left.y, self.bottom_right.y)

        if future_position.x < min_x and direction.x < 0:
            collision_normal = Vector2D(1, 0)  # Normal pointant vers la droite
        elif future_position.x > max_x and direction.x > 0:
            collision_normal = Vector2D(-1, 0)  # Normal pointant vers la gauche

        if future_position.y < min_y and direction.y < 0:
            collision_normal = Vector2D(0, 1)  # Normal pointant vers le haut
        elif future_position.y > max_y and direction.y > 0:
            collision_normal = Vector2D(0, -1)  # Normal pointant vers le bas

        # Si collision détectée, inverser la rotation
        if collision_normal is not None:
            self.parent.transform.rotation = self.parent.transform.rotation.reflect(
                collision_normal
            )
            direction = self.parent.transform.forward()
            velocity = direction * attributes.speed

        desired_velocity = direction * attributes.speed
        acceleration = desired_velocity - physic_body.velocity
        physic_body.add_acceleration(acceleration)

        # Transmettre l'intention au PhysicBodyComponent
        # physic_body.set_velocity(velocity)
