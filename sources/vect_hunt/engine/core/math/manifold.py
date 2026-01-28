from typing import List, Tuple

from .tolerance import Tolerence
from .vector import Vector2D


class Manifold:
    """
    Utilitaires de génération de points de contact (manifold).

    Version spécialisée pour OBB (rectangles orientés) : 4 coins en ordre cyclique.
    """

    @staticmethod
    def build_contact_manifold(
        corners_a: List[Vector2D],
        corners_b: List[Vector2D],
        collision_normal: Vector2D,
        reference_from_a: bool,
    ) -> List[Vector2D]:
        """
        Construit 0 à 2 points de contact pour une collision OBB/OBB.

        Parameters
        ----------
        corners_a : List[Vector2D]
            4 coins du rectangle A en coordonnées scène (ordre cyclique).
        corners_b : List[Vector2D]
            4 coins du rectangle B en coordonnées scène (ordre cyclique).
        collision_normal : Vector2D
            Normale unitaire A -> B (issue du SAT).
        reference_from_a : bool
            True si l'axe SAT minimal vient de A, sinon False.

        Returns
        -------
        List[Vector2D]
            Liste de 0 à 2 points de contact en coordonnées scène.
        """
        if len(corners_a) != 4 or len(corners_b) != 4:
            raise ValueError("build_contact_manifold attend 4 coins par rectangle.")

        # Ref = polygone dont provient l'axe SAT minimal
        if reference_from_a:
            ref_corners = corners_a
            inc_corners = corners_b
            ref_normal = collision_normal  # déjà unitaire et (A -> B)
        else:
            ref_corners = corners_b
            inc_corners = corners_a
            ref_normal = -collision_normal  # face de B qui fait face à A

        # 1) Choisir l'arête de référence 
        # (celle dont la normale sortante est la plus alignée)
        ref_i = Manifold._box_reference_edge_index(ref_corners, ref_normal)
        ref_v1 = ref_corners[ref_i]
        ref_v2 = ref_corners[(ref_i + 1) & 3]

        # 2) Choisir l'arête incidente (normale la plus opposée à ref_normal)
        inc_i = Manifold._box_incident_edge_index(inc_corners, ref_normal)
        inc_p1 = inc_corners[inc_i]
        inc_p2 = inc_corners[(inc_i + 1) & 3]

        # 3) Side planes de la face de référence
        # ref_dir = direction de l'arête (unitaire) -> dérivée de la normale (perp)
        ref_edge = ref_v2 - ref_v1

        if ref_edge.magnitude_squared() <= Tolerence.GENERAL * Tolerence.GENERAL:
            return []

        ref_dir = ref_edge.normalized()  # direction arête (tangent)

        # deux demi-plans latéraux qui délimitent la face
        side_n1 = -ref_dir
        side_o1 = side_n1.dot(ref_v1)

        side_n2 = ref_dir
        side_o2 = side_n2.dot(ref_v2)

        clipped = Manifold._clip_segment_to_line_2pts(inc_p1, inc_p2, side_n1, side_o1)
        if clipped is None:
            return []
        c1, c2 = clipped

        clipped = Manifold._clip_segment_to_line_2pts(c1, c2, side_n2, side_o2)
        if clipped is None:
            return []
        c1, c2 = clipped

        # 4) Face plane : ref_normal · x = ref_normal · ref_v1
        face_offset = ref_normal.dot(ref_v1)

        eps = Tolerence.COLLISION
        eps2 = eps * eps
        #TODO : Remettre epsilon
        contacts: List[Vector2D] = []

        sep1 = ref_normal.dot(c1) - face_offset
        if sep1 <= 0.5:
            contacts.append(c1)

        sep2 = ref_normal.dot(c2) - face_offset
        if sep2 <= 0.5:
            if not contacts or (c2 - contacts[0]).magnitude_squared() > 0.5 * 0.5:
                contacts.append(c2)

        return contacts

    @staticmethod
    def _box_reference_edge_index(corners: List[Vector2D], face_dir: Vector2D) -> int:
        """
        Choisit l'arête référence d'une box (OBB).

        Parameters
        ----------
        corners : List[Vector2D]
            4 coins en ordre cyclique.
        face_dir : Vector2D
            Normale cible unitaire (normale de face issue du SAT).

        Returns
        -------
        int
            Index i de l'arête (corners[i] -> corners[i+1]).
        """
        # Normales de face unitaires de la box (4) 
        # calculées avec seulement 2 normalisations
        n0, n1, n2, n3 = Manifold._box_face_normals(corners)

        # On maximise dot(n_i, face_dir)
        d0 = n0.dot(face_dir)
        d1 = n1.dot(face_dir)
        d2 = n2.dot(face_dir)
        d3 = n3.dot(face_dir)

        best_i = 0
        best_d = d0

        if d1 > best_d:
            best_d = d1
            best_i = 1
        if d2 > best_d:
            best_d = d2
            best_i = 2
        if d3 > best_d:
            best_i = 3

        return best_i

    @staticmethod
    def _box_incident_edge_index(corners: List[Vector2D], ref_normal: Vector2D) -> int:
        """
        Choisit l'arête incidente d'une box (OBB).

        Parameters
        ----------
        corners : List[Vector2D]
            4 coins en ordre cyclique.
        ref_normal : Vector2D
            Normale unitaire de la face de référence.

        Returns
        -------
        int
            Index i de l'arête (corners[i] -> corners[i+1]).
        """
        n0, n1, n2, n3 = Manifold._box_face_normals(corners)

        # On minimise dot(n_i, ref_normal) (la plus opposée)
        d0 = n0.dot(ref_normal)
        d1 = n1.dot(ref_normal)
        d2 = n2.dot(ref_normal)
        d3 = n3.dot(ref_normal)

        best_i = 0
        best_d = d0

        if d1 < best_d:
            best_d = d1
            best_i = 1
        if d2 < best_d:
            best_d = d2
            best_i = 2
        if d3 < best_d:
            best_i = 3

        return best_i

    @staticmethod
    def _box_face_normals(
        corners: List[Vector2D],
    ) -> Tuple[Vector2D, Vector2D, Vector2D, Vector2D]:
        """
        Calcule les 4 normales sortantes unitaires d'une box.

        Contrairement à une approche basée sur CW/CCW, on choisit le signe
        de la normale en vérifiant qu'elle pointe vers l'extérieur (loin du centre).

        Parameters
        ----------
        corners : List[Vector2D]
            4 coins dans un ordre cyclique (CW ou CCW).

        Returns
        -------
        Tuple[Vector2D, Vector2D, Vector2D, Vector2D]
            (n0, n1, n2, n3) normales sortantes unitaires des 4 arêtes.
        """
        if len(corners) != 4:
            raise ValueError("_box_face_normals attend 4 coins.")

        # Centre (centroïde simple)
        center = Vector2D(
            (corners[0].x + corners[1].x + corners[2].x + corners[3].x) * 0.25,
            (corners[0].y + corners[1].y + corners[2].y + corners[3].y) * 0.25,
        )

        normals: List[Vector2D] = []
        eps2 = Tolerence.GENERAL * Tolerence.GENERAL

        for i in range(4):
            a = corners[i]
            b = corners[(i + 1) & 3]
            edge = b - a
            if edge.magnitude_squared() <= eps2:
                normals.append(Vector2D(1.0, 0.0))
                continue

            # Normale candidate (perpendiculaire)
            n = edge.normal().normalized()

            # On force la normale à pointer vers l'extérieur :
            # si elle pointe vers le centre, on l'inverse.
            mid = (a + b) * 0.5
            to_mid = mid - center
            if n.dot(to_mid) < 0.0:
                n = -n

            normals.append(n)

        return normals[0], normals[1], normals[2], normals[3]

    @staticmethod
    def _clip_segment_to_line_2pts(
        p1: Vector2D,
        p2: Vector2D,
        plane_normal: Vector2D,
        plane_offset: float,
    ) -> Tuple[Vector2D, Vector2D] | None:
        """
        Clippe un segment contre un demi-plan et retourne 2 points si survivant.

        Parameters
        ----------
        p1 : Vector2D
            Premier point du segment.
        p2 : Vector2D
            Second point du segment.
        plane_normal : Vector2D
            Normale unitaire du plan.
        plane_offset : float
            Offset du plan (n·x = offset).

        Returns
        -------
        Tuple[Vector2D, Vector2D] | None
            Segment clippé (2 points), ou None si rejeté.
        """
        eps = 0.5#Tolerence.COLLISION

        d1 = plane_normal.dot(p1) - plane_offset
        d2 = plane_normal.dot(p2) - plane_offset

        inside1 = d1 <= eps
        inside2 = d2 <= eps

        if not inside1 and not inside2:
            return None
        if inside1 and inside2:
            return (p1, p2)

        direction = p2 - p1
        denom = plane_normal.dot(direction)
        if abs(denom) <= Tolerence.GENERAL:
            return (p1, p1) if inside1 else (p2, p2)

        t = (plane_offset - plane_normal.dot(p1)) / denom
        inter = p1 + direction * t

        return (p1, inter) if inside1 else (inter, p2)
