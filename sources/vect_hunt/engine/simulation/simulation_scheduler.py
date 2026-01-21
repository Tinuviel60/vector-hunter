from typing import Set, Tuple

from vect_hunt.engine.components.collider import ColliderComponent
from vect_hunt.engine.input import InputSystem
from vect_hunt.engine.physics.collider_system import ColliderSystem
from vect_hunt.engine.physics.collision_resolution_system import (
    CollisionResolutionSystem,
)
from vect_hunt.engine.physics.collision_tracker import CollisionTracker
from vect_hunt.engine.physics.external_forces_system import ExternalForcesSystem


class SimulationScheduler:
    """
    Orchestrateur de la simulation.

    Centralise l'ordre d'update du monde (inputs, objets, forces, collisions).
    """

    def __init__(
        self,
        scene,
        input_config: dict,
        tag_system,
        max_collision_passes: int = 6,
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

        self.input_system = InputSystem(input_config)
        self.collider_system = ColliderSystem(tag_system)
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
        self.update_collisions(delta_time)
        self._resolve_collisions()

    def _update_inputs(self, delta_time: float) -> None:
        """
        Met à jour le système d'entrée.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        self.input_system.update(delta_time)

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

    def update_collisions(self, delta_time: float) -> None:
        """
        Met a jour le systeme de collisions et triggers pour cette frame.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        current_collisions, current_triggers, collision_info = (
            self.collider_system.detect_collisions(self.scene)
        )

        self.collision_tracker.update(
            current_collisions, current_triggers, collision_info, delta_time
        )

        self._handle_enters()
        self._handle_exits()
        self._handle_stays(current_collisions, current_triggers)

    def _resolve_collisions(self) -> None:
        """
        Résout les collisions en plusieurs passes.

        Utilise un nombre maximal d'itérations pour éviter les boucles infinies.
        """
        for _ in range(self.max_collision_passes):
            collisions, _, collision_info = self.collider_system.detect_collisions(
                self.scene
            )
            moved = self.collision_resolution_system.update_from_collisions(
                list(collisions),
                collision_info,
            )
            if not moved:
                break

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
