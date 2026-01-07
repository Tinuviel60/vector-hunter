from typing import List, Optional
from vect_hunt.core.transform import Transform
from vect_hunt.core.collider import Collider


class GameObject:
    """
    Représente un objet du jeu, avec sa transformation spatiale et ses colliders.

    Un GameObject est une entité logique qui peut être :
    - déplacée dans l'espace via son Transform,
    - équipée de colliders pour la détection de collisions,
    - enrichie plus tard avec des composants (physique, rendu, scripts...).

    Attributes
    ----------
    name : str
        Nom de l'objet pour identification.
    transform : Transform
        Transformation spatiale de l'objet.
    colliders : List[Collider]
        Liste des colliders attachés à l'objet. Peut être vide.
    active : bool
        Indique si l'objet est actif dans le monde.
    """

    def __init__(self, name: str, transform: Transform = Transform()):
        """
        Initialise un GameObject.

        Parameters
        ----------
        name : str
            Nom de l'objet.
        transform : Transform, optional
            Transformation initiale de l'objet. Par défaut, un Transform
            avec position (0,0) et rotation 0.
        """
        self.name = name
        self.transform = transform if transform is not None else Transform()
        self.colliders: List[Collider] = []
        self.active = True

    def add_collider(self, collider: Collider) -> None:
        """
        Attache un collider à l'objet.

        Parameters
        ----------
        collider : Collider
            Le collider à ajouter.
        """
        self.colliders.append(collider)

    def remove_collider(self, collider: Collider) -> None:
        """
        Retire un collider de l'objet.

        Parameters
        ----------
        collider : Collider
            Le collider à retirer.
        """
        if collider in self.colliders:
            self.colliders.remove(collider)

    def move(self, dx: float, dy: float) -> None:
        """
        Déplace le GameObject dans l'espace en modifiant son Transform.

        Parameters
        ----------
        dx : float
            Déplacement sur l'axe X.
        dy : float
            Déplacement sur l'axe Y.
        """
        self.transform.translate(dx, dy)

    def rotate(self, delta: float) -> None:
        """
        Applique une rotation relative au GameObject.

        Parameters
        ----------
        delta : float
            Angle en radians à ajouter à la rotation actuelle.
        """
        self.transform.rotate(delta)

    def set_position(self, x: float, y: float) -> None:
        """
        Définit explicitement la position du GameObject.

        Parameters
        ----------
        x : float
            Position X.
        y : float
            Position Y.
        """
        dx = x - self.transform.position.x
        dy = y - self.transform.position.y
        self.move(dx, dy)
