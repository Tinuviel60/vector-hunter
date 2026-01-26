from typing import List, Tuple

from .tolerance import Tolerence
from .vector import Vector2D


class Manifold:
    @staticmethod
    def build_contact_manifold(
        corners_a: List[Vector2D],
        corners_b: List[Vector2D],
        collision_normal: Vector2D,
        penetration_depth: float,
        reference_from_a: bool | None = None,
    ) -> List[Vector2D]:
        """
        Construit 1 à 2 points de contact (manifold) par edge clipping.

        Cette fonction suppose :
        - polygones convexes,
        - sommets en sens horaire (CW),
        - collision_normal pointe de A vers B,
        - penetration_depth provient d'un SAT préalable.

        Étapes :
        1) Choisir reference edge sur A ou B (celle la plus alignée à collision_normal).
        2) Choisir incident edge sur l'autre polygone.
        3) Clipper l'incident edge contre les deux side planes de la reference edge.
        4) Filtrer les points conservés qui sont "derrière" le plan de référence.

        Parameters
        ----------
        corners_a : List[Vector2D]
            Sommets du polygone A (CW) en coordonnées scène.
        corners_b : List[Vector2D]
            Sommets du polygone B (CW) en coordonnées scène.
        collision_normal : Vector2D
            Normale de collision (unitaire) pointant de A vers B.
        penetration_depth : float
            Profondeur de pénétration (SAT).
        reference_from_a : bool | None
            Si défini, force le choix de l'arête de référence à partir du polygone A
            (True) ou B (False) en se basant sur l'axe SAT minimal.

        Returns
        -------
        List[Vector2D]
            Une liste de 0 à 2 points de contact en coordonnées scène.
        """
        normal = collision_normal.normalized()

        # On choisit la "face de référence" en se liant à l'axe SAT minimal si demandé
        if reference_from_a is None:
            ref_edge_a = Manifold._find_reference_edge(corners_a, normal)
            ref_edge_b = Manifold._find_reference_edge(corners_b, -normal)

            ref_n_a = (-(ref_edge_a[1] - ref_edge_a[0]).normal()).normalized()
            ref_n_b = (-(ref_edge_b[1] - ref_edge_b[0]).normal()).normalized()

            score_a = ref_n_a.dot(normal)
            score_b = ref_n_b.dot(-normal)

            if score_a >= score_b:
                ref_edge = ref_edge_a
                ref_normal = ref_n_a
                inc_edge = Manifold._find_incident_edge(corners_b, ref_normal)
            else:
                ref_edge = ref_edge_b
                ref_normal = ref_n_b
                inc_edge = Manifold._find_incident_edge(corners_a, ref_normal)
        elif reference_from_a:
            ref_edge = Manifold._find_reference_edge(corners_a, normal)
            ref_normal = (-(ref_edge[1] - ref_edge[0]).normal()).normalized()
            inc_edge = Manifold._find_incident_edge(corners_b, ref_normal)
        else:
            ref_edge = Manifold._find_reference_edge(corners_b, -normal)
            ref_normal = (-(ref_edge[1] - ref_edge[0]).normal()).normalized()
            inc_edge = Manifold._find_incident_edge(corners_a, ref_normal)

        # Direction de l'arête de référence (unitaire)
        ref_dir = (ref_edge[1] - ref_edge[0]).normalized()
        # "Side planes" : on clippe l'incident edge dans la bande délimitée
        # par les côtés. Les normales des side planes pointent vers l'intérieur
        # de la face de référence. Pour CW, l'intérieur de la face
        # (par rapport à l'arête) est du côté opposé à la normale sortante.
        # On construit deux planes passant par v1 et v2, perpendiculaires à ref_dir.
        side_normal_1 = (
            -ref_dir
        )  # plan perpendiculaire à ref_dir passant par v1 (garde vers v2)
        side_offset_1 = side_normal_1.dot(ref_edge[0])

        side_normal_2 = (
            ref_dir  # plan perpendiculaire à ref_dir passant par v2 (garde vers v1)
        )
        side_offset_2 = side_normal_2.dot(ref_edge[1])

        # On clippe l'incident edge contre les side planes, si moins de 2 points restent
        # , on arrête
        clipped = Manifold._clip_segment_to_line(
            inc_edge[0], inc_edge[1], side_normal_1, side_offset_1
        )
        if len(clipped) < 2:
            return []

        # On clippe contre le second plan, si rien ne reste, on arrête
        clipped = Manifold._clip_segment_to_line(
            clipped[0], clipped[1], side_normal_2, side_offset_2
        )
        if not clipped:
            return []

        # Plan de la face de référence : n·x = offset
        # offset = n·v1 (face plane)
        face_offset = ref_normal.dot(ref_edge[0])

        eps = Tolerence.COLLISION
        # Filtrage final : on garde les points qui sont derrière la face (pénétration)
        contacts: List[Vector2D] = []
        for p in clipped:
            separation = ref_normal.dot(p) - face_offset
            # séparation <= 0 => point sur ou derrière le plan de face (donc en contact)
            if separation <= eps:
                contacts.append(p)

        # En pratique, tu obtiens 0..2 points. On peut réduire si >2 (rare).
        if len(contacts) > 2:
            contacts = contacts[:2]

        return contacts

    @staticmethod
    def _find_incident_edge(
        corners: List[Vector2D],
        reference_normal: Vector2D,
    ) -> Tuple[Vector2D, Vector2D]:
        """
        Choisit l'arête "incidente" sur un polygone.

        L'arête incidente est celle dont la normale sortante est la plus opposée
        à la normale de la face de référence (celle qui "fait face" à la collision).

        Parameters
        ----------
        corners : List[Vector2D]
            Sommets du polygone (CW) en coordonnées scène.
        reference_normal : Vector2D
            Normale sortante de l'arête référence (unitaire).

        Returns
        -------
        Tuple[Vector2D, Vector2D]
            Arête incidente.
        """
        best_index = 0
        best_dot = float("inf")  # on veut minimiser dot(n_edge, reference_normal)

        for i in range(len(corners)):
            v1 = corners[i]
            v2 = corners[(i + 1) % len(corners)]
            edge = v2 - v1

            normal = (-edge.normal()).normalized()
            dot = normal.dot(reference_normal)
            if dot < best_dot:
                best_dot = dot
                best_index = i

        return (corners[best_index], corners[(best_index + 1) % len(corners)])

    @staticmethod
    def _clip_segment_to_line(
        p1: Vector2D,
        p2: Vector2D,
        plane_normal: Vector2D,
        plane_offset: float,
    ) -> List[Vector2D]:
        """
        Clippe un segment contre un demi-plan défini par une normale et un offset.

        On renvoie 0 à 2 points (les extrémités du segment résultant après clipping).
        Cette fonction est la brique centrale du "edge clipping".

        Parameters
        ----------
        p1 : Vector2D
            Premier point du segment (scène).
        p2 : Vector2D
            Second point du segment (scène).
        plane_normal : Vector2D
            Normale unitaire du plan.
        plane_offset : float
            Offset du plan (n·x = offset).
        Returns
        -------
        List[Vector2D]
            Liste de 0 à 2 points correspondant au segment clippé.
        """
        # Calcul des distances des points au plan
        d1 = plane_normal.dot(p1) - plane_offset
        d2 = plane_normal.dot(p2) - plane_offset

        eps = Tolerence.COLLISION
        inside1 = d1 <= eps
        inside2 = d2 <= eps

        points: List[Vector2D] = []

        # Si un point est dedans, on le garde
        if inside1:
            points.append(p1)
        if inside2:
            points.append(p2)

        # Si le segment traverse le plan, on ajoute le point d'intersection
        if inside1 ^ inside2:  # XOR, équivalent à len(points) == 1
            # t (lambda) tel que :
            # point d'intersection = p1 + t * (p2 - p1) et n·p = offset
            direction = p2 - p1
            denominateur = plane_normal.dot(direction)
            if abs(denominateur) > eps:
                t = (plane_offset - plane_normal.dot(p1)) / denominateur
                intersection = p1 + direction * t
                points.append(intersection)

        # On s'assure de ne pas renvoyer plus de 2 points (au cas où)
        if len(points) <= 2:
            return points

        # Déduplique les points très proches dans le cas où on en a plus de 2 points
        unique: List[Vector2D] = []
        for p in points:
            if all((p - q).magnitude_squared() > (eps * eps) for q in unique):
                unique.append(p)

        return unique[:2]

    @staticmethod
    def _find_reference_edge(
        corners: List[Vector2D],
        collision_normal: Vector2D,
    ) -> Tuple[Vector2D, Vector2D]:
        """
        Choisit l'arête "référence" sur un polygone.

        On cherche l'arête dont la normale sortante est la plus alignée
        avec la normale de collision.

        Parameters
        ----------
        corners : List[Vector2D]
            Sommets du polygone (CW) en coordonnées scène.
        collision_normal : Vector2D
            Normale de collision (unitaire) pointant de A vers B.

        Returns
        -------
        Tuple[Vector2D, Vector2D]
            L'arête de référence (Vector2D start, Vector2D end).
        """
        best_index = 0
        best_dot = float("-inf")

        for i in range(len(corners)):
            v1 = corners[i]
            v2 = corners[(i + 1) % len(corners)]
            edge = v2 - v1

            normal = (-edge.normal()).normalized()
            dot = normal.dot(collision_normal)
            if dot > best_dot:
                best_dot = dot
                best_index = i

        ref_edge = (corners[best_index], corners[(best_index + 1) % len(corners)])
        return ref_edge
