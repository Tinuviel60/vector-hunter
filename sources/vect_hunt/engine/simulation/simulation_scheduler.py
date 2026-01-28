from typing import Set, Tuple

from vect_hunt.engine.components.collider.collider_component import ColliderComponent
from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
from vect_hunt.engine.core.collisions.collision_info import CollisionInfo
from vect_hunt.engine.input.input_system import InputSystem
from vect_hunt.engine.physics.collider_detection import ColliderDetection
from vect_hunt.engine.physics.collision_resolution_system import (
    CollisionResolutionSystem,
)
from vect_hunt.engine.physics.collision_tracker import CollisionTracker
from vect_hunt.engine.physics.external_forces_system import ExternalForcesSystem


class SimulationScheduler:
    """
    Orchestrateur de la simulation.

    Centralise l'ordre d'update du monde (inputs, objets, forces, collisions).

    Notes
    -----
    Cette version considère que le système de collision travaille en collider/collider.
    Les callbacks gameplay (on_enter_collision, etc.) restent en game_object/game_object
    et sont dérivés des paires de colliders avec déduplication.
    """

    def __init__(
        self,
        scene,
        input_config: dict,
        tag_system,
        max_collision_passes: int = 2,
    ) -> None:
        """
        Initialise le scheduler pour une scene.

        Parameters
        ----------
        scene : Scene
            La scene a mettre a jour.
        max_collision_passes : int
            Nombre max d'iterations de resolution des collisions.
        """
        self.scene = scene
        self.max_collision_passes = max_collision_passes
        self.impulse_iterations = max_collision_passes * 2

        self.input_system = InputSystem(input_config)
        self.collider_detection = ColliderDetection(tag_system)

        # TODO : On doit tracker des collider id maintenat, a faire
        self.collision_tracker = CollisionTracker()

        self.collision_resolution_system = CollisionResolutionSystem(scene)
        self.external_forces_system = ExternalForcesSystem()

    def handle_event(self, event) -> None:
        """
        Traite un événement d'entrée via l'InputSystem.
        """
        self.input_system.process_event(event)

    def update(self, delta_time: float) -> None:
        """
        Met a jour la scene et ses systemes.

        Parameters
        ----------
        delta_time : float
            Temps ecoule depuis la derniere frame (en secondes).
        """
        self._update_inputs(delta_time)
        self._update_game_objects(delta_time)
        self.external_forces_system.apply_gravity(self.scene, delta_time)
        self._update_game_objects_velocities(delta_time)
        self._resolve_collisions(delta_time)
        self._update_game_objects_transforms(delta_time)
        self.update_collisions(delta_time)

    def _update_inputs(self, delta_time: float) -> None:
        """
        Met à jour le système d'entrée.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        self.input_system.update(delta_time)

    def _update_game_objects_velocities(self, delta_time: float) -> None:
        """
        Met à jour les vélocités de tous les GameObjects de la scène.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        for game_object in self.scene.game_objects.values():
            if not game_object.active:
                continue

            for body in game_object.get_components(PhysicBodyComponent):
                body.integrate_velocity(delta_time)

    def _update_game_objects_transforms(self, delta_time: float) -> None:
        """
        Met à jour les transformations de tous les GameObjects de la scène.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        for game_object in self.scene.game_objects.values():
            if not game_object.active:
                continue

            for body in game_object.get_components(PhysicBodyComponent):
                body.integrate_transform(delta_time)

    def _update_game_objects(self, delta_time: float) -> None:
        """
        Met à jour tous les GameObjects de la scène.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        for game_object in self.scene.game_objects.values():
            if game_object.active:
                game_object.update(delta_time)

    def _collider_pairs_to_object_pairs(
        self, pairs: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """
        convertit des paires de collider ids en paires d'object ids.

        Parameters
        ----------
        pairs : Set[Tuple[int, int]]
            Paires de collider ids.

        Returns
        -------
        Set[Tuple[int, int]]
            Paires d'object ids.
        """
        out: Set[Tuple[int, int]] = set()
        for col_a, col_b in pairs:
            p = self._collider_pair_to_object_pair(col_a, col_b)
            if p is not None:
                out.add(p)
        return out

    def update_collisions(self, delta_time: float) -> None:
        """
        Met a jour le systeme de collisions et triggers pour cette frame.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        collision_result = self.collider_detection.detect(self.scene)

        # Convertit collider pairs -> object pairs pour le tracker actuel
        collisions = self._collider_pairs_to_object_pairs(collision_result.collisions)
        triggers = self._collider_pairs_to_object_pairs(collision_result.triggers)

        # TODO : Le tracker doit travailler en collider pairs (pas object pairs)
        self.collision_tracker.update(collisions, triggers, delta_time)

        self._handle_enters()
        self._handle_exits()
        self._handle_stays(collisions, triggers)


    def _resolve_collisions(self, delta_time: float) -> None:
        """
        Résout les collisions en plusieurs passes.

        Cette méthode assume que :
        -Les vélocités des objets ont déjà été mises à jour.
        -Les positions des objets n'ont pas encore été mises à jour.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """

        # 1) Detect contacts once for impulse iterations
        collision_result = self.collider_detection.detect(self.scene)
        if not collision_result.collisions:
            return
        collision_info = self.collision_resolution_system.resolve_all_collision_info(
            collision_result.collisions,
            collision_result.collision_info,
        )

        for i in range(self.impulse_iterations):
            #print("Impulse pass:", i + 1)  # DEBUG
            # Sequential impulses: same contact set, update velocities only
            moved = self.collision_resolution_system.apply_impulse_response(
                list(collision_result.collisions),
                collision_info,
                delta_time=delta_time,
            )
            if not moved:
                break
        
        # 2) Small position correction passes (re-detect each pass)
        for j in range(self.max_collision_passes):
            collision_result = self.collider_detection.detect(self.scene)
            collision_info = self.collision_resolution_system.resolve_all_collision_info(
                collision_result.collisions,
                collision_result.collision_info,
            )
            if not collision_result.collisions:
                break

            moved = self.collision_resolution_system.correct_collisions(
                list(collision_result.collisions),
                collision_result.collision_info,
            )
            if not moved:
                break
        print(
            i + 1,
            "impulse passes performed.",
            j + 1,
            "position correction passes performed.",
        )

    def _collider_pair_to_object_pair(
        self, col_a: int, col_b: int
    ) -> Tuple[int, int] | None:
        """
        Convertit une paire de collider ids en une paire d'object ids.

        Parameters
        ----------
        col_a : int
            Collider id A.
        col_b : int
            Collider id B.

        Returns
        -------
        Tuple[int, int] | None
            (obj_a_id, obj_b_id) ou None si conversion impossible ou même objet.
        """
        obj_a = self.scene.game_objects_by_component.get(col_a)
        obj_b = self.scene.game_objects_by_component.get(col_b)

        if obj_a is None or obj_b is None:
            return None
        if obj_a == obj_b:
            return None

        return (min(obj_a, obj_b), max(obj_a, obj_b))

    def _handle_enters(self) -> None:
        """
        Gère les événements d'entrée de collision et de trigger.
        """
        for obj_id, obj in self.scene.game_objects.items():
            for other_id in self.collision_tracker.get_entered_objects(obj_id):
                other = self.scene.game_objects.get(other_id)
                if not other:
                    continue
                if self.collision_tracker.is_collision_active(obj_id, other_id):
                    obj.on_enter_collision(other)
                else:
                    obj.on_enter_trigger(other)

    def _handle_exits(self) -> None:
        """
        Gère les événements de sortie de collision et de trigger.
        """
        for obj_id, obj in self.scene.game_objects.items():
            for other_id in self.collision_tracker.get_exited_collision_objects(obj_id):
                other = self.scene.game_objects.get(other_id)
                if not other:
                    continue
                obj.on_exit_collision(other)

            for other_id in self.collision_tracker.get_exited_trigger_objects(obj_id):
                other = self.scene.game_objects.get(other_id)
                if not other:
                    continue
                obj.on_exit_trigger(other)

    def _handle_stays(
        self,
        current_collisions: Set[Tuple[int, int]],
        current_triggers: Set[Tuple[int, int]],
    ) -> None:
        """
        Gère les événements de maintien de collision et de trigger.

        Parameters
        ----------
        current_collisions : Set[Tuple[int, int]]
            Ensemble des paires d'IDs d'objets en collision cette frame.
        current_triggers : Set[Tuple[int, int]]
            Ensemble des paires d'IDs d'objets en trigger cette frame.
        """
        # Collisions physiques actives
        for obj1_id, obj2_id in current_collisions:
            obj1 = self.scene.game_objects.get(obj1_id)
            obj2 = self.scene.game_objects.get(obj2_id)
            if obj1 and obj2:
                obj1.on_collision(obj2)
                obj2.on_collision(obj1)

        # Triggers actifs
        for obj1_id, obj2_id in current_triggers:
            obj1 = self.scene.game_objects.get(obj1_id)
            obj2 = self.scene.game_objects.get(obj2_id)
            if obj1 and obj2:
                colliders1 = obj1.get_components(ColliderComponent)
                colliders2 = obj2.get_components(ColliderComponent)

                obj1_has_trigger = any(not c.solid for c in colliders1)
                obj2_has_trigger = any(not c.solid for c in colliders2)
                if obj1_has_trigger:
                    obj1.on_trigger(obj2)
                if obj2_has_trigger:
                    obj2.on_trigger(obj1)
