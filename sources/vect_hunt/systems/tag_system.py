from vect_hunt.core import Tag
from typing import Dict

# Masque de collision par défaut : quels tags peuvent interagir avec quels autres
# Exemple : PLAYER peut toucher ENEMY et PICKUP
CAN_COLLIDE: Dict[Tag, Tag] = {
    Tag.PLAYER: Tag.ENEMY,
    Tag.ENEMY: Tag.PLAYER | Tag.WALL | Tag.PROJECTILE,
    Tag.PROJECTILE: Tag.ENEMY | Tag.WALL,
    Tag.WALL: Tag.PLAYER | Tag.ENEMY | Tag.PROJECTILE,
}


# NOTE : Exemple de masque d'interraction via les tags, non implémentée dans le moteur
CAN_DESTROY: Dict[Tag, Tag] = {
    Tag.PROJECTILE: Tag.ENEMY | Tag.WALL,
    Tag.ENEMY: Tag.PLAYER,
}

# NOTE : Exemple de masque d'interraction via les tags, non implémentée dans le moteur
CAN_PICKUP: Dict[Tag, Tag] = {
    Tag.PLAYER: Tag.PICKUP,
}


class TagSystem:
    """
    Système utilitaire pour gérer les tags et tester les collisions.
    """

    @staticmethod
    def can_collide(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si deux tags peuvent interagir pour une collision.

        Parameters
        ----------
        tag1 : Tag
            Premier tag.
        tag2 : Tag
            Deuxième tag.

        Returns
        -------
        bool
            True si les objets peuvent interagir.
        """
        # On teste si tag2 est présent dans le masque autorisé de tag1
        return bool(CAN_COLLIDE.get(tag1, Tag.NONE) & tag2)
    
    # NOTE : Exemple d'interraction via les tags, non implémentée dans le moteur
    @staticmethod
    def can_destroy(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si un objet avec tag1 peut détruire un objet avec tag2.

        Parameters
        ----------
        tag1 : Tag
            Tag de l'objet agresseur.
        tag2 : Tag
            Tag de l'objet cible.

        Returns
        -------
        bool
            True si l'objet avec tag1 peut détruire l'objet avec tag2.
        """
        return bool(CAN_DESTROY.get(tag1, Tag.NONE) & tag2)
    
    # NOTE : Exemple d'interraction via les tags, non implémentée dans le moteur
    @staticmethod
    def can_pickup(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si un objet avec tag1 peut ramasser un objet avec tag2.

        Parameters
        ----------
        tag1 : Tag
            Tag de l'objet ramasseur.
        tag2 : Tag
            Tag de l'objet ramassable.

        Returns
        -------
        bool
            True si l'objet avec tag1 peut ramasser l'objet avec tag2.
        """
        return bool(CAN_PICKUP.get(tag1, Tag.NONE) & tag2)