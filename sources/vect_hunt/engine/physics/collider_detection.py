from typing import Dict, List, Set, Tuple, cast, TYPE_CHECKING

from vect_hunt.engine.core.collisions.collision_result import CollisionResult
from vect_hunt.engine.physics.broad_phase import BroadPhase
from vect_hunt.engine.physics.narrow_phase import NarrowPhase

if TYPE_CHECKING:
    from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
    from vect_hunt.engine.components.collider.collider_component import ColliderComponent
    from vect_hunt.engine.core.collisions.collision_info import CollisionInfo
    from vect_hunt.engine.core.tag_system import TagSystem
    from vect_hunt.engine.scenes.scene import Scene

class ColliderDetection:
    """
    Point d'entrée du pipeline de détection.

    Orchestration :
    - récupère les colliders de la Scene
    - broad phase : génère les paires candidates
    - narrow phase : calcule CollisionInfo
    - classe en "collisions" vs "triggers"
    """

    def __init__(self, tag_system: "TagSystem") -> None:
        """
        Initialise le pipeline de détection avec ses étapes.

        Parameters
        ----------
        tag_system : "TagSystem"
            Système de tags pour la gestion des collisions.
        """
        self._broad_phase = BroadPhase()
        self._narrow_phase = NarrowPhase()

        self._tag_system = tag_system

    def detect(self, scene: "Scene") -> CollisionResult:
        """
        Exécute le pipeline de détection des collisions sur une scène.

        Parameters
        ----------
        scene : "Scene"
            Scène contenant les GameObjects / composants.

        Returns
        -------
        CollisionResult
            Résultat structuré (collisions, triggers, collision_info).
        """
        colliders = self._collect_colliders(scene)

        candidates = self._broad_phase.compute_candidate_pairs(colliders)
        candidates_can_collide = self._candidates_can_collide(candidates)

        collisions: Set[Tuple[int, int]] = set()
        triggers: Set[Tuple[int, int]] = set()
        collision_info: Dict[Tuple[int, int], "CollisionInfo"] = {}

        sleep_cache: Dict[int, bool] = {}
        for collider_a, collider_b in candidates_can_collide:
            parent_id_a = collider_a.parent.id
            parent_id_b = collider_b.parent.id
            if parent_id_a == parent_id_b:
                continue  # Ignorer les auto-collisions du même objet

            id_a = collider_a.id
            id_b = collider_b.id
            pair = (min(id_a, id_b), max(id_a, id_b))

            is_trigger = self._is_trigger_pair(collider_a, collider_b)

            # Skip sleep/sleep seulement pour solid/solid
            if not is_trigger:
                if parent_id_a not in sleep_cache:
                    body_a = cast("PhysicBodyComponent | None", collider_a.parent.get_component("physic_body"))
                    sleep_cache[parent_id_a] = body_a.is_sleeping if body_a else False
                if parent_id_b not in sleep_cache:
                    body_b = cast("PhysicBodyComponent | None", collider_b.parent.get_component("physic_body"))
                    sleep_cache[parent_id_b] = body_b.is_sleeping if body_b else False

                if sleep_cache[parent_id_a] and sleep_cache[parent_id_b]:
                    continue

            # Narrow phase uniquement si on n'a pas skippé
            info = self._narrow_phase.check_collision(collider_a, collider_b)
            if info is None:
                continue

            collision_info[pair] = info

            if is_trigger:
                triggers.add(pair)
            else:
                collisions.add(pair)
                
        return CollisionResult(
            collisions=collisions, triggers=triggers, collision_info=collision_info
        )

    def _collect_colliders(self, scene: "Scene") -> List["ColliderComponent"]:
        """
        Récupère la liste des colliders actifs depuis la scène.

        Parameters
        ----------
        scene : Scene
            Scène source.

        Returns
        -------
        List[ColliderComponent]
            Colliders actifs.
        """
        colliders: List["ColliderComponent"] = []
        for game_object in scene.game_objects.values():
            if not game_object.active:
                continue
            go_colliders = cast(List["ColliderComponent"], game_object.get_components("collider"))
            colliders.extend(go_colliders)

        return colliders

    def _is_trigger_pair(
        self, collider_a: "ColliderComponent", collider_b: "ColliderComponent"
    ) -> bool:
        """
        Détermine si le couple (A,B) doit être traité en tant que trigger.

        Parameters
        ----------
        collider_a : ColliderComponent
            Collider A.
        collider_b : ColliderComponent
            Collider B.

        Returns
        -------
        bool
            True si trigger, sinon False.
        """
        return not collider_a.solid or not collider_b.solid

    def _candidates_can_collide(
        self, candidates: List[Tuple["ColliderComponent", "ColliderComponent"]]
    ) -> List[Tuple["ColliderComponent", "ColliderComponent"]]:
        """
        Détermine une liste de paires de colliders pouvant entrer en collision.

        Parameters
        ----------
        candidates : List[Tuple["ColliderComponent", "ColliderComponent"]]
            Liste des paires de colliders à tester.

        Returns
        -------
        List[Tuple["ColliderComponent", "ColliderComponent"]]
            Liste des paires pouvant entrer en collision.
        """

        candidates_can_collide: List[Tuple["ColliderComponent", "ColliderComponent"]] = []
        for col_a, col_b in candidates:
            if col_a == col_b:
                continue
            tags_a = col_a.parent.tags
            tags_b = col_b.parent.tags
            if self._tag_system.can_collide(tags_a, tags_b):
                candidates_can_collide.append((col_a, col_b))

        return candidates_can_collide
