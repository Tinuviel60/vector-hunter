from abc import ABC, abstractmethod
from typing import Optional

from vect_hunt.engine.core.math.vector import Vector2D


class Shape(ABC):
    """
    Base abstraite pour une forme géométrique 2D en repère local.

    La forme est supposée centrée sur (0, 0) et NON-rotée.
    Toute rotation/translation doit être appliquée via un Transform externe
    (par exemple celui du GameObject ou du Collider).

    L'objectif est de partager la même géométrie entre :
    - collisions (SAT / circle-box / etc.)
    - debug rendering (générer des points)
    - broad phase (AABB)

    Notes
    -----
    - Toutes les méthodes travaillent en coordonnées LOCALES.
    """

    @abstractmethod
    def area(self) -> float:
        """
        Retourne l'aire de la forme.

        Parameters
        ----------
        None

        Returns
        -------
        float
            L'aire de la forme.
        """

    @abstractmethod
    def perimeter(self) -> float:
        """
        Retourne le périmètre de la forme.

        Parameters
        ----------
        None

        Returns
        -------
        float
            Le périmètre de la forme.
        """

    @abstractmethod
    def aabb_local(self) -> tuple[Vector2D, Vector2D]:
        """
        Retourne l'AABB locale de la forme sous la forme (min, max).

        Parameters
        ----------
        None

        Returns
        -------
        tuple[Vector2D, Vector2D]
            Les coins min et max de l'AABB en coordonnées locales.
        """

    @abstractmethod
    def support(self, direction: Vector2D) -> Vector2D:
        """
        Retourne le point le plus éloigné dans une direction donnée (espace local).

        Cette méthode est utile pour SAT et d'autres algorithmes de collision qui
        reposent sur des points extrêmes le long d'une direction.

        Parameters
        ----------
        direction : Vector2D
            Direction de recherche (espace local). N'a pas besoin d'être normalisée.

        Returns
        -------
        Vector2D
            Le point support en coordonnées locales.
        """

    def local_vertices(self) -> Optional[list[Vector2D]]:
        """
        Retourne la liste des sommets en espace local, si la forme est polygonale.

        Les cercles n'ont pas de sommets, donc ils retournent None.

        Parameters
        ----------
        None

        Returns
        -------
        Optional[list[Vector2D]]
            Liste des sommets locaux pour les formes polygonales, sinon None.
        """
        return None

    @abstractmethod
    def closest_point_local(self, point: Vector2D) -> Vector2D:
        """
        Retourne le point le plus proche sur la forme
        par rapport à un point donné (espace local).

        Cette méthode est typiquement utilisée pour la collision cercle-boîte et pour
        calculer les informations de pénétration.

        Parameters
        ----------
        point : Vector2D
            Point de requête en espace local.

        Returns
        -------
        Vector2D
            Le point le plus proche sur la forme en espace local.
        """
        pass

    @property
    def inertia(self) -> float:
        """
        Calcule le moment d'inertie de la forme pour une masse de 1.0.

        Returns
        -------
        float
            Moment d'inertie de la forme.
        """
        raise NotImplementedError(
            "La méthode shape_inertia doit être implémentée dans les sous-classes."
        )
