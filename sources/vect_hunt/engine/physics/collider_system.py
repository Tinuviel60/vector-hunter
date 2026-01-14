from typing import List, Set, Tuple, TYPE_CHECKING

from vect_hunt.engine.core.tag_system import TagSystem
from vect_hunt.engine.core import Geometry
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform
from .collider import Collider, BoxCollider, CircleCollider
from vect_hunt.engine.components.collider_component import ColliderComponent

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject
    from vect_hunt.engine.worlds import World


class ColliderSystem:
    """
    Système global de collision pour un ensemble de colliders.

    - Interroge les GameObjects du World pour trouver ceux avec des ColliderComponents.
    - Calcule les AABB et collisions entre eux.
    - Utilise le système de tags pour filtrer les paires de collision.
    """

    def __init__(self):
        """Initialise le système de collision."""
        pass  # Plus besoin de maintenir une liste de colliders

    # --------------------
    # AABB Mondial
    # --------------------
    @staticmethod
    def compute_aabb(collider: Collider, parent_transform: Transform) -> tuple:
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
        assert collider.parent is not None, "Collider must have a parent GameObject"
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
            assert c1.parent is not None, "c1 must have a parent"
            assert c2.parent is not None, "c2 must have a parent"
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
        assert box1.parent is not None, "box1 must have a parent"
        assert box2.parent is not None, "box2 must have a parent"
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
        assert circle.parent is not None, "circle must have a parent"
        assert box.parent is not None, "box must have a parent"
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
        assert box.parent is not None, "box must have a parent"
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
    def detect_collisions(
        self, world: "World"
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Détecte les collisions entre tous les GameObjects du monde
        ayant des ColliderComponents.

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
        # Récupérer tous les GameObjects actifs avec des ColliderComponents
        collidable_objects: List["GameObject"] = []
        for game_object in world.game_objects.values():
            if not game_object.active:
                continue
            if game_object.get_component(
                ColliderComponent
            ):  # Property qui retourne colliders du ColliderComponent
                collidable_objects.append(game_object)

        current_collisions: Set[Tuple[int, int]] = set()
        current_triggers: Set[Tuple[int, int]] = set()

        # Réinitialiser le compteur de collisions debug
        for game_object in collidable_objects:
            collider_comp = game_object.get_component(ColliderComponent)
            if collider_comp:
                collider_comp.nb_collision = 0
        
        # Tester toutes les paires de GameObjects
        for i, obj1 in enumerate(collidable_objects):
            next_i = i + 1
            for obj2 in collidable_objects[next_i:]:
                collider_component1 = obj1.get_component(ColliderComponent)
                collider_component2 = obj2.get_component(ColliderComponent)

                # Filtrage par tags
                if not TagSystem.can_collide(obj1.tags, obj2.tags):
                    continue

                # Tester tous les colliders de obj1 contre tous les colliders de obj2
                assert collider_component1 is not None
                assert collider_component2 is not None
                for c1 in collider_component1.colliders:
                    for c2 in collider_component2.colliders:
                        # AABB rapide (broad phase)
                        if not self.aabb_overlap(
                            self.compute_aabb(c1, obj1.transform),
                            self.compute_aabb(c2, obj2.transform),
                        ):
                            continue

                        # Collision fine (narrow phase)
                        if not self.check_collision(c1, c2):
                            continue

                        # Collision détectée - enregistrer une seule paire d'objets
                        pair = (obj1.id, obj2.id)
                        if c1.solid and c2.solid:
                            current_collisions.add(pair)
                            # Incrémenter le compteur debug pour les deux objets
                            collider_component1.nb_collision += 1
                            collider_component2.nb_collision += 1
                        else:
                            # Au moins un des deux est un trigger
                            current_triggers.add(pair)

                        # Pas besoin de tester les autres colliders pour cette paire
                        break
                    else:
                        # Continue si pas de collision détectée avec c1
                        continue
                    # Break du for c2 si collision détectée
                    break

        return current_collisions, current_triggers
