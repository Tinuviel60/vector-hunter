from typing import Optional

from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.rotation import Rotation


class Transform:
    """
    Représente la transformation spatiale d'un objet dans son espace local.

    Un Transform définit la position et l'orientation d'un objet.
    Il ne gère ni l'échelle, ni la hiérarchie parent/enfant, ni
    les systèmes de rendu ou de physique.

    Cette classe sert de source de vérité spatiale pour les systèmes
    (collisions, rendu, physique).

    Notes
    -----
    Structure fixe : __slots__ est utilisé pour limiter la mémoire
    et éviter les attributs dynamiques.

    Attributes
    ----------
    position : Vector2D
        Position de l'objet dans la scène.
    rotation : Rotation
        Rotation de l'objet en radians.
    """

    __slots__ = ("position", "rotation")

    def __init__(self, position: Optional[Vector2D] = None, rotation: float = 0.0):
        """
        Initialise un Transform.

        Parameters
        ----------
        position : Vector2D
            Position initiale dans la scène. Si None, la position
            est initialisée à (0, 0).
        rotation : float
            Orientation en radians. 0 correspond à aucune rotation.
        """
        self.position: Vector2D = position if position is not None else Vector2D()
        self.rotation: Rotation = Rotation(rotation)

    def translate(self, position: Vector2D) -> None:
        """
        Déplace le Transform dans l'espace.

        Cette méthode modifie directement la position.

        Parameters
        ----------
        position : Vector2D
            Nouvelle position.
        """
        self.position = position

    def move(self, direction: Vector2D) -> None:
        """
        Déplace le Transform selon un vecteur directionnel.

        Parameters
        ----------
        direction : Vector2D
            Vecteur représentant le déplacement à appliquer.
        """
        self.position += direction

    def rotate(self, delta: float) -> None:
        """
        Applique une rotation relative au Transform.

        Parameters
        ----------
        delta : float
            Angle en radians à ajouter à la rotation actuelle.
        """
        rotation_delta = Rotation(delta)
        self.rotation = self.rotation.compose(rotation_delta)

    def set_rotation(self, rotation: float) -> None:
        """
        Définit explicitement l'orientation du Transform.

        Parameters
        ----------
        rotation : float
            Angle en radians.
        """
        self.rotation = Rotation(rotation)

    def forward(self) -> Vector2D:
        """
        Retourne le vecteur directionnel correspondant à l'orientation
        du Transform.

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant dans la direction de la rotation.
        """

        return self.rotation.apply(Vector2D.top())

    def right(self) -> Vector2D:
        """
        Retourne le vecteur directionnel perpendiculaire à l'orientation
        du Transform (vers la droite).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers la droite par rapport à la rotation.
        """

        return self.rotation.apply(Vector2D.right())

    def behind(self) -> Vector2D:
        """
        Retourne le vecteur directionnel opposé à l'orientation
        du Transform (vers l'arrière).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers l'arrière par rapport à la rotation.
        """

        return self.rotation.apply(Vector2D.bottom())

    def left(self) -> Vector2D:
        """
        Retourne le vecteur directionnel perpendiculaire à l'orientation
        du Transform (vers la gauche).

        Returns
        -------
        Vector2D
            Vecteur unitaire pointant vers la gauche par rapport à la rotation.
        """

        return self.rotation.apply(Vector2D.left())
