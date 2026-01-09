import math

from vect_hunt.core import Vector2D


class Rotation:
    """
    Représente une rotation 2D sous forme de matrice.

    La rotation est initialisée à partir d'un angle en radians,
    mais est ensuite stockée sous forme matricielle afin d'éviter
    les recalculs trigonométriques lors des opérations répétées.

    La matrice utilisée est de la forme :

        [ cos(a)  -sin(a) ]
        [ sin(a)   cos(a) ]
    """

    def __init__(self, angle: float = 0.0):
        """
        Initialise une rotation à partir d'un angle en radians.

        Parameters
        ----------
        angle : float
            Angle de rotation en radians.
            Une rotation positive correspond à une rotation anti-horaire.
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Stockage direct de la matrice 2x2
        self.m00 = cos_a
        self.m01 = -sin_a
        self.m10 = sin_a
        self.m11 = cos_a

    def apply(self, vector: Vector2D) -> Vector2D:
        """
        Applique la rotation à un vecteur 2D.

        Parameters
        ----------
        vector : Vector2D
            Le vecteur à faire tourner.

        Returns
        -------
        Vector2D
            Le vecteur résultant après application de la rotation.
        """
        return Vector2D(
            vector.x * self.m00 + vector.y * self.m01,
            vector.x * self.m10 + vector.y * self.m11,
        )

    def inverse(self) -> "Rotation":
        """
        Retourne la rotation inverse.

        Pour une matrice de rotation orthonormée, l'inverse est égal
        à la transposée de la matrice.

        Returns
        -------
        Rotation
            Une nouvelle rotation correspondant à l'inverse de celle-ci.
        """
        inv = Rotation.__new__(Rotation)

        # Transposée de la matrice
        inv.m00 = self.m00
        inv.m01 = self.m10
        inv.m10 = self.m01
        inv.m11 = self.m11

        return inv

    def compose(self, other: "Rotation") -> "Rotation":
        """
        Additionne/ompose cette rotation avec une autre rotation.

        La rotation résultante correspond à l'application de `other`
        suivie de l'application de cette rotation.

        Parameters
        ----------
        other : Rotation
            La rotation à composer avec celle-ci.

        Returns
        -------
        Rotation
            La rotation résultante de la composition.
        """
        result = Rotation.__new__(Rotation)

        result.m00 = self.m00 * other.m00 + self.m01 * other.m10
        result.m01 = self.m00 * other.m01 + self.m01 * other.m11
        result.m10 = self.m10 * other.m00 + self.m11 * other.m10
        result.m11 = self.m10 * other.m01 + self.m11 * other.m11

        return result

    def to_angle(self) -> float:
        """
        Retourne l'angle équivalent de la rotation.

        Attention : cette opération est principalement destinée
        au debug ou à l'affichage. La valeur retournée dépend
        de la précision flottante.

        Returns
        -------
        float
            Angle de rotation en radians.
        """
        return math.atan2(self.m10, self.m00)
