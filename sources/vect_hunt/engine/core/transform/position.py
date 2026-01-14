import math
from vect_hunt.engine.core.math.vector import Vector2D


class Position2D:
    """
    Répresente une position 2D.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0):
        """
        Initialise une position 2D.

        Parameters
        ----------
        x : float
            La composante x de la position. Par défaut à 0.0.
        y : float
            La composante y de la position. Par défaut à 0.0.
        """
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        """
        Obtient la composante x de la position.

        Returns
        -------
        float
            La composante x de la position.
        """
        return self._x

    @x.setter
    def x(self, x: float) -> None:
        """
        Définit la composante x de la position.

        Parameters
        ----------
        x : float
            La nouvelle valeur de la composante x.
        """
        self._x = x

    @property
    def y(self) -> float:
        """
        Obtient la composante y de la position.

        Returns
        -------
        float
            La composante y de la position.
        """
        return self._y

    @y.setter
    def y(self, y: float) -> None:
        """
        Définit la composante y de la position.

        Parameters
        ----------
        y : float
            La nouvelle valeur de la composante y.
        """
        self._y = y

    def set_position(self, x: float, y: float) -> None:
        """
        Définit les composantes x et y de la position.

        Parameters
        ----------
        x : float
            La nouvelle valeur de la composante x.
        y : float
            La nouvelle valeur de la composante y.
        """
        self._x = x
        self._y = y

    def get_position(self) -> tuple[float, float]:
        """
        Obtient les composantes x et y de la position.

        Returns
        -------
        tuple[float, float]
            Un tuple contenant les composantes (x, y) de la position.
        """
        return (self._x, self._y)

    def distance_to(self, other: "Position2D") -> float:
        """
        Calcule la distance entre cette position et une autre.

        Parameters
        ----------
        other : Position2D
            L'autre position à laquelle calculer la distance.

        Returns
        -------
        float
            La distance entre les deux positions.
        """
        dx = self._x - other._x
        dy = self._y - other._y
        return math.hypot(dx, dy)

    def translate(self, vector: Vector2D) -> None:
        """
        Translate cette position en utilisant un vecteur.

        Parameters
        ----------
        vector : Vector2D
            Le vecteur de translation.
        """
        self._x += vector.x
        self._y += vector.y

    def translated(self, vector: Vector2D) -> "Position2D":
        """
        Retourne une nouvelle position traduite par un vecteur.

        Parameters
        ----------
        vector : Vector2D
            Le vecteur de translation.

        Returns
        -------
        Position2D
            La nouvelle position traduite.
        """
        return Position2D(self._x + vector.x, self._y + vector.y)

    def __eq__(self, other: "Position2D") -> bool:
        """
        Vérifie si deux positions sont égales.

        Parameters
        ----------
        other : Position2D
            La position à comparer.

        Returns
        -------
        bool
            True si les positions sont égales, False sinon.
        """
        return math.isclose(self._x, other._x) and math.isclose(self._y, other._y)
