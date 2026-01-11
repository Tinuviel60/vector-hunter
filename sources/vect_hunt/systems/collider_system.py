from typing import List

from .tag_system import TagSystem

from vect_hunt.core import (
    Tag,
    Transform,
    Vector2D,
    Geometry,
    Collider,
    BoxCollider,
    CircleCollider,
)
from vect_hunt.objects import GameObject


class ColliderSystem:
    """
    Système global de collision pour un ensemble de colliders.

    - Gère la liste des colliders actifs.
    - Calcule les AABB et collisions entre eux.
    - Fournit des méthodes pour vérifier les collisions pour un objet spécifique.
    """

    def __init__(self):
        self.colliders: dict[Tag, List[Collider]] = {}

    def register(self, game_object: GameObject) -> None:
        """
        Ajoute les collider d'un objet de jeu au système.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu dont les colliders doivent être ajoutés.
        """
        for tag in game_object.list_tags():
            if tag not in self.colliders:
                self.colliders[tag] = []
            for collider in game_object.colliders:
                self.colliders[tag].append(collider)

    def unregister(self, game_object: GameObject) -> None:
        """
        Retire les collider d'un objet de jeu du système.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu dont les colliders doivent être retirés.
        """
        for tag in game_object.list_tags():
            if tag in self.colliders:
                for collider in game_object.colliders:
                    if collider in self.colliders[tag]:
                        self.colliders[tag].remove(collider)

    def update_tag(self, game_object: GameObject) -> None:
        """
        Met à jour l'affectation des colliders d'un objet en fonction de ses tags.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu dont les colliders doivent être mis à jour.
        """
        self.unregister(game_object)
        self.register(game_object)

    # --------------------
    # AABB Mondial
    # --------------------
    @staticmethod
    def compute_aabb(collider: Collider, parent_transform: Transform) -> tuple:
        """
        Calcule l'AABB mondial du collider.

        Pour CircleCollider : centre ± rayon
        Pour BoxCollider : calcule coins mondiaux
        """
        if isinstance(collider, CircleCollider):
            return ColliderSystem._compute_aabb_circle(collider, parent_transform)
        elif isinstance(collider, BoxCollider):
            return ColliderSystem._compute_aabb_box(collider, parent_transform)
        else:
            raise TypeError("Collider inconnu pour calcul AABB")

    @staticmethod
    def _compute_aabb_box(collider: BoxCollider, parent_transform: Transform):
        """
        Calcule l'AABB mondial d'un BoxCollider.

        Parameters
        ----------
        collider : BoxCollider
            Le BoxCollider dont on veut calculer l'AABB.
        parent_transform : Transform
            La transformation du GameObject parent.

        Returns
        -------
        tuple
            L'AABB sous la forme (min_x, min_y, max_x, max_y
        """
        world_corners = ColliderSystem.get_world_corners(
            collider.corners, parent_transform
        )
        xs = [c.x for c in world_corners]
        ys = [c.y for c in world_corners]
        return (min(xs), min(ys), max(xs), max(ys))

    @staticmethod
    def _compute_aabb_circle(collider: CircleCollider, parent_transform: Transform):
        """
        Calcule l'AABB mondial d'un CircleCollider.

        Parameters
        ----------
        collider : CircleCollider
            Le CircleCollider dont on veut calculer l'AABB.

        Returns
        -------
        tuple
            L'AABB sous la forme (min_x, min_y, max_x, max_y
        """
        pos = collider.transform.position + parent_transform.position
        r = collider.radius
        return (pos.x - r, pos.y - r, pos.x + r, pos.y + r)

    @staticmethod
    def aabb_overlap(a: tuple, b: tuple) -> bool:
        """Vérifie si deux AABB se superposent."""
        a_min_x, a_min_y, a_max_x, a_max_y = a
        b_min_x, b_min_y, b_max_x, b_max_y = b
        return not (
            a_max_x < b_min_x
            or a_min_x > b_max_x
            or a_max_y < b_min_y
            or a_min_y > b_max_y
        )

    # --------------------
    # Collisions fines
    # --------------------
    @staticmethod
    def check_collision(c1: Collider, c2: Collider) -> bool:
        """
        Détecte la collision fine entre deux colliders.

        Parameters
        ----------
        c1 : Collider
            Le premier collider.
        c2 : Collider
            Le second collider.

        Returns
        -------
        bool
            True si les colliders sont en collision, False sinon.
        """
        # Circle / Circle
        if isinstance(c1, CircleCollider) and isinstance(c2, CircleCollider):
            c1_world_pos = c1.transform.position + c1.parent.transform.position
            c2_world_pos = c2.transform.position + c2.parent.transform.position

            delta = c1_world_pos - c2_world_pos
            radius_sum = c1.radius + c2.radius
            return delta.magnitude_squared() <= radius_sum**2

        # Box / Box : Séparation des axes (SAT)
        elif isinstance(c1, BoxCollider) and isinstance(c2, BoxCollider):
            return ColliderSystem._sat_collision(c1, c2)

        # Box / Circle
        elif isinstance(c1, BoxCollider) and isinstance(c2, CircleCollider):
            return ColliderSystem._circle_box_collision(c2, c1)
        elif isinstance(c1, CircleCollider) and isinstance(c2, BoxCollider):
            return ColliderSystem._circle_box_collision(c1, c2)

        else:
            raise TypeError("Type de collider non supporté pour collision fine")

    @staticmethod
    def _sat_collision(box1: BoxCollider, box2: BoxCollider) -> bool:
        """
        Collision Box/Box avec la méthode SAT (Séparation des axes).
        Pour cette méthode, on projette les coins des deux boîtes sur les normales
        de chaque boîte et on vérifie les chevauchements.

        Parameters
        ----------
        box1 : BoxCollider
            Le premier BoxCollider.
        box2 : BoxCollider
            Le second BoxCollider.

        Returns
        -------
        bool
            True si les boîtes sont en collision, False sinon.
        """
        corners1 = ColliderSystem.get_world_corners(box1.corners, box1.parent.transform)
        corners2 = ColliderSystem.get_world_corners(box2.corners, box2.parent.transform)

        # Obtenir les axes de projection (normales des arêtes)
        axes = Geometry.get_polygon_normals(corners1) + Geometry.get_polygon_normals(
            corners2
        )

        # Vérifier la projection sur chaque axe
        for axis in axes:
            min1, max1 = Geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = Geometry.project_polygon_on_axis(corners2, axis)

            # Séparation trouvée, pas de collision
            if not Geometry.intervals_overlap(min1, max1, min2, max2):
                return False

        # Aucune séparation trouvée, collision détectée
        return True

    @staticmethod
    def _circle_box_collision(circle: CircleCollider, box: BoxCollider) -> bool:
        """Collision Circle / Box."""
        circle_world_pos = circle.transform.position + circle.parent.transform.position
        closest = ColliderSystem.get_closest_point_on_box(box, circle_world_pos)
        delta = circle_world_pos - closest
        return delta.magnitude_squared() <= circle.radius**2

    @staticmethod
    def get_world_corners(corners: List[Vector2D], parent: Transform) -> list[Vector2D]:
        """
        Calcule les coins mondiaux d'un BoxCollider orienté.

        Parameters
        ----------
        corners : List[Vector2D]
            La liste des coins locaux d'un BoxCollider orienté.
        parent : Transform
            La transformation du GameObject parent.

        Returns
        -------
        list[Vector2D]
            La liste des coins mondiaux du BoxCollider.
        """
        world_corners = []

        for corner in corners:
            # rotation par le parent
            corner_rotated = parent.rotation.apply(corner)
            # translation locale

            world_corner = parent.position + corner_rotated

            world_corners.append(world_corner)
            # Appliquer rotation du parent

        return world_corners

    # TODO : Bouger dans geometry.py ?
    @staticmethod
    def get_closest_point_on_box(box: BoxCollider, point: Vector2D) -> Vector2D:
        """
        Trouve le point le plus proche sur un BoxCollider orienté
        à partir d'un point donné.

        La méthode :
            1. Passe le point dans le repère parent.
            2. Passe dans le repère local du BoxCollider.
            3. Clamp pour rester à l'intérieur du box.
            4. Reconvertit le point en coordonnées mondiales.

        Parameters
        ----------
        box : BoxCollider
            Le BoxCollider concerné.
        point : Vector2D
            Le point à partir duquel trouver le point le plus proche.

        Returns
        -------
        Vector2D
            Le point le plus proche sur le box en coordonnées mondiales.
        """
        parent_tr = box.parent.transform
        box_tr = box.transform

        # ----------------------------
        # On passe le point en coordonnées locales du parent
        # ----------------------------
        delta_to_parent = point - parent_tr.position
        point_local_parent = parent_tr.rotation.inverse().apply(delta_to_parent)

        # ----------------------------
        # On passe le point en coordonnées locales du box
        # ----------------------------
        point_relative_to_box = point_local_parent - box_tr.position
        point_local_box = box_tr.rotation.inverse().apply(point_relative_to_box)

        # ----------------------------
        # Clamp pour rester à l'intérieur du box
        # ----------------------------
        half_w = box.width / 2
        half_h = box.height / 2
        clamped_x = max(-half_w, min(half_w, point_local_box.x))
        clamped_y = max(-half_h, min(half_h, point_local_box.y))
        point_clamped_local_box = Vector2D(clamped_x, clamped_y)

        # ----------------------------
        # Repasser en coordonnées parent
        # ----------------------------
        point_in_parent_space = (
            box_tr.rotation.apply(point_clamped_local_box) + box_tr.position
        )

        # ----------------------------
        # Repasser en coordonnées mondiales
        # ----------------------------
        point_world = (
            parent_tr.rotation.apply(point_in_parent_space) + parent_tr.position
        )

        return point_world

    # --------------------
    # Détection globale
    # --------------------
    # TODO : optimiser avec spatial partitioning? (quadtrees, grilles, etc.)
    # TODO : gestion de on_enter et on_exit à mettre en place
    def detect_collisions(self) -> None:
        """
        Détecte les collisions entre tous les colliders enregistrés dans le système.
        Pour chaque paire de colliders, effectue une détection en deux étapes :
        1. Vérification rapide avec AABB.
        2. Détection fine si les AABB se chevauchent.

        En cas de collision détectée, appelle les méthodes on_collision ou on_trigger
        des GameObjects parents en fonction de la nature des colliders.
        """
        checked_pairs = set()

        for tag_mask, colliders in self.colliders.items():
            for c1 in colliders:
                for tag_mask2, colliders2 in self.colliders.items():
                    # Filtrage par tags (une seule fois par groupe)
                    if not TagSystem.can_collide(tag_mask, tag_mask2):
                        continue

                    # On ne se compare pas avec soi-même
                    for c2 in colliders2:
                        if c1 is c2:
                            continue

                        pair = (id(c1), id(c2))
                        reverse_pair = (id(c2), id(c1))
                        # Si déjà vérifié, on skip
                        if pair in checked_pairs or reverse_pair in checked_pairs:
                            continue
                        checked_pairs.add(pair)
                        checked_pairs.add(reverse_pair)

                        parent1 = c1.parent
                        parent2 = c2.parent

                        # AABB rapide
                        if not self.aabb_overlap(
                            self.compute_aabb(c1, parent1.transform),
                            self.compute_aabb(c2, parent2.transform),
                        ):
                            continue

                        # Collision fine
                        if not self.check_collision(c1, c2):
                            continue

                        # Collision détectée
                        if c1.solid and c2.solid:
                            parent1.on_collision(parent2)
                            parent2.on_collision(parent1)
                        # Trigger avec solide
                        elif not c1.solid and c2.solid:
                            parent1.on_trigger(parent2)
                        # Trigger avec solide
                        elif c1.solid and not c2.solid:
                            parent2.on_trigger(parent1)
