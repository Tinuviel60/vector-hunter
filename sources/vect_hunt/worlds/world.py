from typing import List
from vect_hunt.objects import GameObject


class World:
    """
    Répresente le monde du jeu, contenant les cibles et le joueur.
    """

    def __init__(self):
        """
        Initialise un monde de jeu vide.
        """

        # TODO : targets and player management to remove when GameObject management is fully in place ?
        self.targets: dict[str, GameObject] = {}  # TODO Define a proper target class
        self.player = object()  # TODO Define a proper player class

        self.gameObjects: dict[str, GameObject] = {}

    def add_game_object(self, game_object: GameObject) -> None:
        """
        Ajoute un GameObject au monde.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à ajouter.
        """
        self.gameObjects[game_object.name] = game_object

    def remove_game_object(self, game_object: GameObject) -> None:
        """
        Retire un GameObject du monde.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à retirer.
        """
        if game_object.name in self.gameObjects:
            del self.gameObjects[game_object.name]

    def add_target(self, target: GameObject) -> None:
        """
        Ajoute une cible au monde.

        Parameters
        ----------
        target : GameObject
            La cible à ajouter au monde.
        """
        self.targets[target.name] = target

    def remove_target(self, target: GameObject) -> None:
        """
        Retire une cible du monde.

        Parameters
        ----------
        target : GameObject
            La cible à retirer du monde.
        """
        if target.name in self.targets:
            del self.targets[target.name]

    def validate_name(self, name: str) -> str:
        """
        Valide et ajuste le nom d'un GameObject pour éviter les conflits.

        Parameters
        ----------
        name : str
            Le nom proposé pour le GameObject.

        Returns
        -------
        str
            Un nom unique pour le GameObject.
        """

        original_name = name
        id = 1
        while name in self.gameObjects:
            name = f"{original_name}_{id}"
            id += 1
        return name
