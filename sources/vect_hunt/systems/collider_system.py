from typing import List

from .tag_system import TagSystem

from vect_hunt.core import *
from vect_hunt.objects import GameObject

import math


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
        Met à jour l'affectation des colliders d'un objet de jeu en fonction de ses tags.

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
    def compute_aabb(collider: Collider):
        """
        Calcule l'AABB mondial du collider.

        Pour CircleCollider : centre ± rayon
        Pour BoxCollider : calcule coins mondiaux
        """
        if isinstance(collider, CircleCollider):
            return ColliderSystem._compute_aabb_circle(collider)
        elif isinstance(collider, BoxCollider):
            return ColliderSystem._compute_aabb_box(collider)
        else:
            raise TypeError("Collider inconnu pour calcul AABB")

    @staticmethod
    def _compute_aabb_box(collider: BoxCollider):
        """
        Calcule l'AABB mondial d'un BoxCollider.

        Parameters
        ----------
        collider : BoxCollider
            Le BoxCollider dont on veut calculer l'AABB.

        Returns
        -------
        tuple
            L'AABB sous la forme (min_x, min_y, max_x, max_y
        """
        xs = [c.x for c in collider.corners]
        ys = [c.y for c in collider.corners]
        return (min(xs), min(ys), max(xs), max(ys))

    @staticmethod
    def _compute_aabb_circle(collider: CircleCollider):
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
        pos = collider.transform.position
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
            delta = c1.transform.position - c2.transform.position
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
        corners1 = box1.corners
        corners2 = box2.corners

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
        closest = ColliderSystem.get_closest_point_on_box(
            box, circle.transform.position
        )
        delta = circle.transform.position - closest
        return delta.magnitude_squared() <= circle.radius**2

    # TODO : Bouger dans geometry.py ?
    @staticmethod
    def get_closest_point_on_box(box: BoxCollider, point: Vector2D) -> Vector2D:
        """
        Trouve le point le plus proche sur un BoxCollider orienté
        à partir d'un point donné.

        Cette fonction transforme le point dans le repère local du box, trouve le
        point le plus proche dans ce repère, puis le retransforme dans le repère global.
        Utilisée pour la détection de collision Circle-Box.

        Parameters
        ----------
        point : Vector2D
            Le point à partir duquel trouver le point le plus proche.

        Returns
        -------
        Vector2D
            Le point le plus proche sur le box.
        """
        # Transforme le point dans le repère local du box
        local_x = point.x - box.transform.position.x
        local_y = point.y - box.transform.position.y

        # Rotation inverse pour passer dans le repère du box
        cos_angle = math.cos(-box.transform.rotation)
        sin_angle = math.sin(-box.transform.rotation)

        rotated_x = local_x * cos_angle - local_y * sin_angle
        rotated_y = local_x * sin_angle + local_y * cos_angle

        # Clamp aux limites du box
        half_width = box.width / 2
        half_height = box.height / 2

        clamped_x = max(-half_width, min(half_width, rotated_x))
        clamped_y = max(-half_height, min(half_height, rotated_y))

        # Rotation directe pour revenir au repère global
        cos_angle = math.cos(box.transform.rotation)
        sin_angle = math.sin(box.transform.rotation)

        world_x = (
            clamped_x * cos_angle - clamped_y * sin_angle + box.transform.position.x
        )
        world_y = (
            clamped_x * sin_angle + clamped_y * cos_angle + box.transform.position.y
        )
        return Vector2D(world_x, world_y)

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

                        # AABB rapide
                        if not self.aabb_overlap(
                            self.compute_aabb(c1),
                            self.compute_aabb(c2),
                        ):
                            continue

                        # Collision fine
                        if not self.check_collision(c1, c2):
                            continue

                        parent1 = c1.parent
                        parent2 = c2.parent

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
