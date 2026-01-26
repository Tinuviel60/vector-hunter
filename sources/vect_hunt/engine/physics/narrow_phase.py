from vect_hunt.engine.components.collider.box_collider_component import (
    BoxColliderComponent,
)
from vect_hunt.engine.components.collider.circle_collider_component import (
    CircleColliderComponent,
)
from vect_hunt.engine.components.collider.collider_component import ColliderComponent
from vect_hunt.engine.core.collisions.collision import Collision
from vect_hunt.engine.core.collisions.collision_info import CollisionInfo


class NarrowPhase:
    """
    Réalise la narrow phase : tests géométriques précis et génération de CollisionInfo.

    Cette classe doit rester la plus pure possible :
    - pas de dépendance à Scene
    - pas de logique de pipeline
    - seulement du "collision test" entre deux colliders.
    """

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
            return NarrowPhase._circle_circle_collision_info(c1, c2)
        elif isinstance(c1, BoxColliderComponent) and isinstance(
            c2, BoxColliderComponent
        ):
            return NarrowPhase._sat_collision_info(c1, c2)
        elif isinstance(c1, BoxColliderComponent) and isinstance(
            c2, CircleColliderComponent
        ):
            return NarrowPhase._circle_box_collision_info(c2, c1, reverse_result=False)
        elif isinstance(c1, CircleColliderComponent) and isinstance(
            c2, BoxColliderComponent
        ):
            return NarrowPhase._circle_box_collision_info(c1, c2, reverse_result=True)
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
        return Collision.circle_circle_collision_info(
            c1_scene_pos, c1.shape.radius, c2_scene_pos, c2.shape.radius
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
        return Collision.sat_collision_info(corners1, corners2)

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

        collision_info = Collision.circle_box_collision_info(
            circle_scene_pos, circle.shape.radius, box_scene_tr, box_shape
        )
        if collision_info is not None and reverse_result:
            # Inverser la normale
            collision_info.normal = -collision_info.normal

        return collision_info
