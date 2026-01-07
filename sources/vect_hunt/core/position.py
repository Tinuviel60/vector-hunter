import math
from .vector import Vector2D

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
    
    def distance_to(self, other: 'Position2D') -> float:
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
        return math.sqrt(dx * dx + dy * dy)
    
    def __add__(self, other: Vector2D) -> 'Position2D':
        """
        Ajoute un vecteur à cette position.

        Parameters
        ----------
        other : Vector2D
            Le vecteur à ajouter.
        
        Returns
        -------
        Position2D
            La nouvelle position résultant de l'addition.
        """
        return Position2D(self._x + other._x, self._y + other._y)
    
    def __sub__(self, other):
        """
        Soustrait soit une position, soit un vecteur à cette position.

        - Position - Position -> Vector2D
        - Position - Vector2D -> Position2D
        """
        if isinstance(other, Position2D):
            return Vector2D(self._x - other._x, self._y - other._y)

        if isinstance(other, Vector2D):
            return Position2D(self._x - other._x, self._y - other._y)

        raise TypeError("Unsupported operand for Position2D subtraction")

    def __eq__(self, other: 'Position2D') -> bool:
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