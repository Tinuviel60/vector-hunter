"""
Composant d'attributs de base pour un GameObject.
"""

from typing import Any

from vect_hunt.engine.components.component import Component


class AttributesComponent(Component):
    """
    Composant stockant des attributs simples (ex: vitesse).

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    speed : float
        Vitesse de déplacement en pixels/seconde.
    """

    component_name = "attributes"

    def __init__(self, speed: float = 300.0) -> None:
        """
        Initialise les attributs de base.

        Parameters
        ----------
        speed : float, optional
            Vitesse de déplacement en pixels/seconde.
        """
        super().__init__()
        self.speed = speed

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "AttributesComponent":
        """
        Crée un AttributesComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        context : dict[str, Any]
            Contexte additionnel pour la création (non utilisé ici).

        Returns
        -------
        AttributesComponent
            Instance du composant créé.
        """
        speed = data.get("speed", 300.0)
        return cls(speed=speed)
    
    def update(self, delta_time: float) -> None:
        """
        Mise à jour du composant (non utilisé ici).

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass