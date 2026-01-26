from typing import TYPE_CHECKING, List, Set, Tuple

from vect_hunt.engine.components.collider.box_collider_component import (
    BoxColliderComponent,
)
from vect_hunt.engine.components.collider.circle_collider_component import (
    CircleColliderComponent,
)
from vect_hunt.engine.components.collider.collider_component import ColliderComponent
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.geometry import Geometry
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.tag_system import TagSystem
from vect_hunt.engine.core.transform.rotation import Rotation
from vect_hunt.engine.core.transform.transform import Transform
from vect_hunt.engine.physics.collision_info import CollisionInfo

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.scenes.scene import Scene


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
    """

    def __init__(self, tag_system: TagSystem):
        """
        Initialise le système de collision.

        Parameters
        ----------
        tag_system : TagSystem
            Systeme de tags a utiliser pour filtrer les collisions.
        """
        self._tag_system = tag_system

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
        return Geometry.aabb_overlap(a_min, a_max, b_min, b_max)

    # --------------------
    # Collisions fines
    # --------------------
    @staticmethod
    def check_collision(
        c1: ColliderComponent, c2: ColliderComponent
    ) -> CollisionInfo | None:
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
        CollisionInfo | None
            Les informations de collision (normal, depth, point, etc.) si collision,
            sinon None.
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
                c2, c1, reverse_result=False
            )
        elif isinstance(c1, CircleColliderComponent) and isinstance(
            c2, BoxColliderComponent
        ):
            return ColliderSystem._circle_box_collision_info(c1, c2, reverse_result=True)
        else:
            raise TypeError("Type de collider non supporté pour collision fine")

    @staticmethod
    def _circle_circle_collision_info(
        c1: CircleColliderComponent, c2: CircleColliderComponent
    ) -> CollisionInfo | None:
        """
        Détecte et retourne les informations de collision entre deux cercles.

        Parameters
        ----------
        c1 : CircleCollider
            Premier cercle.
        c2 : CircleCollider
            Second cercle.


        -------
        CollisionInfo or None
            Informations de collision (normal, depth, points) si collision, sinon None.
        """
        c1_scene_pos = c1.get_scene_transform().position
        c2_scene_pos = c2.get_scene_transform().position
        return Geometry.circle_circle_collision_info(
            c1_scene_pos,
            c1.shape.radius,
            c2_scene_pos,
            c2.shape.radius
        )

    @staticmethod
    def _sat_collision_info(
        box1: BoxColliderComponent, box2: BoxColliderComponent
    ) -> CollisionInfo | None:
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
        CollisionInfo or None
            Informations de collision (normal, depth) si collision, sinon None.
        """
        # SAT avec calcul de la plus petite séparation

        corners1 = box1.get_scene_corners()
        corners2 = box2.get_scene_corners()
        return Geometry.sat_collision_info(corners1, corners2)

    @staticmethod
    def _circle_box_collision_info(
        circle: CircleColliderComponent,
        box: BoxColliderComponent,
        reverse_result: bool = False,
    ) -> CollisionInfo | None:
        """
        Détecte et retourne les informations de collision entre un cercle et un box.

        Parameters
        ----------
        circle : CircleCollider
            Le cercle.
        box : BoxCollider
            Le box.
        reverse_result : bool, optional
            Indique si les informations de collision doivent être inversées,
            pour preserver la convention normal allant de c1 vers c2.
            Par défaut False.

        Returns
        -------
        CollisionInfo or None
            Informations de collision (normal, depth, points) si collision, sinon None.
        """
        circle_scene_pos = circle.get_scene_transform().position
        box_scene_tr = box.get_scene_transform()
        box_shape = box.shape

        collision_info = Geometry.circle_box_collision_info(
            circle_scene_pos,
            circle.shape.radius,
            box_scene_tr,
            box_shape
        )
        if collision_info is not None and reverse_result:
            # Inverser la normale
            collision_info.normal = -collision_info.normal
        
        return collision_info

    # --------------------
    # Détection globale
    # --------------------
    def detect_collisions(
        self, scene: "Scene"
    ) -> Tuple[
        Set[Tuple[int, int]], Set[Tuple[int, int]], dict[Tuple[int, int], CollisionInfo]
    ]:
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
        collision_info: dict[Tuple[int, int], CollisionInfo] = {}

        # Tester toutes les paires de GameObjects
        for i, obj1 in enumerate(collidable_objects):
            next_i = i + 1
            for obj2 in collidable_objects[next_i:]:
                colliders1 = colliders_by_object[obj1.id]
                colliders2 = colliders_by_object[obj2.id]

                # Filtrage par tags
                if not self._tag_system.can_collide(obj1.tags, obj2.tags):
                    continue

                # Tester tous les colliders de obj1 contre tous les colliders de obj2
                for c1 in colliders1:
                    for c2 in colliders2:
                        # AABB rapide (broad phase)
                        if not self.aabb_overlap(
                            c1.get_scene_aabb(),
                            c2.get_scene_aabb(),
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
