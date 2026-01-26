from typing import TYPE_CHECKING, List, Tuple

from vect_hunt.engine.core.geometries.box_shape import BoxShape
from vect_hunt.engine.core.math.numeric import Numeric
from vect_hunt.engine.core.transform.transform import Transform

from .tolerance import Tolerence
from .vector import Vector2D

from vect_hunt.engine.physics.collision_info import CollisionInfo


class Geometry:
    """
    Fournit des fonctions géométriques utilitaires pour la détection de collisions
    et d'autres opérations géométriques.

    Attributes
    ----------
    None
    """

    @staticmethod
    def get_polygon_normals(corners: List[Vector2D]) -> List[Vector2D]:
        """
        Calcule les normales unitaires aux arêtes d'un polygone.

        Pour chaque arête du polygone, calcule le vecteur normal (perpendiculaire)
        et le normalise. Ces normales sont utilisées comme axes de projection
        dans l'algorithme SAT (Separating Axis Theorem).

        Parameters
        ----------
        corners : List[Vector2D]
            Liste des coins du polygone dans l'ordre (sens horaire ou anti-horaire).

        Returns
        -------
        List[Vector2D]
            Liste des vecteurs normaux unitaires aux arêtes du polygone.
        """
        normals = []
        num_corners = len(corners)

        for i in range(num_corners):
            # Récupère les deux coins formant l'arête
            p1 = corners[i]
            p2 = corners[(i + 1) % num_corners]  # Boucle au premier coin

            # Vecteur de l'arête
            edge = Vector2D(p2.x - p1.x, p2.y - p1.y)

            # Calcule la normale (perpendiculaire) à l'arête
            normal = edge.normal()

            # Normalise le vecteur normal
            normal.normalize()
            normals.append(normal)

        return normals

    @staticmethod
    def project_polygon_on_axis(
        corners: List[Vector2D], axis: Vector2D
    ) -> Tuple[float, float]:
        """
        Projette les coins d'un polygone sur un axe et retourne l'intervalle [min, max].

        La projection d'un point sur un axe est calculée via le produit scalaire.
        Cette fonction est utilisée dans l'algorithme SAT pour détecter si deux
        polygones se chevauchent sur un axe donné.

        Parameters
        ----------
        corners : List[Vector2D]
            Liste des coins du polygone.
        axis : Vector2D
            L'axe de projection (doit être un vecteur unitaire).

        Returns
        -------
        Tuple[float, float]
            Un tuple (min_projection, max_projection) représentant l'intervalle
            de projection du polygone sur l'axe.
        """
        min_proj = float("inf")
        max_proj = float("-inf")

        for corner in corners:
            # Calcule la projection via le produit scalaire
            projection = corner.dot(axis)

            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)

        return (min_proj, max_proj)

    @staticmethod
    def intervals_overlap(min1: float, max1: float, min2: float, max2: float) -> bool:
        """
        Vérifie si deux intervalles [min1, max1] et [min2, max2] se chevauchent.

        Parameters
        ----------
        min1 : float
            Borne inférieure du premier intervalle.
        max1 : float
            Borne supérieure du premier intervalle.
        min2 : float
            Borne inférieure du deuxième intervalle.
        max2 : float
            Borne supérieure du deuxième intervalle.

        Returns
        -------
        bool
            True si les intervalles se chevauchent, False sinon.
        """
        return max1 >= min2 and max2 >= min1

    @staticmethod
    def aabb_overlap(
        a_min: Vector2D, a_max: Vector2D, b_min: Vector2D, b_max: Vector2D
    ) -> bool:
        """
        Vérifie si deux AABB se superposent.

        Parameters
        ----------
        a_min : Vector2D
            Borne min AABB 1.
        a_max : Vector2D
            Borne max AABB 1.
        b_min : Vector2D
            Borne min AABB 2.
        b_max : Vector2D
            Borne max AABB 2.

        Returns
        -------
        bool
            True si les AABB se superposent, False sinon.
        """
        return Geometry.intervals_overlap(
            a_min.x, a_max.x, b_min.x, b_max.x
        ) and Geometry.intervals_overlap(a_min.y, a_max.y, b_min.y, b_max.y)

    @staticmethod
    def to_local(point: Vector2D, scene_tr: Transform) -> Vector2D:
        """
        Convertit un point scene vers un repere local.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees monde.
        scene_tr : Transform
            Transform du repere monde.

        Returns
        -------
        Vector2D
            Point en coordonnees locales.
        """
        return scene_tr.rotation.apply_inverse(point - scene_tr.position)

    @staticmethod
    def to_scene(point: Vector2D, scene_tr: Transform) -> Vector2D:
        """
        Convertit un point local vers le repere scene.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees locales.
        scene_tr : Transform
            Transform du repere monde.

        Returns
        -------
        Vector2D
            Point en coordonnees monde.
        """
        return scene_tr.position + scene_tr.rotation.apply(point)

    @staticmethod
    def get_scene_corners(
        local_corners: List[Vector2D], scene_tr: Transform
    ) -> List[Vector2D]:
        """
        Transforme des coins locaux vers des coins monde.

        Parameters
        ----------
        local_corners : List[Vector2D]
            Coins en repere local.
        scene_tr : Transform
            Transform du repere monde.

        Returns
        -------
        List[Vector2D]
            Coins en repere monde.
        """
        return [scene_tr.rotation.apply(corner) + scene_tr.position for corner in local_corners]


    @staticmethod
    def closest_point_on_box(
        point: Vector2D,
        box_scene_tr: Transform,
        box_shape: BoxShape,
    ) -> Vector2D:
        """
        Calcule le point le plus proche sur un rectangle oriente.

        Parameters
        ----------
        point : Vector2D
            Point en coordonnees monde.
        box_scene_tr : Transform
            Transform du box.
        box_shape: BoxShape
            Forme du box.

        Returns
        -------
        Vector2D
            Point le plus proche en monde.
        """
        local_point = Geometry.to_local(point, box_scene_tr)

        half_w = box_shape.width / 2
        half_h = box_shape.height / 2

        clamped_x = Numeric.clamp(local_point.x, -half_w, half_w)
        clamped_y = Numeric.clamp(local_point.y, -half_h, half_h)

        return Geometry.to_scene(Vector2D(clamped_x, clamped_y), box_scene_tr)

    @staticmethod
    def circle_circle_collision_info(
        pos1: Vector2D,
        radius1: float,
        pos2: Vector2D,
        radius2: float,
    ) -> "CollisionInfo | None":
        """
        Détecte une collision entre deux cercles.

        Parameters
        ----------
        pos1 : Vector2D
            Centre du premier cercle.
        radius1 : float
            Rayon du premier cercle.
        pos2 : Vector2D
            Centre du second cercle.
        radius2 : float
            Rayon du second cercle.

        Returns
        -------
        CollisionInfo | None
            Informations de collision ou None.
        """
        delta = pos2 - pos1
        radius_sum = radius1 + radius2
        radius_sum2 = radius_sum * radius_sum

        dist2 = delta.magnitude_squared()
        if dist2 >= radius_sum2:
            return None
        
        # Cas collision : on calcule la distance réelle une seule fois
        if dist2 <= Tolerence.GENERAL:
            # Centres (quasi) confondus : normale arbitraire mais stable
            normal = Vector2D(-1.0, 0.0)
            dist = 0.0
        else:
            dist = dist2 ** 0.5
            inv_dist = 1.0 / dist
            normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)

        penetration = radius_sum - dist
        if penetration < Tolerence.COLLISION:
            return None

        # Point de contact côté cercle 2 (sur sa surface, vers l'extérieur)
        contact_point = pos2 + (-normal) * radius2

        return CollisionInfo(normal=normal, depth=penetration, points=[contact_point])

    @staticmethod
    def get_polygon_center(corners: List[Vector2D]) -> Vector2D:
        """
        Calcule le centre (centroïde) d'un polygone.

        Parameters
        ----------
        corners : List[Vector2D]
            Coins du polygone.

        Returns
        -------
        Vector2D
            Centre du polygone.
        """
        sum_x = sum(corner.x for corner in corners)
        sum_y = sum(corner.y for corner in corners)
        num_corners = len(corners)
        return Vector2D(sum_x / num_corners, sum_y / num_corners)

    @staticmethod
    def sat_collision_info(
        corners1: List[Vector2D],
        corners2: List[Vector2D],
    ) -> CollisionInfo | None:
        """
        Détecte une collision SAT entre deux polygones.

        Parameters
        ----------
        corners1 : List[Vector2D]
            Coins du polygone 1.
        corners2 : List[Vector2D]
            Coins du polygone 2.
        Returns
        -------
        dict | None
            Informations de collision (normal, depth) ou None.
        """
        axes: List[tuple[Vector2D, bool]] = []
        for axis in Geometry.get_polygon_normals(corners1):
            axes.append((axis, True))
        for axis in Geometry.get_polygon_normals(corners2):
            axes.append((axis, False))
        penetration = float("inf")
        smallest_axis = None
        axis_from_a = True

        for axis, from_a in axes:
            min1, max1 = Geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = Geometry.project_polygon_on_axis(corners2, axis)
            if not Geometry.intervals_overlap(min1, max1, min2, max2):
                return None

            overlap = min(max1, max2) - max(min1, min2)
            if overlap < penetration:
                penetration = overlap
                smallest_axis = axis
                axis_from_a = from_a

        eps = Tolerence.COLLISION
        if penetration < eps or smallest_axis is None:
            return None

        normal = smallest_axis.normalized()

        center1 = Geometry.get_polygon_center(corners1)
        center2 = Geometry.get_polygon_center(corners2)
        direction = center2 - center1
        if direction.dot(normal) < 0:
            normal = -normal

        points = Geometry._build_contact_manifold(
            corners_a=corners1,
            corners_b=corners2,
            collision_normal=normal,
            penetration_depth=penetration,
            reference_from_a=axis_from_a,
        )
        return CollisionInfo(normal=normal, depth=penetration, points=points)

    @staticmethod
    def circle_box_collision_info(
        circle_pos: Vector2D,
        circle_radius: float,
        box_scene_tr: Transform,
        box_shape: BoxShape,
    ) -> "CollisionInfo | None":
        """
        Détecte une collision entre un cercle et un rectangle orienté.

        Parameters
        ----------
        circle_pos : Vector2D
            Centre du cercle.
        circle_radius : float
            Rayon du cercle.
        box_scene_tr : Transform
            Transform du box.
        box_shape: BoxShape
            Forme du box.

        Returns
        -------
        CollisionInfo | None
            Informations de collision (normal, depth, point) ou None.
        """
        closest = Geometry.closest_point_on_box(circle_pos, box_scene_tr, box_shape)
        delta = circle_pos - closest
        dist2 = delta.magnitude_squared()

        if dist2 < circle_radius * circle_radius:
            dist = dist2 ** 0.5
            penetration = circle_radius - dist
            if penetration < Tolerence.COLLISION:
                return None

            if dist2 <= Tolerence.GENERAL:
                normal = Vector2D(-1.0, 0.0)  # fallback stable
            else:
                inv_dist = 1.0 / dist
                normal = Vector2D(delta.x * inv_dist, delta.y * inv_dist)

            return CollisionInfo(normal=normal, depth=penetration, points=[closest])
        return None

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
    def _build_contact_manifold(
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
            ref_edge_a = Geometry._find_reference_edge(corners_a, normal)
            ref_edge_b = Geometry._find_reference_edge(corners_b, -normal)

            ref_n_a = (-(ref_edge_a[1] - ref_edge_a[0]).normal()).normalized()
            ref_n_b = (-(ref_edge_b[1] - ref_edge_b[0]).normal()).normalized()

            score_a = ref_n_a.dot(normal)
            score_b = ref_n_b.dot(-normal)

            if score_a >= score_b:
                ref_edge = ref_edge_a
                ref_normal = ref_n_a
                inc_edge = Geometry._find_incident_edge(corners_b, ref_normal)
            else:
                ref_edge = ref_edge_b
                ref_normal = ref_n_b
                inc_edge = Geometry._find_incident_edge(corners_a, ref_normal)
        elif reference_from_a:
            ref_edge = Geometry._find_reference_edge(corners_a, normal)
            ref_normal = (-(ref_edge[1] - ref_edge[0]).normal()).normalized()
            inc_edge = Geometry._find_incident_edge(corners_b, ref_normal)
        else:
            ref_edge = Geometry._find_reference_edge(corners_b, -normal)
            ref_normal = (-(ref_edge[1] - ref_edge[0]).normal()).normalized()
            inc_edge = Geometry._find_incident_edge(corners_a, ref_normal)

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
        clipped = Geometry._clip_segment_to_line(
            inc_edge[0], inc_edge[1], side_normal_1, side_offset_1
        )
        if len(clipped) < 2:
            return []

        # On clippe contre le second plan, si rien ne reste, on arrête
        clipped = Geometry._clip_segment_to_line(
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
