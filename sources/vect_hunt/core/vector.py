import math


class Vector2D:
    """
    Répresente un vecteur 2D.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0):
        """
        Initialise un vecteur 2D.

        Parameters
        ----------
        x : float
            La composante x du vecteur. Par défaut à 0.0.
        y : float
            La composante y du vecteur. Par défaut à 0.0.
        """
        self._x = x
        self._y = y

    def orientation(self) -> float:
        """
        Calcule l'orientation (angle) du vecteur en radians.

        Returns
        -------
        float
            L'angle du vecteur en radians.
        """
        return math.atan2(self._y, self._x)

    def magnitude(self) -> float:
        """
        Calcule la magnitude (longueur) du vecteur.

        Returns
        -------
        float
            La magnitude du vecteur.
        """
        return math.hypot(self._x, self._y)

    def normalized(self) -> "Vector2D":
        """
        Renvoie le vecteur normalisé (le rend de longueur 1).

        Returns
        -------
        Vector2D
            Le vecteur normalisé.
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self._x / mag, self._y / mag)

    def normalize(self) -> None:
        """
        Normalise le vecteur (le rend de longueur 1).
        """
        mag = self.magnitude()
        if mag == 0:
            self._x = 0.0
            self._y = 0.0
            return
        self._x /= mag
        self._y /= mag

    def normal(self) -> "Vector2D":
        """
        Calcule le vecteur normal (perpendiculaire) à ce vecteur.

        Returns
        -------
        Vector2D
            Le vecteur normal.
        """
        return Vector2D(-self._y, self._x)

    def dot(self, other: "Vector2D") -> float:
        """
        Calcule le produit scalaire entre ce vecteur et un autre.

        Parameters
        ----------
        other : Vector2D
            Le vecteur avec lequel calculer le produit scalaire.

        Returns
        -------
        float
            Le produit scalaire des deux vecteurs.
        """
        return self._x * other._x + self._y * other._y

    @property
    def x(self) -> float:
        """
        Obtient la composante x du vecteur.

        Returns
        -------
        float
            La composante x du vecteur.
        """
        return self._x

    @x.setter
    def x(self, x: float) -> None:
        """
        Définit la composante x du vecteur.

        Parameters
        ----------
        x : float
            La nouvelle valeur de la composante x.
        """
        self._x = x

    @property
    def y(self) -> float:
        """
        Obtient la composante y du vecteur.

        Returns
        -------
        float
            La composante y du vecteur.
        """
        return self._y

    @y.setter
    def y(self, y: float) -> None:
        """
        Définit la composante y du vecteur.

        Parameters
        ----------
        y : float
            La nouvelle valeur de la composante y.
        """
        self._y = y

    def set_vector(self, x: float, y: float) -> None:
        """
        Définit les composantes x et y du vecteur.

        Parameters
        ----------
        x : float
            La nouvelle valeur de la composante x.
        y : float
            La nouvelle valeur de la composante y.
        """
        self._x = x
        self._y = y

    def get_vector(self) -> tuple[float, float]:
        """
        Obtient les composantes x et y du vecteur.

        Returns
        -------
        tuple[float, float]
            Un tuple contenant les composantes (x, y) du vecteur.
        """
        return (self._x, self._y)

    def __add__(self, other: "Vector2D") -> "Vector2D":
        """
        Additionne deux vecteurs.

        Parameters
        ----------
        other : Vector2D
            Le vecteur à additionner.

        Returns
        -------
        Vector2D
            Le vecteur résultant de l'addition.
        """
        return Vector2D(self._x + other._x, self._y + other._y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        """
        Soustrait deux vecteurs.

        Parameters
        ----------
        other : Vector2D
            Le vecteur à soustraire.

        Returns
        -------
        Vector2D
            Le vecteur résultant de la soustraction.
        """
        return Vector2D(self._x - other._x, self._y - other._y)

    def __mul__(self, scalar: float) -> "Vector2D":
        """
        Multiplie le vecteur par un scalaire.

        Parameters
        ----------
        scalar : float
            Le scalaire par lequel multiplier le vecteur.

        Returns
        -------
        Vector2D
            Le vecteur résultant de la multiplication.
        """
        return Vector2D(self._x * scalar, self._y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2D":
        """
        Multiplie le vecteur par un scalaire (opération à droite).

        Parameters
        ----------
        scalar : float
            Le scalaire par lequel multiplier le vecteur.

        Returns
        -------
        Vector2D
            Le vecteur résultant de la multiplication.
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector2D":
        """
        Divise le vecteur par un scalaire.

        Parameters
        ----------
        scalar : float
            Le scalaire par lequel diviser le vecteur.

        Returns
        -------
        Vector2D
            Le vecteur résultant de la division.
        """
        if scalar == 0:
            raise ValueError("Division par zéro dans la division de vecteurs.")
        return Vector2D(self._x / scalar, self._y / scalar)

    def __repr__(self) -> str:
        """
        Représentation en chaîne du vecteur.

        Returns
        -------
        str
            La représentation en chaîne du vecteur.
        """
        return f"Vector2D(x={self._x}, y={self._y})"

    def __eq__(self, other: "Vector2D") -> bool:
        """
        Vérifie l'égalité entre deux vecteurs.

        Parameters
        ----------
        other : object
            Le vecteur à comparer.

        Returns
        -------
        bool
            True si les vecteurs sont égaux, False sinon.
        """

        return math.isclose(self._x, other._x) and math.isclose(self._y, other._y)
