from .position import Position2D
from .transform import Transform
import math
from typing import Tuple
from vect_hunt.core import geometry 

class Collider:
    def __init__(self, transform: Transform = Transform(), solid: bool = True):
        """
        Classe de base pour les colliders.
        """
        self.transform = transform
        self.solid = solid
        self.aabb = self.calculate_aabb()

    def calculate_aabb(self) -> Tuple[Position2D, Position2D]:
        """
        Calcule l'AABB (Axis-Aligned Bounding Box) du collider.

        Returns
        -------
        Tuple[Position2D, Position2D]
            Un tuple contenant le coin inférieur gauche et le coin supérieur droit de l'AABB.
        """
        return (Position2D(0, 0), Position2D(0, 0))

    def aabb_intersects(self, other: "Collider") -> bool:
        """
        Vérifie si l'AABB de ce collider intersecte avec celle d'un autre collider.

        Parameters
        ----------
        other : Collider
            L'autre collider à vérifier.

        Returns
        -------
        bool
            True si les AABB s'intersectent, False sinon.
        """
        a_min, a_max = self.aabb
        b_min, b_max = other.aabb

        return (
            a_min.x <= b_max.x
            and a_max.x >= b_min.x
            and a_min.y <= b_max.y
            and a_max.y >= b_min.y
        )

    def collides_with(self, other: "Collider") -> bool:
        """
        Vérifie si ce collider entre en collision avec un autre collider.
        Vérifie d'abord que les AABB s'intersectent, puis renvoie vers la
        méthode spécifique de collision selon le type de collider.

        Parameters
        ----------
        other : Collider
            L'autre collider à vérifier.

        Returns
        -------
        bool
            True si les colliders entrent en collision, False sinon.
        """
        raise NotImplementedError(
            "Cette méthode doit être implémentée dans les sous-classes."
        )


class BoxCollider(Collider):
    def __init__(
        self,
        center: Position2D,
        width: float,
        height: float,
        orientation: float = 0.0,
        solid: bool = True,
    ):
        """
        Initialise un BoxCollider avec une largeur, une hauteur et une orientation.
        Utiliser dans les systèmes de collision pour définir des zones rectangulaires.

        Parameters
        ----------
        center : Position2D
            Le centre du BoxCollider.
        width : float
            La largeur du BoxCollider.
        height : float
            La hauteur du BoxCollider.
        orientation : float
            L'orientation du BoxCollider en radians. Par défaut à 0.
        """
        self.width = width
        self.height = height

        transform = Transform(position=center, rotation=orientation)
        super().__init__(transform, solid)

        self.corners = self.calculate_corners()
        self.cos_orientation = math.cos(self.transform.rotation)
        self.sin_orientation = math.sin(self.transform.rotation)

    def get_area(self):
        """
        Calcule l'aire du BoxCollider.

        Returns
        -------
        float
            L'aire du rectangle.
        """
        return self.width * self.height

    def calculate_corners(self):
        """
        Calcule les coordonnées des coins du BoxCollider.

        Returns
        -------
        List[Position2D]
            Une liste des coins du BoxCollider dans l'ordre suivant :
            [top-left, top-right, bottom-right, bottom-left]
        """
        half_width = self.width / 2
        half_height = self.height / 2

        # Calcul des coins avant rotation
        corners = [
            Position2D(-half_width, half_height),  # top-left
            Position2D(half_width, half_height),  # top-right
            Position2D(half_width, -half_height),  # bottom-right
            Position2D(-half_width, -half_height),  # bottom-left
        ]

        # Rotation des coins autour du centre
        rotated_corners = []
        cos_angle = self.cos_orientation
        sin_angle = self.sin_orientation

        for corner in corners:
            rotated_x = corner.x * cos_angle - corner.y * sin_angle
            rotated_y = corner.x * sin_angle + corner.y * cos_angle
            rotated_corners.append( Position2D(rotated_x + self.transform.position.x, rotated_y + self.transform.position.y))

        return rotated_corners

    def calculate_aabb(self) -> Tuple[Position2D, Position2D]:
        """
        Calcule l'AABB (Axis-Aligned Bounding Box) du BoxCollider.

        Returns
        -------
        Tuple[Position2D, Position2D]
            Un tuple contenant le coin inférieur gauche et
            le coin supérieur droit de l'AABB.
        """

        min_x = min(corner.x for corner in self.corners)
        max_x = max(corner.x for corner in self.corners)
        min_y = min(corner.y for corner in self.corners)
        max_y = max(corner.y for corner in self.corners)

        return (Position2D(min_x, min_y), Position2D(max_x, max_y))

    def _collides_with_box(self, other: "BoxCollider") -> bool:
        """
        Vérifie la collision entre deux BoxColliders en utilisant
        la méthode de séparation des axes (SAT).

        Parameters
        ----------
        other : BoxCollider
            L'autre BoxCollider à vérifier.

        Returns
        -------
        bool
            True si les BoxColliders entrent en collision, False sinon.
        """

        # Obtenir les coins des deux BoxColliders
        corners1 = self.corners
        corners2 = other.corners

        # Obtenir les axes de projection (normales des arêtes)
        axes = geometry.get_polygon_normals(corners1) + geometry.get_polygon_normals(
            corners2
        )

        # Vérifier la projection sur chaque axe
        for axis in axes:
            min1, max1 = geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = geometry.project_polygon_on_axis(corners2, axis)

            if geometry.intervals_overlap(min1, max1, min2, max2) is False:
                return False  # Séparation trouvée

        return True  # Pas de séparation trouvée, collision détectée

    def get_closest_point_on_box(self, point: Position2D) -> Position2D:
        """
        Trouve le point le plus proche sur un BoxCollider orienté
        à partir d'un point donné.

        Cette fonction transforme le point dans le repère local du box, trouve le
        point le plus proche dans ce repère, puis le retransforme dans le repère global.
        Utilisée pour la détection de collision Circle-Box.

        Parameters
        ----------
        point : Position2D
            Le point à partir duquel trouver le point le plus proche.

        Returns
        -------
        Position2D
            Le point le plus proche sur le box.
        """
        # Transforme le point dans le repère local du box
        local_x = point.x - self.transform.position.x
        local_y = point.y - self.transform.position.y

        # Rotation inverse pour passer dans le repère du box
        cos_angle = math.cos(-self.transform.rotation)
        sin_angle = math.sin(-self.transform.rotation)

        rotated_x = local_x * cos_angle - local_y * sin_angle
        rotated_y = local_x * sin_angle + local_y * cos_angle

        # Clamp aux limites du box
        half_width = self.width / 2
        half_height = self.height / 2

        clamped_x = max(-half_width, min(half_width, rotated_x))
        clamped_y = max(-half_height, min(half_height, rotated_y))

        # Rotation directe pour revenir au repère global
        cos_angle = math.cos(self.transform.rotation)
        sin_angle = math.sin(self.transform.rotation)

        world_x = clamped_x * cos_angle - clamped_y * sin_angle + self.transform.position.x
        world_y = clamped_x * sin_angle + clamped_y * cos_angle + self.transform.position.y
        return Position2D(world_x, world_y)

    def _collides_with_circle(self, circle: "CircleCollider") -> bool:
        """
        Vérifie la collision entre un BoxCollider et un CircleCollider.

        Parameters
        ----------
        circle : CircleCollider
            Le CircleCollider à vérifier.

        Returns
        -------
        bool
            True si le BoxCollider et le CircleCollider entrent en collision, False sinon.
        """
        closest_point = self.get_closest_point_on_box(circle.transform.position)
        distance_squared = geometry.distance_squared(circle.transform.position, closest_point)
        return distance_squared <= (circle.radius**2)

    def collides_with(self, other: "Collider") -> bool:
        """
        Vérifie si ce collider entre en collision avec un autre collider.
        Vérifie d'abord que les AABB s'intersectent, puis renvoie vers la
        méthode spécifique de collision selon le type de collider.

        Parameters
        ----------
        other : Collider
            L'autre collider à vérifier.

        Returns
        -------
        bool
            True si les colliders entrent en collision, False sinon.
        """
        if not self.aabb_intersects(other):
            return False

        if isinstance(other, BoxCollider):
            return self._collides_with_box(other)
        elif isinstance(other, CircleCollider):
            return self._collides_with_circle(other)
        else:
            raise TypeError(
                "Type de collider non supporté pour la détection de collision."
            )


class CircleCollider(Collider):
    def __init__(self, center: Position2D, radius: float, solid: bool = True):
        """
        Initialise un CircleCollider avec un rayon.
        Utiliser dans les systèmes de collision pour définir des zones circulaires.

        Parameters
        ----------
        center : Position2D
            Le centre du CircleCollider.
        radius : float
            Le rayon du CircleCollider.
        """

        transform = Transform(center)
        self.radius = radius

        super().__init__(transform, solid)

        self.aabb = self.calculate_aabb()

    def get_area(self):
        """
        Calcule l'aire du CircleCollider.

        Returns
        -------
        float
            L'aire du cercle.
        """
        return math.pi * (self.radius**2)

    def calculate_aabb(self):
        """
        Calcule l'AABB (Axis-Aligned Bounding Box) du CircleCollider.

        Returns
        -------
        (Position2D, Position2D)
            Un tuple contenant le coin inférieur gauche et le coin supérieur droit de l'AABB.
        """
        min_x = self.transform.position.x - self.radius
        max_x = self.transform.position.x + self.radius
        min_y = self.transform.position.y - self.radius
        max_y = self.transform.position.y + self.radius

        return (Position2D(min_x, min_y), Position2D(max_x, max_y))

    def _collides_with_circle(self, other: "CircleCollider") -> bool:
        """
        Vérifie la collision entre deux CircleColliders.

        Parameters
        ----------
        other : CircleCollider
            L'autre CircleCollider à vérifier.

        Returns
        -------
        bool
            True si les CircleColliders entrent en collision, False sinon.
        """
        distance_squared = geometry.distance_squared(self.transform.position, other.transform.position)
        radius_sum = self.radius + other.radius
        return distance_squared <= (radius_sum**2)

    def _collides_with_box(self, box: "BoxCollider") -> bool:
        """
        Vérifie la collision entre un CircleCollider et un BoxCollider.

        Parameters
        ----------
        box : BoxCollider
            Le BoxCollider à vérifier.

        Returns
        -------
        bool
            True si le CircleCollider et le BoxCollider entrent en collision, False sinon.
        """
        closest_point = box.get_closest_point_on_box(self.transform.position)
        distance_squared = geometry.distance_squared(self.transform.position, closest_point)
        return distance_squared <= (self.radius**2)

    def collides_with(self, other: "Collider") -> bool:
        """
        Vérifie si ce collider entre en collision avec un autre collider.
        Vérifie d'abord que les AABB s'intersectent, puis renvoie vers la
        méthode spécifique de collision selon le type de collider.

        Parameters
        ----------
        other : Collider
            L'autre collider à vérifier.

        Returns
        -------
        bool
            True si les colliders entrent en collision, False sinon.
        """
        if not self.aabb_intersects(other):
            return False

        if isinstance(other, CircleCollider):
            return self._collides_with_circle(other)
        elif isinstance(other, BoxCollider):
            return self._collides_with_box(other)
        else:
            raise TypeError(
                "Type de collider non supporté pour la détection de collision."
            )
