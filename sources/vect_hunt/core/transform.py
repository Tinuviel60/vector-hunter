from .position import Position2D
from .vector import Vector2D
import math


class Transform:
    """
    Représente la transformation spatiale d'un objet dans son espace local.

    Un Transform définit la position et l'orientation d'un objet.
    Il ne gère ni l'échelle, ni la hiérarchie parent/enfant, ni
    les systèmes de rendu ou de physique.

    Cette classe sert de source de vérité spatiale pour les systèmes
    (collisions, rendu, physique).
    """

    def __init__(self, position: Position2D = Position2D(0, 0), rotation: float = 0):
        """
        Initialise un Transform.

        Parameters
        ----------
        position : Position2D
            Position initiale dans le monde. Si None, la position
            est initialisée à (0, 0).
        rotation : float
            Orientation en radians. 0 correspond à aucune rotation.
        """
        self.position = position
        self.rotation = rotation

    def translate(self, dx: float, dy: float) -> None:
        """
        Déplace le Transform dans l'espace.

        Cette méthode modifie directement la position.

        Parameters
        ----------
        dx : float
            Déplacement sur l'axe X.
        dy : float
            Déplacement sur l'axe Y.
        """
        self.position.x += dx
        self.position.y += dy

    def move(self, direction: Vector2D) -> None:
        """
        Déplace le Transform selon un vecteur directionnel.

        Parameters
        ----------
        direction : Vector2D
            Vecteur représentant le déplacement à appliquer.
        """
        self.position.x += direction.x
        self.position.y += direction.y

    def rotate(self, delta: float) -> None:
        """
        Applique une rotation relative au Transform.

        Parameters
        ----------
        delta : float
            Angle en radians à ajouter à la rotation actuelle.
        """
        self.rotation += delta

    def set_rotation(self, rotation: float) -> None:
        """
        Définit explicitement l'orientation du Transform.

        Parameters
        ----------
        rotation : float
            Angle en radians.
        """
        self.rotation = rotation

    def forward(self) -> Vector2D:
        """
        Retourne le vecteur directionnel correspondant à l'orientation
        du Transform.

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant dans la direction de la rotation.
        """

        return Vector2D.from_direction(self.rotation)

    def right(self) -> Vector2D:
        """
        Retourne le vecteur directionnel perpendiculaire à l'orientation
        du Transform (vers la droite).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers la droite par rapport à la rotation.
        """

        return Vector2D.from_direction(self.rotation + math.pi / 2)

    def behind(self) -> Vector2D:
        """
        Retourne le vecteur directionnel opposé à l'orientation
        du Transform (vers l'arrière).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers l'arrière par rapport à la rotation.
        """

        return Vector2D.from_direction(self.rotation + math.pi)

    def left(self) -> Vector2D:
        """
        Retourne le vecteur directionnel perpendiculaire à l'orientation
        du Transform (vers la gauche).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers la gauche par rapport à la rotation.
        """

        return Vector2D.from_direction(self.rotation - math.pi / 2)
