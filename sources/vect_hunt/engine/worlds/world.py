from typing import Set, Tuple

from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.physics import ColliderSystem, CollisionTracker
from vect_hunt.engine.input import InputSystem
from vect_hunt.engine.components.collider import Collider
from vect_hunt.engine.physics.collision_resolution_system import (
    CollisionResolutionSystem,
)
from vect_hunt.engine.physics.external_forces_system import ExternalForcesSystem


class World:
    """
    Répresente le monde du jeu, contenant les cibles et le joueur.

    Attributes
    ----------
    game_objects : dict[int, GameObject]
        GameObjects présents dans le monde.
    input_system : InputSystem
        Système d'inputs du monde.
    collider_system : ColliderSystem
        Système global de détection des collisions.
    collision_tracker : CollisionTracker
        Tracker des collisions pour les événements.
    collision_resolution_system : CollisionResolutionSystem
        Système de résolution des collisions.
    """

    def __init__(self):
        """
        Initialise un monde de jeu vide.
        """
        self.game_objects: dict[int, GameObject] = {}

        self.input_system = InputSystem()

        self.collider_system = ColliderSystem()
        self.collision_tracker = CollisionTracker()
        self.collision_resolution_system = CollisionResolutionSystem(self)
        self.external_forces_system = ExternalForcesSystem()

    def add_game_object(self, game_object: GameObject) -> None:
        """
        Ajoute un GameObject au monde.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à ajouter.
        """
        game_object.name = self.validate_name(game_object.name)

        self.game_objects[game_object.id] = game_object

    def remove_game_object(self, game_object: GameObject) -> None:
        """
        Retire un GameObject du monde.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à retirer.
        """
        if game_object.id in self.game_objects:
            del self.game_objects[game_object.id]

    def validate_name(self, name: str) -> str:
        """
        Valide et ajuste le nom d'un GameObject pour éviter les conflits.

        Parameters
        ----------
        name : str
            Le nom proposé pour le GameObject.

        Returns
        -------
        str
            Un nom unique pour le GameObject.
        """
        # Collecter tous les noms existants
        existing_names = {obj.name for obj in self.game_objects.values()}

        original_name = name
        counter = 1
        while name in existing_names:
            name = f"{original_name}_{counter}"
            counter += 1
        return name

    def update(self, delta_time: float) -> None:
        """
        Met à jour le monde et tous ses systèmes.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        # Mettre à jour le système d'inputs
        self.input_system.update(delta_time)

        # Mettre à jour tous les GameObjects
        for game_object in self.game_objects.values():
            if game_object.active:
                game_object.update(delta_time)

    def update_collisions(self, delta_time: float) -> None:
        """
        Met à jour le système de collisions et triggers pour cette frame.

        Gère :
        - Les collisions actives (stay)
        - Les triggers actifs (stay)
        - Les événements on_enter / on_exit pour collisions et triggers

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes
        """
        # Détecter toutes les collisions et triggers pour cette frame
        current_collisions, current_triggers, collision_info = (
            self.collider_system.detect_collisions(self)
        )

        # Mettre à jour le tracker (CollisionTracker)
        self.collision_tracker.update(
            current_collisions, current_triggers, collision_info, delta_time
        )

        # Gestion des événements
        self._handle_enters()
        self._handle_exits()
        self._handle_stays(current_collisions, current_triggers)

    def _handle_enters(self):
        """
        Parcourt tous les objets et déclenche on_enter_collision ou on_enter_trigger
        selon le type d'interaction qui vient de commencer cette frame.
        """
        for obj_id, obj in self.game_objects.items():
            for other_id in self.collision_tracker.get_entered_objects(obj_id):
                other = self.game_objects.get(other_id)
                if not other:
                    continue
                if self.collision_tracker.is_collision_active(obj_id, other_id):
                    obj.on_enter_collision(other)
                else:
                    obj.on_enter_trigger(other)

    def _handle_exits(self):
        """
        Parcourt tous les objets et déclenche on_exit_collision ou on_exit_trigger
        selon le type d'interaction qui vient de se terminer cette frame.
        """
        for obj_id, obj in self.game_objects.items():
            for other_id in self.collision_tracker.get_exited_collision_objects(obj_id):
                other = self.game_objects.get(other_id)
                if not other:
                    continue
                obj.on_exit_collision(other)

            for other_id in self.collision_tracker.get_exited_trigger_objects(obj_id):
                other = self.game_objects.get(other_id)
                if not other:
                    continue
                obj.on_exit_trigger(other)

    def _handle_stays(
        self,
        current_collisions: Set[Tuple[int, int]],
        current_triggers: Set[Tuple[int, int]],
    ):
        """
        Déclenche les callbacks 'stay' pour toutes les collisions et triggers
        encore actifs cette frame.
        """
        # Collisions physiques actives
        for obj1_id, obj2_id in current_collisions:
            obj1 = self.game_objects.get(obj1_id)
            obj2 = self.game_objects.get(obj2_id)
            if obj1 and obj2:
                obj1.on_collision(obj2)
                obj2.on_collision(obj1)

        # Triggers actifs
        for obj1_id, obj2_id in current_triggers:
            obj1 = self.game_objects.get(obj1_id)
            obj2 = self.game_objects.get(obj2_id)
            if obj1 and obj2:
                # Déterminer qui est trigger
                colliders1 = obj1.get_components(Collider)
                colliders2 = obj2.get_components(Collider)

                obj1_has_trigger = any(not c.solid for c in colliders1)
                obj2_has_trigger = any(not c.solid for c in colliders2)
                # Appeler on_trigger uniquement pour les objets qui ont des triggers
                if obj1_has_trigger:
                    obj1.on_trigger(obj2)
                if obj2_has_trigger:
                    obj2.on_trigger(obj1)
