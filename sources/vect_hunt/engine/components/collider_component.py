from typing import List, TYPE_CHECKING
from vect_hunt.engine.components.component import Component
from vect_hunt.engine.physics.collider import Collider

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject


class ColliderComponent(Component):
    """
    Composant gérant les colliders d'un GameObject.

    Un ColliderComponent peut contenir plusieurs Collider (cercles, rectangles, etc.)
    pour permettre des formes de collision complexes.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    colliders : List[Collider]
        Liste des colliders attachés.
    nb_collision : int
        Compteur de collisions pour le debug rendering.
    """

    def __init__(self):
        """
        Initialise le composant de collision.
        """
        super().__init__()
        self.colliders: List[Collider] = []
        self.nb_collision = 0  # Compteur pour le debug rendering

    def add_collider(self, collider: Collider) -> Collider:
        """
        Ajoute un collider à ce composant.

        Le collider est lié au GameObject du composant.

        Parameters
        ----------
        collider : Collider
            Le collider à ajouter.

        Returns
        -------
        Collider
            Le collider ajouté, permettant un chaînage de méthodes.
        """
        self.colliders.append(collider)
        # Le collider a besoin de connaître son GameObject pour les callbacks
        if self.game_object:
            collider.parent = self.game_object
        return collider

    def remove_collider(self, collider: Collider) -> None:
        """
        Retire un collider de ce composant.

        Parameters
        ----------
        collider : Collider
            Le collider à retirer.
        """
        if collider in self.colliders:
            self.colliders.remove(collider)

    def on_attach(self, game_object: "GameObject") -> None:
        """
        Appelé lorsque le composant est attaché à un GameObject.

        Met à jour la référence game_object dans tous les colliders existants.

        Parameters
        ----------
        game_object : GameObject
            Le GameObject auquel ce composant est attaché.
        """
        super().on_attach(game_object)
        # Mettre à jour tous les colliders avec le nouveau game_object
        for collider in self.colliders:
            collider.parent = game_object

    def on_detach(self) -> None:
        """
        Appelé lors du détachement du composant.

        Nettoie les références dans tous les colliders.
        """
        # Nettoyer lors du détachement
        # Note: On ne met pas parent à None pour garder la référence
        super().on_detach()

    def update(self, delta_time: float) -> None:
        """
        Les colliders n'ont pas de logique dans update.

        La détection de collision est gérée par le ColliderSystem.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass
