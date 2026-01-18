"""
Composant de gestion des inputs pour les entités contrôlées par le joueur.
"""

from typing import Any, TYPE_CHECKING

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.components.component import Component
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent

if TYPE_CHECKING:
    from vect_hunt.engine.input import InputSystem


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
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "InputComponent":
        """
        Crée un InputComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration (non utilisées ici).
        game_object : GameObject
            Le GameObject auquel ce composant sera attaché.
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
        assert (
            self.game_object is not None
        ), "InputComponent doit être attaché à un GameObject"

        move_vector = self.input_system.get_vector("move")

        # Récupérer le PhysicBodyComponent
        physic_body = self.game_object.get_component(PhysicBodyComponent)
        if not physic_body:
            return

        if move_vector.magnitude() > 0.0:
            # Calculer la vélocité à appliquer en utilisant la vitesse du corps physique
            velocity = move_vector * physic_body.speed
            physic_body.set_velocity(velocity)
        else:
            # Arrêter le mouvement si aucun input
            physic_body.set_velocity(Vector2D(0, 0))
