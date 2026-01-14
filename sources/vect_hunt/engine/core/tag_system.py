from .tag import Tag
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
    def _check_mask(source: Tag, target: Tag, mask: dict[Tag, Tag]) -> bool:
        """
        Vérifie si une interaction est permise entre deux tags selon un masque donné.

        Parameters
        ----------
        source : Tag
            Le tag source de l'interaction.
        target : Tag
            Le tag cible de l'interaction.
        mask : dict[Tag, Tag]
            Le masque d'interaction à utiliser.

        Returns
        -------
        bool
            True si l'interaction est permise, False sinon.
        """
        return bool(mask.get(source, Tag.NONE) & target)

    @staticmethod
    def can_collide(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si un tag peut entrer en collision avec le second.

        Parameters
        ----------
        source : Tag
            Le tag source de l'interaction.
        target : Tag
            Le tag cible de l'interaction.

        Returns
        -------
        bool
            True si la collision est permise, False sinon.
        """
        return TagSystem._check_mask(tag1, tag2, CAN_COLLIDE)

    @staticmethod
    def can_destroy(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si un tag peut détruire le second.

        Parameters
        ----------
        source : Tag
            Le tag source de l'interaction.
        target : Tag
            Le tag cible de l'interaction.

        Returns
        -------
        bool
            True si la destruction est permise, False sinon.
        """
        return TagSystem._check_mask(tag1, tag2, CAN_DESTROY)

    @staticmethod
    def can_pickup(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si un tag peut ramasser le second.

        Parameters
        ----------
        source : Tag
            Le tag source de l'interaction.
        target : Tag
            Le tag cible de l'interaction.

        Returns
        -------
        bool
            True si le ramassage est permis, False sinon.
        """
        return TagSystem._check_mask(tag1, tag2, CAN_PICKUP)
