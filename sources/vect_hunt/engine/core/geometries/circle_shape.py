import math
from dataclasses import dataclass

from vect_hunt.engine.core.geometries.shape import Shape
from vect_hunt.engine.core.math.vector import Vector2D


@dataclass(frozen=True, slots=True)
class CircleShape(Shape):
    """
    Forme de cercle en espace local.
    La forme est centrée en (0, 0). La translation est externe (Transform).
    """

    radius: float

    def __post_init__(self) -> None:
        """
        Validation du rayon du cercle.
        """
        if self.radius <= 0.0:
            raise ValueError("Le rayon du cercle doit être > 0.")

    def area(self) -> float:
        """
        Retourne l'aire du cercle.

        Returns
        -------
        float
            L'aire du cercle.
        """

        return math.pi * (self.radius**2)

    def perimeter(self) -> float:
        """
        Retourne le périmètre du cercle.

        Returns
        -------
        float
            Le périmètre du cercle (circonférence).
        """

        return 2.0 * math.pi * self.radius

    def aabb_local(self) -> tuple[Vector2D, Vector2D]:
        """
        Retourne l'AABB locale du cercle sous forme de (min, max).

        Returns
        -------
        tuple[Vector2D, Vector2D]
            AABB locale du cercle sous forme de (min, max).
        """
        r = self.radius
        return (Vector2D(-r, -r), Vector2D(r, r))

    def support(self, direction: Vector2D) -> Vector2D:
        """
        Retourne le point le plus éloigné sur le cercle dans une direction donnée.

        Parameters
        ----------
        direction : Vector2D
            Direction de recherche (espace local). N'a pas besoin d'être normalisée.

        Returns
        -------
        Vector2D
            Point de support sur le cercle en espace local.
        """
        # Si direction est nulle, on renvoie un point arbitraire.
        if direction.magnitude_squared() <= 1e-9:  # TODO: faire appel a epsilon globale
            return Vector2D(self.radius, 0.0)

        dir_norm = direction.normalized()
        return dir_norm * self.radius

    def closest_point_local(self, point: Vector2D) -> Vector2D:
        """
        Retourne le point le plus proche sur le cercle par rapport au point local donné.

        Si le point est à l'intérieur du cercle, le point le plus proche est le point
        lui-même (utile pour les calculs de pénétration en dehors de cette classe).

        Parameters
        ----------
        point : Vector2D
            Point de requête en espace local.

        Returns
        -------
        Vector2D
            Point le plus proche sur le cercle en espace local.
        """
        dist_sq = point.magnitude_squared()
        r_sq = self.radius * self.radius

        if dist_sq <= r_sq:
            return point

        # Point outside: clamp onto circle boundary
        if dist_sq <= 1e-9:  # TODO: faire appel a epsilon globale
            return Vector2D(self.radius, 0.0)

        return point.normalized() * self.radius

    @property
    def inertia(self) -> float:
        """
        Calcule le moment d'inertie du cercle pour une masse de 1.0.

        Returns
        -------
        float
            Moment d'inertie du cercle.
        """
        return 0.5 * (self.radius**2)
