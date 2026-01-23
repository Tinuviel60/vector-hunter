"""
Composant de gestion des inputs pour les entités contrôlées par le joueur.
"""

from typing import TYPE_CHECKING, Any

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent

if TYPE_CHECKING:
    from vect_hunt.engine.input.input_system import InputSystem


class InputComponent(Component):
    """
    Composant permettant de contrôler un GameObject via les inputs clavier/souris.

    Récupère les inputs du InputSystem et génère des intentions de mouvement
    qui seront transmises au PhysicBodyComponent.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    input_system : InputSystem
        Référence au système d'inputs.
    """

    component_name = "input"

    def __init__(self, input_system: "InputSystem"):
        """
        Initialise le composant d'input.

        Parameters
        ----------
        input_system : InputSystem
            Référence au système d'inputs du jeu.
        """
        super().__init__()
        self.input_system = input_system

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "InputComponent":
        """
        Crée un InputComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration (non utilisées ici).
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        InputComponent
            Instance du composant créé.
        """
        input_system = context.get("input_system")
        if input_system is None:
            raise ValueError("InputSystem requis pour creer un composant 'input'.")
        return cls(input_system)

    def update(self, delta_time: float) -> None:
        """
        Met à jour le composant en récupérant les inputs et appliquant le mouvement.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        move_vector = self.input_system.get_vector("move")

        # Récupérer le PhysicBodyComponent
        physic_body = self.parent.get_component(PhysicBodyComponent)
        if not physic_body:
            return

        # Versions plateforme
        # if move_vector.x != 0:
        #     # Calculer l'accélération à appliquer pour atteindre la vitesse désirée
        #     desired_velocity_x = move_vector.x * physic_body.speed
        #     delta_v_x = desired_velocity_x - physic_body.velocity.x
        #     acceleration = Vector2D(delta_v_x, 0)

        #     physic_body.add_acceleration(acceleration)

        # if move_vector.y != 0:
        #     # Calculer l'accélération verticale (saut)
        #     desired_velocity_y = move_vector.y * physic_body.speed
        #     delta_v_y = desired_velocity_y - physic_body.velocity.y
        #     acceleration_y = Vector2D(0, delta_v_y)

        #     physic_body.add_acceleration(acceleration_y)

        # Versions vu du dessus
        desired_velocity = move_vector * physic_body.speed
        acceleration = desired_velocity - physic_body.velocity
        physic_body.add_acceleration(acceleration)

        # physic_body.set_velocity(desired_velocity)
