from typing import List, Tuple, cast, TYPE_CHECKING, Dict

from vect_hunt.engine.input.input_system import InputSystem
from vect_hunt.engine.physics.collider_detection import ColliderDetection
from vect_hunt.engine.physics.collision_resolution_system import (
    CollisionResolutionSystem
)
from vect_hunt.engine.physics.collision_tracker import CollisionTracker
from vect_hunt.engine.physics.external_forces_system import ExternalForcesSystem

if TYPE_CHECKING:
    from vect_hunt.engine.components.physic_body_component import PhysicBodyComponent
    from vect_hunt.engine.core.tag_system import TagSystem
    from vect_hunt.engine.scenes.scene import Scene
    from vect_hunt.engine.components.collider.collider_component import ColliderComponent

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
        scene: "Scene",
        input_config: dict,
        tag_system: "TagSystem",
        max_collision_passes: int = 4,
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

        self.collision_tracker = CollisionTracker()

        self.collision_resolution_system = CollisionResolutionSystem(scene)
        self.external_forces_system = ExternalForcesSystem()

        # Suivi des collisions et triggers au niveau des objets
        self._object_collision_counts: Dict[Tuple[int, int], int] = {}
        self._object_trigger_counts: Dict[Tuple[int, int], int] = {}

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

        # Gameplay
        self._update_inputs(delta_time)
        self._update_game_objects(delta_time)
        self.external_forces_system.apply_gravity(self.scene, delta_time)
        self._update_game_objects_velocities(delta_time)

        # Met à jour le tracker
        self.update_collision_tracker(delta_time)

        # Résolution des collisions
        self._resolve_collisions(delta_time)
        self._update_game_objects_sleep(delta_time)
        self._update_game_objects_transforms(delta_time)

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

            for body in cast(List["PhysicBodyComponent"], game_object.get_components("physic_body")):
                body.integrate_velocity(delta_time)

    def _update_game_objects_sleep(self, delta_time: float) -> None:
        """
        Met à jour le statut de sommeil de tous les GameObjects de la scène.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        for game_object in self.scene.game_objects.values():
            if not game_object.active:
                continue

            for body in cast(List["PhysicBodyComponent"], game_object.get_components("physic_body")):
                body.sleep_check(delta_time)

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

            for body in cast(List["PhysicBodyComponent"], game_object.get_components("physic_body")):
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

    def update_collision_tracker(self, delta_time: float) -> None:
        """
        Met a jour le systeme de collisions et triggers pour cette frame.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        collision_result = self.collider_detection.detect(self.scene)

        # Le tracker travaille en collider pairs
        self.collision_tracker.update(collision_result.collisions, collision_result.triggers, delta_time)

        # Dispatch gameplay au niveau GameObject via agrégation
        self._dispatch_collision_events()
        self._dispatch_trigger_events()


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

        # 1) Detect contacts 
        collision_result = self.collider_detection.detect(self.scene)
        if not collision_result.collisions:
            return
        collision_info = self.collision_resolution_system.resolve_all_collision_info(
            collision_result.collisions,
            collision_result.collision_info,
        )

        # 2) Warm starting + purge cache 
        active_keys = self.collision_resolution_system.build_active_contact_keys(
            collisions=list(collision_result.collisions),
            collision_info=collision_info,
        )
        self.collision_resolution_system.prune_contact_cache(active_keys)
        self.collision_resolution_system.warm_start_contacts(
            collisions=list(collision_result.collisions),
            collision_info=collision_info,
            warm_start_factor=0.9,  # valeur de départ (0.7..1.0)
        )

        # 3) ittération d'impulsion
        for i in range(self.impulse_iterations):
            moved = self.collision_resolution_system.apply_impulse_response(
                list(collision_result.collisions),
                collision_info,
                self.collision_tracker.get_all_entered(),
                delta_time=delta_time,
            )
            if not moved:
                break

        # 4) Detect contacts after impulsion
        collision_result = self.collider_detection.detect(self.scene)
        if not collision_result.collisions:
            return
        collision_info = self.collision_resolution_system.resolve_all_collision_info(
            collision_result.collisions,
            collision_result.collision_info,
        )

        # 5) Small position correction passes 
        for j in range(self.max_collision_passes):
            moved = self.collision_resolution_system.correct_collisions(
                list(collision_result.collisions),
                collision_info,
            )
            if not moved:
                break
            
        # 6) Debug
        # print(
        #     i + 1,
        #     "impulse passes performed.",
        #     j + 1,
        #     "position correction passes performed.",
        # )

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
    def _dispatch_collision_events(self) -> None:
        """
        Envoie des événements collision au niveau GameObject.

        Règles
        ------
        - Enter : compteur 0 -> 1
        - Exit  : compteur 1 -> 0
        - Stay  : compteur > 0
        """
        entered_pairs = self.collision_tracker.get_all_entered()
        exited_pairs = self.collision_tracker.get_all_exited_collisions()

        # ENTER (collider-level -> object-level)
        for col_a, col_b in entered_pairs:
            if not self.collision_tracker.is_collision_active(col_a, col_b):
                continue

            obj_pair = self._collider_pair_to_object_pair(col_a, col_b)
            if obj_pair is None:
                continue

            previous = self._object_collision_counts.get(obj_pair, 0)
            self._object_collision_counts[obj_pair] = previous + 1
            if previous == 0:
                self._emit_enter_collision(obj_pair)

        # EXIT
        for col_a, col_b in exited_pairs:
            obj_pair = self._collider_pair_to_object_pair(col_a, col_b)
            if obj_pair is None:
                continue

            previous = self._object_collision_counts.get(obj_pair, 0)
            if previous <= 1:
                if obj_pair in self._object_collision_counts:
                    del self._object_collision_counts[obj_pair]
                self._emit_exit_collision(obj_pair)
            else:
                self._object_collision_counts[obj_pair] = previous - 1

        # STAY (une fois par paire d'objets)
        for obj_pair in list(self._object_collision_counts.keys()):
            self._emit_stay_collision(obj_pair)

    def _emit_enter_collision(self, obj_pair: Tuple[int, int]) -> None:
        """
        Envoie un événement d'entrée de collision à une paire d'objets.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en collision.
        """
        obj_a_id, obj_b_id = obj_pair
        obj_a = self.scene.game_objects.get(obj_a_id)
        obj_b = self.scene.game_objects.get(obj_b_id)
        if obj_a is None or obj_b is None:
            return
        
        obj_a.on_enter_collision(obj_b)
        obj_b.on_enter_collision(obj_a)

    def _emit_exit_collision(self, obj_pair: Tuple[int, int]) -> None:
        """
        Envoie un événement de sortie de collision à une paire d'objets.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en collision.
        """
        obj_a_id, obj_b_id = obj_pair
        obj_a = self.scene.game_objects.get(obj_a_id)
        obj_b = self.scene.game_objects.get(obj_b_id)
        if obj_a is None or obj_b is None:
            return
        obj_a.on_exit_collision(obj_b)
        obj_b.on_exit_collision(obj_a)

    def _emit_stay_collision(self, obj_pair: Tuple[int, int]) -> None:
        """
        Envoie un événement de maintien de collision à une paire d'objets.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en collision.
        """
        obj_a_id, obj_b_id = obj_pair
        obj_a = self.scene.game_objects.get(obj_a_id)
        obj_b = self.scene.game_objects.get(obj_b_id)
        if obj_a is None or obj_b is None:
            return
        obj_a.on_collision(obj_b)
        obj_b.on_collision(obj_a)

    def _dispatch_trigger_events(self) -> None:
        """
        Envoie des événements trigger au niveau GameObject.
        """
        entered_pairs = self.collision_tracker.get_all_entered()
        exited_pairs = self.collision_tracker.get_all_exited_triggers()

        # ENTER
        for col_a, col_b in entered_pairs:
            if not self.collision_tracker.is_trigger_active(col_a, col_b):
                continue

            obj_pair = self._collider_pair_to_object_pair(col_a, col_b)
            if obj_pair is None:
                continue

            previous = self._object_trigger_counts.get(obj_pair, 0)
            self._object_trigger_counts[obj_pair] = previous + 1
            if previous == 0:
                self._emit_enter_trigger(obj_pair, col_a, col_b)

        # EXIT
        for col_a, col_b in exited_pairs:
            obj_pair = self._collider_pair_to_object_pair(col_a, col_b)
            if obj_pair is None:
                continue

            previous = self._object_trigger_counts.get(obj_pair, 0)
            if previous <= 1:
                if obj_pair in self._object_trigger_counts:
                    del self._object_trigger_counts[obj_pair]
                self._emit_exit_trigger(obj_pair, col_a, col_b)
            else:
                self._object_trigger_counts[obj_pair] = previous - 1

        # STAY
        for obj_pair in list(self._object_trigger_counts.keys()):
            self._emit_stay_trigger(obj_pair)

    def _emit_enter_trigger(self, obj_pair: Tuple[int, int], col_a: int, col_b: int) -> None:
        """
        Emet un trigger d'entrée.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en trigger.
        col_a : int
            ID du premier collider.
        col_b : int
            ID du second collider.
        """
        self._emit_trigger_event("enter", obj_pair, col_a, col_b)

    def _emit_exit_trigger(self, obj_pair: Tuple[int, int], col_a: int, col_b: int) -> None:
        """
        Emet un trigger de sortie.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en trigger.
        col_a : int
            ID du premier collider.
        col_b : int
            ID du second collider.
        """
        self._emit_trigger_event("exit", obj_pair, col_a, col_b)

    def _emit_stay_trigger(self, obj_pair: Tuple[int, int]) -> None:
        """
        Emet un trigger de maintien.

        Parameters:
        -----------
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en trigger.
        """
        # Pour stay, on n'a pas les col ids spécifiques. Si tu veux une sémantique exacte,
        # il faut aussi conserver "quels collider-pairs actifs" -> object-pair.
        # Version simple: appeler sur les deux objets qui ont au moins un trigger collider.
        obj_a_id, obj_b_id = obj_pair
        obj_a = self.scene.game_objects.get(obj_a_id)
        obj_b = self.scene.game_objects.get(obj_b_id)
        if obj_a is None or obj_b is None:
            return

        if self._object_has_trigger(obj_a_id):
            obj_a.on_trigger(obj_b)
        if self._object_has_trigger(obj_b_id):
            obj_b.on_trigger(obj_a)

    def _emit_trigger_event(self, kind: str, obj_pair: Tuple[int, int], col_a: int, col_b: int) -> None:
        """
        Emet un événement de trigger.

        Parameters:
        -----------
        kind : str
            Type d'événement de trigger ("enter" ou "exit").
        obj_pair : Tuple[int, int]
            Paire d'IDs d'objets en trigger.
        col_a : int
            ID du premier collider.
        col_b : int
            ID du second collider.
        """
        obj_a_id, obj_b_id = obj_pair
        obj_a = self.scene.game_objects.get(obj_a_id)
        obj_b = self.scene.game_objects.get(obj_b_id)
        if obj_a is None or obj_b is None:
            return

        col_a_comp = cast("ColliderComponent | None", self.scene.components.get(col_a))
        col_b_comp = cast("ColliderComponent | None", self.scene.components.get(col_b))
        if col_a_comp is None or col_b_comp is None:
            return

        # Si col_a est un trigger (solid=False), alors A reçoit l'event
        if not col_a_comp.solid:
            if kind == "enter":
                obj_a.on_enter_trigger(obj_b)
            else:
                obj_a.on_exit_trigger(obj_b)

        # Si col_b est un trigger, alors B reçoit l'event
        if not col_b_comp.solid:
            if kind == "enter":
                obj_b.on_enter_trigger(obj_a)
            else:
                obj_b.on_exit_trigger(obj_a)

    def _object_has_trigger(self, obj_id: int) -> bool:
        """
        Vérifie si un objet possède au moins un collider de type trigger (non solide).

        Parameters:
        -----------
        obj_id : int
            ID de l'objet à vérifier.

        Returns:
        --------
        bool
            True si l'objet possède au moins un collider de type trigger, False sinon.
        """
        obj = self.scene.game_objects.get(obj_id)
        if obj is None:
            return False
        colliders = cast(List["ColliderComponent"], obj.get_components("collider"))
        return any(not c.solid for c in colliders)