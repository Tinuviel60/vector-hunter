from vect_hunt.objects import GameObject
from vect_hunt.systems import ColliderSystem
from vect_hunt.trackers import CollisionTracker


class World:
    """
    Répresente le monde du jeu, contenant les cibles et le joueur.
    """

    def __init__(self):
        """
        Initialise un monde de jeu vide.
        """

        # TODO : targets and player to remove when GameObject  is fully in place ?
        self.targets: dict[str, GameObject] = {}  # TODO Define a proper target class
        self.player = object()  # TODO Define a proper player class

        self.game_objects: dict[int, GameObject] = {}

        self.collider_system = ColliderSystem()
        self.collision_tracker = CollisionTracker()

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
        self.collider_system.register(game_object)

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
        self.collider_system.unregister(game_object)

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

    def update_collisions(self, delta_time: float) -> None:
        """
        Met à jour le système de collision et déclenche les callbacks appropriés.
        
        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes
        """
        # Détecter les collisions de cette frame
        current_collisions, current_triggers = self.collider_system.detect_collisions()
        
        # Mettre à jour le tracker
        self.collision_tracker.update(current_collisions, current_triggers, delta_time)
        
        # Déclencher les callbacks on_collision pour les collisions actives
        for obj1_id, obj2_id in current_collisions:
            obj1 = self.game_objects.get(obj1_id)
            obj2 = self.game_objects.get(obj2_id)
            if obj1 and obj2:
                obj1.on_collision(obj2)
                obj2.on_collision(obj1)
        
        # Déclencher les callbacks on_trigger pour les triggers actifs
        for obj1_id, obj2_id in current_triggers:
            obj1 = self.game_objects.get(obj1_id)
            obj2 = self.game_objects.get(obj2_id)
            if obj1 and obj2:
                # Déterminer qui est trigger
                obj1_has_trigger = any(not c.solid for c in obj1.colliders)
                obj2_has_trigger = any(not c.solid for c in obj2.colliders)
                
                # Appeler on_trigger uniquement pour les objets qui ont des triggers
                if obj1_has_trigger:
                    obj1.on_trigger(obj2)
                if obj2_has_trigger:
                    obj2.on_trigger(obj1)
