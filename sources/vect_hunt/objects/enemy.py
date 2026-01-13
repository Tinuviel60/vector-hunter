from typing import Optional
from vect_hunt.objects.game_object import GameObject
from vect_hunt.core import Transform, Vector2D


class Enemy(GameObject):
    """
    Classe représentant un ennemi avec mouvement automatique.

    Les ennemis se déplacent automatiquement selon leur vitesse configurée.
    """

    def __init__(
        self,
        name: str = "Enemy",
        transform: Optional[Transform] = None,
        speed: float = 150.0,
    ):
        """
        Initialise un ennemi.

        Parameters
        ----------
        name : str, optional
            Nom de l'ennemi. Par défaut "Enemy".
        transform : Transform, optional
            Transformation initiale de l'ennemi.
        speed : float, optional
            Vitesse de déplacement horizontal en pixels/seconde.
            Valeur négative pour aller vers la gauche. Par défaut -150.0.
        """
        super().__init__(name=name, transform=transform)
        self.speed = speed

    def update(self, delta_time: float) -> None:
        """
        Met à jour l'ennemi (déplacement automatique).

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        # Déplacement horizontal automatique
        self.make_decision(delta_time)

    def make_decision(self, delta_time: float) -> None:
        """
        Permet à l'ennemi de prendre des décisions (IA basique).

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        self.move_in_limite(Vector2D(100, 100), Vector2D(700, 500), delta_time)

    def move_in_limite(
        self, top_left_pos: Vector2D, bottom_right_pos: Vector2D, delta_time: float
    ) -> None:
        """
        Déplace l'ennemi et rebondit sur les limites en conservant le mouvement restant.

        Parameters
        ----------
        top_left_pos : Vector2D
            Position en haut à gauche définissant les limites.
        bottom_right_pos : Vector2D
            Position en bas à droite définissant les limites.
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        direction = self.transform.forward()
        displacement = direction * (self.speed * delta_time)
        target_position = self.transform.position + displacement

        # Vérifier et corriger les dépassements de limites
        collision_normal = None

        if target_position.x < top_left_pos.x and direction.x < 0:
            target_position = Vector2D(top_left_pos.x, target_position.y)
            collision_normal = Vector2D(1, 0)  # Normal pointant vers la droite
        elif target_position.x > bottom_right_pos.x and direction.x > 0:
            target_position = Vector2D(bottom_right_pos.x, target_position.y)
            collision_normal = Vector2D(-1, 0)  # Normal pointant vers la gauche

        if target_position.y < top_left_pos.y and direction.y < 0:
            target_position = Vector2D(target_position.x, top_left_pos.y)
            collision_normal = Vector2D(0, 1)  # Normal pointant vers le bas
        elif target_position.y > bottom_right_pos.y and direction.y > 0:
            target_position = Vector2D(target_position.x, bottom_right_pos.y)
            collision_normal = Vector2D(0, -1)  # Normal pointant vers le haut

        # Appliquer le déplacement
        self.transform.position = target_position

        # Si collision, appliquer la réflexion
        if collision_normal is not None:
            self.transform.rotation = self.transform.rotation.reflect(collision_normal)
