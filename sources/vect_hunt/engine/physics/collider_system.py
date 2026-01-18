from typing import List, Set, Tuple, TYPE_CHECKING

from vect_hunt.engine.core.tag_system import TagSystem
from vect_hunt.engine.core import Geometry
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform
from vect_hunt.engine.components.collider import (
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderComponent,
)
from vect_hunt.engine.resources.loaders.data_loader import DataLoader

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject
    from vect_hunt.engine.worlds import World


class ColliderSystem:
    """
    Système global de collision pour un ensemble de colliders.

    - Interroge les GameObjects du World pour trouver ceux avec des Colliders.
    - Calcule les AABB et collisions entre eux.
    - Utilise le système de tags pour filtrer les paires de collision.

    Attributes
    ----------
    physic_config : dict
        Configuration physique chargée depuis les assets.
    min_penetration_depth : float
        Profondeur minimale de pénétration pour valider une collision.
    """

    physic_config = DataLoader.load_json("configs/game.json")["physics"]
    min_penetration_depth = physic_config["min_penetration_depth"]

    def __init__(self):
        """Initialise le système de collision."""

    # --------------------
    # AABB Mondial
    # --------------------
    @staticmethod
    def compute_aabb(collider: ColliderComponent, parent_transform: Transform) -> tuple:
        """
        Calcule l'AABB mondial du collider.

        Pour CircleCollider : centre ± rayon
        Pour BoxCollider : calcule coins mondiaux

        Parameters
        ----------
        collider : Collider
            Le collider dont on veut calculer l'AABB.
        parent_transform : Transform
            La transformation du GameObject parent.

        Returns
        -------
        tuple
            L'AABB sous la forme (min_x, min_y, max_x, max_y).
        """
        assert (
            collider.game_object is not None
        ), "Collider must have a parent GameObject"
        if isinstance(collider, CircleColliderComponent):
            return ColliderSystem._compute_aabb_circle(collider, parent_transform)
        elif isinstance(collider, BoxColliderComponent):
            return ColliderSystem._compute_aabb_box(collider, parent_transform)
        else:
            raise TypeError("Collider inconnu pour calcul AABB")

    @staticmethod
    def _compute_aabb_box(collider: BoxColliderComponent, parent_transform: Transform):
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
    def _compute_aabb_circle(
        collider: CircleColliderComponent, parent_transform: Transform
    ):
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
    def check_collision(c1: ColliderComponent, c2: ColliderComponent) -> dict | None:
        """
        Détecte la collision fine entre deux colliders et retourne un dictionnaire
        d'information ou None.

        Parameters
        ----------
        c1 : Collider
            Le premier collider.
        c2 : Collider
            Le second collider.

        Returns
        -------
        dict | None
            Un dictionnaire d'information de collision (normal, depth, point, etc.)
            si collision, sinon None.
        """
        # Circle / Circle
        if isinstance(c1, CircleColliderComponent) and isinstance(
            c2, CircleColliderComponent
        ):
            return ColliderSystem._circle_circle_collision_info(c1, c2)
        elif isinstance(c1, BoxColliderComponent) and isinstance(
            c2, BoxColliderComponent
        ):
            return ColliderSystem._sat_collision_info(c1, c2)
        elif isinstance(c1, BoxColliderComponent) and isinstance(
            c2, CircleColliderComponent
        ):
            return ColliderSystem._circle_box_collision_info(
                c2, c1, reverse_normal=True
            )
        elif isinstance(c1, CircleColliderComponent) and isinstance(
            c2, BoxColliderComponent
        ):
            return ColliderSystem._circle_box_collision_info(c1, c2)
        else:
            raise TypeError("Type de collider non supporté pour collision fine")

    @staticmethod
    def _circle_circle_collision_info(
        c1: CircleColliderComponent, c2: CircleColliderComponent
    ):
        """
        Détecte et retourne les informations de collision entre deux cercles.

        Parameters
        ----------
        c1 : CircleCollider
            Premier cercle.
        c2 : CircleCollider
            Second cercle.

        Returns
        -------
        dict or None
            Dictionnaire d'information (normal, depth, point) si collision, sinon None.
        """
        assert c1.game_object is not None
        assert c2.game_object is not None

        c1_world_pos = c1.transform.position + c1.game_object.transform.position
        c2_world_pos = c2.transform.position + c2.game_object.transform.position

        delta = c1_world_pos - c2_world_pos
        dist = delta.magnitude()
        radius_sum = c1.radius + c2.radius

        if dist < radius_sum:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            penetration = radius_sum - dist

            if penetration < ColliderSystem.min_penetration_depth:
                return None

            return {
                "normal": normal,
                "depth": penetration,
                "point": c2_world_pos + normal * c2.radius,
            }
        return None

    @staticmethod
    def _sat_collision_info(box1: BoxColliderComponent, box2: BoxColliderComponent):
        """
        Détecte et retourne les informations de collision
        entre deux BoxCollider (méthode SAT).

        Parameters
        ----------
        box1 : BoxCollider
            Premier box.
        box2 : BoxCollider
            Second box.

        Returns
        -------
        dict or None
            Dictionnaire d'information (normal, depth) si collision, sinon None.
        """
        # SAT avec calcul de la plus petite séparation
        assert box1.game_object is not None
        assert box2.game_object is not None

        corners1 = ColliderSystem.get_world_corners(
            box1.corners, box1.game_object.transform
        )
        corners2 = ColliderSystem.get_world_corners(
            box2.corners, box2.game_object.transform
        )
        axes = Geometry.get_polygon_normals(corners1) + Geometry.get_polygon_normals(
            corners2
        )
        penetration = float("inf")
        smallest_axis = None

        for axis in axes:
            min1, max1 = Geometry.project_polygon_on_axis(corners1, axis)
            min2, max2 = Geometry.project_polygon_on_axis(corners2, axis)
            if not Geometry.intervals_overlap(min1, max1, min2, max2):
                return None

            overlap = min(max1, max2) - max(min1, min2)
            if overlap < penetration:
                penetration = overlap
                smallest_axis = axis

        if penetration < ColliderSystem.min_penetration_depth:
            return None

        if smallest_axis is None:
            return None

        # Normale unitaire (mais direction arbitraire à ce stade)
        normal = smallest_axis.normalized()

        # Calcul des centres (moyenne des corners)
        center1 = Vector2D(
            sum(c.x for c in corners1) / len(corners1),
            sum(c.y for c in corners1) / len(corners1),
        )
        center2 = Vector2D(
            sum(c.x for c in corners2) / len(corners2),
            sum(c.y for c in corners2) / len(corners2),
        )

        # Orientation déterministe : normal doit pointer de box2 vers box1
        direction = center1 - center2
        if direction.dot(normal) < 0:
            normal = -1 * normal

        return {"normal": normal, "depth": penetration}

    @staticmethod
    def _circle_box_collision_info(
        circle: CircleColliderComponent,
        box: BoxColliderComponent,
        reverse_normal: bool = False,
    ):
        """
        Détecte et retourne les informations de collision entre un cercle et un box.

        Parameters
        ----------
        circle : CircleCollider
            Le cercle.
        box : BoxCollider
            Le box.
        reverse_normal : bool, optional
            Indique si la normale doit être inversée,
            si l'ordre des paramètres est inversé.
            Par défaut False.

        Returns
        -------
        dict or None
            Dictionnaire d'information (normal, depth, point) si collision, sinon None.
        """
        assert circle.game_object is not None
        assert box.game_object is not None

        circle_world_pos = (
            circle.transform.position + circle.game_object.transform.position
        )
        closest = ColliderSystem.get_closest_point_on_box(box, circle_world_pos)
        delta = circle_world_pos - closest
        dist = delta.magnitude()

        if dist < circle.radius:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            if reverse_normal:
                normal = -1 * normal
            penetration = circle.radius - dist

            if penetration < ColliderSystem.min_penetration_depth:
                return None

            return {"normal": normal, "depth": penetration, "point": closest}
        return None

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

    @staticmethod
    def get_closest_point_on_box(
        box: BoxColliderComponent, point: Vector2D
    ) -> Vector2D:
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
        assert box.game_object is not None, "box must have a game_object"
        parent_tr = box.game_object.transform
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
    def detect_collisions(
        self, world: "World"
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]], dict]:
        """
        Detecte les collisions entre tous les GameObjects du monde
        ayant des colliders.

        Pour chaque paire de GameObjects :
        1. Vérifie si leurs tags permettent une collision (via TagSystem).
        2. Teste les AABB de tous leurs colliders (broad phase).
        3. Si AABB se chevauchent, effectue une détection fine (narrow phase).

        Parameters
        ----------
        world : World
            Le monde contenant les GameObjects à tester.

        Returns
        -------
        Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]
            Un tuple contenant (collisions, triggers) où chaque élément est un
            ensemble de paires (id_obj1, id_obj2) des GameObjects en interaction.
        """
        # Recuperer tous les GameObjects actifs avec des colliders
        collidable_objects: List["GameObject"] = []
        colliders_by_object: dict[int, list[ColliderComponent]] = {}
        for game_object in world.game_objects.values():
            if not game_object.active:
                continue
            colliders = game_object.get_components(ColliderComponent)
            if colliders:
                collidable_objects.append(game_object)
                colliders_by_object[game_object.id] = colliders

        current_collisions: Set[Tuple[int, int]] = set()
        current_triggers: Set[Tuple[int, int]] = set()
        collision_info: dict = {}

        # Reinitialiser le compteur de collisions debug
        for game_object in collidable_objects:
            for collider in colliders_by_object[game_object.id]:
                collider.nb_collision = 0

        # Tester toutes les paires de GameObjects
        for i, obj1 in enumerate(collidable_objects):
            next_i = i + 1
            for obj2 in collidable_objects[next_i:]:
                colliders1 = colliders_by_object[obj1.id]
                colliders2 = colliders_by_object[obj2.id]

                # Filtrage par tags
                if not TagSystem.can_collide(obj1.tags, obj2.tags):
                    continue

                # Tester tous les colliders de obj1 contre tous les colliders de obj2
                for c1 in colliders1:
                    for c2 in colliders2:
                        # AABB rapide (broad phase)
                        if not self.aabb_overlap(
                            self.compute_aabb(c1, obj1.transform),
                            self.compute_aabb(c2, obj2.transform),
                        ):
                            continue

                        # Collision fine (narrow phase)
                        info = self.check_collision(c1, c2)
                        if info is None:
                            continue

                        pair = (obj1.id, obj2.id)
                        if c1.solid and c2.solid:
                            current_collisions.add(pair)
                            collision_info[pair] = info
                            c1.nb_collision += 1
                            c2.nb_collision += 1
                        else:
                            # Au moins un des deux est un trigger
                            current_triggers.add(pair)

                        break
                    else:
                        # Continue si pas de collision détectée avec c1
                        continue
                    # Break du for c2 si collision détectée
                    break

        return current_collisions, current_triggers, collision_info
