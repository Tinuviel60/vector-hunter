from typing import List


class World:
    """
    Répresente le monde du jeu, contenant les cibles et le joueur.
    """

    def __init__(self):
        """
        Initialise un monde de jeu vide.
        """
        self.targets: List[object] = []  # TODO Define a proper target class
        self.player = object()  # TODO Define a proper player class

    def add_target(self, target: object) -> None:
        """
        Ajoute une cible au monde.

        Parameters
        ----------
        target : object
            La cible à ajouter au monde.
        """
        self.targets.append(target)

    def remove_target(self, target: object) -> None:
        """
        Retire une cible du monde.

        Parameters
        ----------
        target : object
            La cible à retirer du monde.
        """
        if target in self.targets:
            self.targets.remove(target)
