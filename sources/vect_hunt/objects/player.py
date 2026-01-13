from typing import Optional
from vect_hunt.objects.game_object import GameObject
from vect_hunt.core import Transform, Vector2D
from vect_hunt.systems import InputSystem


class Player(GameObject):
    """
    Classe représentant le joueur contrôlé par l'utilisateur.

    Le joueur réagit aux inputs du système InputSystem pour se déplacer.
    """

    def __init__(
        self,
        name: str = "Player",
        transform: Optional[Transform] = None,
        speed: float = 300.0,
    ):
        """
        Initialise le joueur.

        Parameters
        ----------
        name : str, optional
            Nom du joueur. Par défaut "Player".
        transform : Transform, optional
            Transformation initiale du joueur.
        speed : float, optional
            Vitesse de déplacement du joueur en pixels/seconde. Par défaut 300.0.
        """
        super().__init__(name=name, transform=transform)
        self.speed = speed

    def update(self, input_system: InputSystem, delta_time: float) -> None:
        """
        Met à jour le joueur en fonction des inputs.

        Parameters
        ----------
        input_system : InputSystem
            Le système d'inputs à consulter.
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        # Récupérer le vecteur de déplacement depuis l'input system
        move_vector = input_system.get_vector("move")
        self.deplacement(move_vector, delta_time)

    def deplacement(self, move_vector: Vector2D, delta_time: float) -> None:
        """
        Déplace le joueur en fonction du vecteur de mouvement des inputs.

        Parameters
        ----------
        move_vector : Vector2D
            Vecteur de déplacement normalisé (direction).
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        # Appliquer le déplacement avec la vitesse
        if move_vector.magnitude() > 0.0:
            displacement = move_vector * self.speed * delta_time
            self.move(displacement)
