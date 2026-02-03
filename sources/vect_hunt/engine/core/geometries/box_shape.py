from dataclasses import dataclass

from vect_hunt.engine.core.geometries.shape import Shape
from vect_hunt.engine.core.math.vector import Vector2D


@dataclass(frozen=True, slots=True)
class BoxShape(Shape):
    """
    Box shape in local space, aligné avec les axes.
    La forme est centrée en (0, 0). La translation est externe (Transform).

    Parameters
    ----------
    width : float
        Largeur du box.
    height : float
        Hauteur du box.
    """

    width: float
    height: float

    def __post_init__(self) -> None:
        """
        Validation des dimensions du box.

        Returns
        -------
        None
        """
        if self.width <= 0.0 or self.height <= 0.0:
            raise ValueError("Largeur et hauteur du box doivent être > 0.")

    def area(self) -> float:
        """
        Retourne l'aire du box.

        Returns
        -------
        float
            L'aire du box.
        """
        return self.width * self.height

    def perimeter(self) -> float:
        """
        Retourne le périmètre du box.

        Returns
        -------
        float
            Le périmètre du box.
        """
        return 2.0 * (self.width + self.height)

    def aabb_local(self) -> tuple[Vector2D, Vector2D]:
        """
        Retourne l'AABB local du box sous la forme (min, max).

        Parameters
        ----------
        None

        Returns
        -------
        tuple[Vector2D, Vector2D]
            Les coins min et max de l'AABB en coordonnées locales.
        """
        half_w = self.width * 0.5
        half_h = self.height * 0.5
        return (Vector2D(-half_w, -half_h), Vector2D(half_w, half_h))

    def local_vertices(self) -> list[Vector2D]:
        """
        Retourne les 4 sommets du box en espace local (ordre cyclique).

        Returns
        -------
        list[Vector2D]
            Les 4 sommets locaux dans un ordre cyclique.
        """
        half_w = self.width * 0.5
        half_h = self.height * 0.5
        return [
            Vector2D(-half_w, -half_h),
            Vector2D(half_w, -half_h),
            Vector2D(half_w, half_h),
            Vector2D(-half_w, half_h),
        ]

    def support(self, direction: Vector2D) -> Vector2D:
        """
        Retourne le coin du box le plus éloigné dans la direction donnée.

        Parameters
        ----------
        direction : Vector2D
            Direction de recherche (espace local).

        Returns
        -------
        Vector2D
            Point de support en espace local.
        """
        half_w = self.width * 0.5
        half_h = self.height * 0.5

        x = half_w if direction.x >= 0.0 else -half_w
        y = half_h if direction.y >= 0.0 else -half_h
        return Vector2D(x, y)

    def closest_point_local(self, point: Vector2D) -> Vector2D:
        """
        Retourne le point le plus proche sur le box par rapport au point local donné.

        Parameters
        ----------
        point : Vector2D
            Point de requête en espace local.

        Returns
        -------
        Vector2D
            Point le plus proche sur le box en espace local.
        """
        half_w = self.width * 0.5
        half_h = self.height * 0.5

        clamped_x = max(-half_w, min(half_w, point.x))
        clamped_y = max(-half_h, min(half_h, point.y))
        return Vector2D(clamped_x, clamped_y)

    @property
    def inertia(self) -> float:
        """
        Calcule le moment d'inertie du box pour une masse de 1.0.

        Returns
        -------
        float
            Moment d'inertie du box.
        """
        return (1 / 12) * (self.width**2 + self.height**2)
