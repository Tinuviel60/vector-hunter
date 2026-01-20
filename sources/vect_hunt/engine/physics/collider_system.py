from typing import List, Set, Tuple, TYPE_CHECKING

from vect_hunt.engine.core.tag_system import TagSystem
from vect_hunt.engine.core import Geometry
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Rotation, Transform
from vect_hunt.engine.components.collider import (
    BoxColliderComponent,
    CircleColliderComponent,
    ColliderComponent,
)

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject
    from vect_hunt.engine.scenes import Scene


class ColliderSystem:
    """
    Système global de collision pour un ensemble de colliders.

    - Interroge les GameObjects de la scène pour trouver ceux avec des Colliders.
    - Calcule les AABB et collisions entre eux.
    - Utilise le système de tags pour filtrer les paires de collision.

    Attributes
    ----------
    physic_config : dict
        Configuration physique chargée depuis les assets.
    min_penetration_depth : float
        Profondeur minimale de pénétration pour valider une collision.
    """

    # TODO : Charger depuis la config de la scène ?
    # physic_config = DataLoader.load_json("configs/units.json")
    min_penetration_depth = 1e-9

    def __init__(self):
        """Initialise le système de collision."""

    @staticmethod
    def aabb_overlap(
        a: tuple[Vector2D, Vector2D], b: tuple[Vector2D, Vector2D]
    ) -> bool:
        """Vérifie si deux AABB se superposent.

        Parameters
        ----------
        a : tuple[Vector2D, Vector2D]
            AABB 1 (min, max).
        b : tuple[Vector2D, Vector2D]
            AABB 2 (min, max).

        Returns
        -------
        bool
            True si les AABB se superposent, False sinon.
        """
        a_min, a_max = a
        b_min, b_max = b

        return Geometry.intervals_overlap(
            a_min.x, a_max.x, b_min.x, b_max.x
        ) and Geometry.intervals_overlap(a_min.y, a_max.y, b_min.y, b_max.y)

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
    def get_collider_scene_transform(collider: ColliderComponent) -> Transform:
        """
        Retourne la transform monde du collider (position + rotation),
        en composant Transform du GameObject et Transform local du collider.

        Parameters
        ----------
        collider : ColliderComponent
            Le collider dont on veut la transform monde.

        Returns
        -------
        Transform
            La transform monde du collider.
        """
        scene_tr = Transform(ColliderSystem._get_collider_scene_position(collider))
        scene_tr.rotation = ColliderSystem._get_collider_scene_rotation(collider)

        return scene_tr

    @staticmethod
    def collider_scene_to_local(
        collider: ColliderComponent, scene_point: Vector2D
    ) -> Vector2D:
        """
        Convertit un point scene en coordonnées LOCALES du collider.
        Dans ce repère, la shape est centrée en (0,0) et non-rotée.

        Parameters
        ----------
        collider : ColliderComponent
            Le collider de référence.
        world_point : Vector2D
            Le point en coordonnées mondiales.

        Returns
        -------
        Vector2D
            Le point en coordonnées locales du collider.
        """
        wt = ColliderSystem.get_collider_scene_transform(collider)
        return wt.rotation.inverse().apply(scene_point - wt.position)

    @staticmethod
    def collider_local_to_scene(
        collider: ColliderComponent, local_point: Vector2D
    ) -> Vector2D:
        """
        Convertit un point du repère local collider en scene.

        Parameters
        ----------
        collider : ColliderComponent
            Le collider de référence.
        local_point : Vector2D
            Le point en coordonnées locales du collider.

        Returns
        -------
        Vector2D
            Le point en coordonnées mondiales.
        """
        wt = ColliderSystem.get_collider_scene_transform(collider)
        return wt.position + wt.rotation.apply(local_point)

    @staticmethod
    def _get_collider_scene_position(collider: ColliderComponent) -> Vector2D:
        """
        Calcule la position mondiale du centre du ColliderComponent :
        - Applique la rotation du parent à la position locale du collider (offset)
        - Ajoute la position du parent
        La rotation locale du collider n'affecte pas la position de son centre.

        Parameters
        ----------
        collider : ColliderComponent
            Le ColliderComponent dont on veut la position mondiale.

        Returns
        -------
        Vector2D
            La position mondiale du centre du ColliderComponent.
        """
        assert collider.game_object is not None
        parent_tr = collider.game_object.transform

        local_offset = collider.transform.position
        rotated_offset = parent_tr.rotation.apply(local_offset)

        world_pos = parent_tr.position + rotated_offset
        return world_pos

    @staticmethod
    def _get_collider_scene_rotation(collider: ColliderComponent) -> Rotation:
        """
        Calcule la rotation mondiale d'un ColliderComponent, en tenant compte
        de la rotation locale du collider et de la rotation du GameObject parent.

        Parameters
        ----------
        collider : ColliderComponent
            Le ColliderComponent dont on veut la rotation mondiale.

        Returns
        -------
        Rotation
            La rotation mondiale du ColliderComponent.
        """
        assert collider.game_object is not None
        parent_tr = collider.game_object.transform
        local_rot = collider.transform.rotation
        # On suppose que la méthode compose existe sur Rotation
        return parent_tr.rotation.compose(local_rot)

    @staticmethod
    def _circle_circle_collision_info(
        c1: CircleColliderComponent, c2: CircleColliderComponent
    ) -> dict | None:
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

        c1_scene_pos = ColliderSystem._get_collider_scene_position(c1)
        c2_scene_pos = ColliderSystem._get_collider_scene_position(c2)

        delta = c1_scene_pos - c2_scene_pos
        dist = delta.magnitude()
        radius_sum = c1.shape.radius + c2.shape.radius

        if dist < radius_sum:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            penetration = radius_sum - dist

            if penetration < ColliderSystem.min_penetration_depth:
                return None

            return {
                "normal": normal,
                "depth": penetration,
                "point": c2_scene_pos + normal * c2.shape.radius,
            }
        return None

    @staticmethod
    def _sat_collision_info(
        box1: BoxColliderComponent, box2: BoxColliderComponent
    ) -> dict | None:
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

        corners1 = ColliderSystem.get_scene_corners(box1)
        corners2 = ColliderSystem.get_scene_corners(box2)
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
    ) -> dict | None:
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
        circle_scene_pos = ColliderSystem._get_collider_scene_position(circle)

        closest = ColliderSystem.get_closest_point_on_box(box, circle_scene_pos)
        delta = circle_scene_pos - closest
        dist = delta.magnitude()

        if dist < circle.shape.radius:
            normal = delta.normalized() if dist != 0 else Vector2D(1, 0)
            if reverse_normal:
                normal = -1 * normal
            penetration = circle.shape.radius - dist
            if penetration < ColliderSystem.min_penetration_depth:
                return None

            return {"normal": normal, "depth": penetration, "point": closest}
        return None

    @staticmethod
    def get_scene_corners(box: BoxColliderComponent) -> list[Vector2D]:
        """
        Calcule les coins mondiaux d'un BoxCollider orienté.

        Parameters
        ----------
        box : BoxCollider
            Le BoxCollider dont on veut les coins mondiaux.

        Returns
        -------
        list[Vector2D]
            La liste des coins mondiaux du BoxCollider.
        """
        assert box.game_object is not None, "box must have a game_object"

        scene_position = ColliderSystem._get_collider_scene_position(box)
        scene_rotation = ColliderSystem._get_collider_scene_rotation(box)

        local_corners = box.shape.local_vertices()
        assert local_corners is not None, "BoxShape must provide local vertices"

        scene_corners = [
            scene_rotation.apply(corner) + scene_position for corner in local_corners
        ]
        return scene_corners

    @staticmethod
    def get_closest_point_on_box(
        box: BoxColliderComponent, point: Vector2D
    ) -> Vector2D:
        """
        Trouve le point le plus proche sur le BoxCollider d'un point donné en monde.

        La méthode :
        1. Convertit le point monde en coordonnées locales du box.
        2. Utilise la méthode closest_point_local de la shape box.
        3. Convertit le point local le plus proche en coordonnées monde.

        Parameters
        ----------
        box : BoxCollider
            Le BoxCollider de référence.
        point : Vector2D
            Le point en coordonnées mondiales.
        """
        point_local = ColliderSystem.collider_scene_to_local(box, point)
        closest_local = box.shape.closest_point_local(point_local)

        return ColliderSystem.collider_local_to_scene(box, closest_local)

    def compute_aabb(self, collider: ColliderComponent) -> tuple[Vector2D, Vector2D]:
        """
        Calcule l'AABB monde d'un collider.

        Returns
        -------
        tuple[Vector2D, Vector2D]
            (min, max) de l'AABB monde du collider.
        """

        center = self._get_collider_scene_position(collider)
        local_min, local_max = collider.shape.aabb_local()

        # Cercle: rotation inutile, AABB directe
        if isinstance(collider, CircleColliderComponent):
            scene_aabb = (local_min + center, local_max + center)
            return scene_aabb
        # Box: calcul des coins monde
        elif isinstance(collider, BoxColliderComponent):
            scene_corners = ColliderSystem.get_scene_corners(collider)

            xs = [p.x for p in scene_corners]
            ys = [p.y for p in scene_corners]
            return Vector2D(min(xs), min(ys)), Vector2D(max(xs), max(ys))
        else:
            raise TypeError("Type de collider non supporté pour AABB monde")

    # --------------------
    # Détection globale
    # --------------------
    def detect_collisions(
        self, scene: "Scene"
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]], dict]:
        """
        Detecte les collisions entre tous les GameObjects de la scène
        ayant des colliders.

        Pour chaque paire de GameObjects :
        1. Vérifie si leurs tags permettent une collision (via TagSystem).
        2. Teste les AABB de tous leurs colliders (broad phase).
        3. Si AABB se chevauchent, effectue une détection fine (narrow phase).

        Parameters
        ----------
        scene : Scene
            La scène contenant les GameObjects à tester.

        Returns
        -------
        Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]
            Un tuple contenant (collisions, triggers) où chaque élément est un
            ensemble de paires (id_obj1, id_obj2) des GameObjects en interaction.
        """
        # Recuperer tous les GameObjects actifs avec des colliders
        collidable_objects: List["GameObject"] = []
        colliders_by_object: dict[int, list[ColliderComponent]] = {}
        for game_object in scene.game_objects.values():
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
                collider.nb_collision = 0  # TODO : Voir si toujours utile

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
                            self.compute_aabb(c1),
                            self.compute_aabb(c2),
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
                    # TODO : A documenter ou a revoir pour selections de la
                    # TODO : meilleur collision? All collision?
                    # Break du for c2 si collision détectée
                    break

        return current_collisions, current_triggers, collision_info
