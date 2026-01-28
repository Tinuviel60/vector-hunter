import math

from vect_hunt.engine.core.math.vector import Vector2D


class Rotation:
    """
    Représente une rotation 2D sous forme de matrice.

    La rotation est initialisée à partir d'un angle en radians,
    mais est ensuite stockée sous forme matricielle afin d'éviter
    les recalculs trigonométriques lors des opérations répétées.

    La matrice utilisée est de la forme :

        [ cos(a)  -sin(a) ]
        [ sin(a)   cos(a) ]

    Notes
    -----
    Structure fixe : __slots__ limite les attributs.

    Attributes
    ----------
    angle : float
        Angle de rotation en radians.
    """

    __slots__ = ("m00", "m01", "m10", "m11", "_angle")

    def __init__(self, angle: float = 0.0):
        """
        Initialise une rotation à partir d'un angle en radians.

        Parameters
        ----------
        angle : float
            Angle de rotation en radians.
            Une rotation positive correspond à une rotation anti-horaire.
        """
        self._angle = angle
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

    def apply_inverse(self, vector: Vector2D) -> Vector2D:
        """
        Applique la rotation inverse à un vecteur 2D.

        Parameters
        ----------
        vector : Vector2D
            Le vecteur à faire tourner inversement.

        Returns
        -------
        Vector2D
            Le vecteur résultant après application de la rotation inverse.
        """
        return Vector2D(
            vector.x * self.m00 + vector.y * self.m10,
            vector.x * self.m01 + vector.y * self.m11,
        )

    def apply_xy(self, x: float, y: float) -> tuple[float, float]:
        """
        Applique la rotation à des composantes x/y sans créer de Vector2D intermédiaire.

        Parameters
        ----------
        x : float
            Composante x.
        y : float
            Composante y.

        Returns
        -------
        tuple[float, float]
            Les composantes (x', y') après rotation.
        """
        return (
            x * self.m00 + y * self.m01,
            x * self.m10 + y * self.m11,
        )

    def apply_inverse_xy(self, x: float, y: float) -> tuple[float, float]:
        """
        Applique la rotation inverse à des composantes x/y sans créer de
        Vector2D intermédiaire.

        Parameters
        ----------
        x : float
            Composante x.
        y : float
            Composante y.

        Returns
        -------
        tuple[float, float]
            Les composantes (x', y') après rotation inverse.
        """
        return (
            x * self.m00 + y * self.m10,
            x * self.m01 + y * self.m11,
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
        inv._angle = -self._angle

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
        RotationA
            La rotation résultante de la composition.
        """
        result = Rotation.__new__(Rotation)

        result.m00 = self.m00 * other.m00 + self.m01 * other.m10
        result.m01 = self.m00 * other.m01 + self.m01 * other.m11
        result.m10 = self.m10 * other.m00 + self.m11 * other.m10
        result.m11 = self.m10 * other.m01 + self.m11 * other.m11

        # Recalcul exact de l’angle depuis la matrice
        result._angle = math.atan2(result.m10, result.m00)

        return result

    @property
    def angle(self) -> float:
        """
        Retourne l'angle équivalent de la rotation.

        Returns
        -------
        float
            Angle de rotation en radians.
        """
        return self._angle

    @property
    def angle_degrees(self) -> float:
        """
        Retourne l'angle équivalent de la rotation.

        Returns
        -------
        float
            Angle de rotation en degrés.
        """
        return math.degrees(self._angle)

    def reflect(self, normal: Vector2D) -> "Rotation":
        """
        Retourne la rotation réfléchie par rapport à une normale de surface.

        Utilise la formule de réflexion :
            reflected = incident - 2 * (incident · normal) * normal
        Cette méthode calcule la nouvelle direction après un rebond sur une surface
        ayant la normale donnée.

        Parameters
        ----------
        normal : Vector2D
            Vecteur normal normalisé de la surface.

        Returns
        -------
        Rotation
            Rotation correspondant à la direction réfléchie.
        """
        # Obtenir le vecteur de direction actuel
        direction = self.apply(Vector2D.top())  # Direction forward

        # Calculer le produit scalaire direction · normal
        dot = direction.dot(normal)

        # Appliquer la formule de réflexion :
        # reflected = incident - 2 * (incident · normal) * normal
        reflected_x = direction.x - 2 * dot * normal.x
        reflected_y = direction.y - 2 * dot * normal.y
        reflected = Vector2D(reflected_x, reflected_y)

        # Calculer l'angle de la nouvelle direction
        # Convertit l'angle "direction" (repère X) vers un angle de rotation
        # dont l'axe forward est Vector2D.top() (repère Y-up).
        new_angle = math.atan2(reflected.y, reflected.x) - math.pi / 2

        reflected_rotation = Rotation(new_angle)
        return reflected_rotation
