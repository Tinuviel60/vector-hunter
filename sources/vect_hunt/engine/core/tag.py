from enum import IntFlag, auto


class Tag(IntFlag):
    """
    Représente un tag unique pour un GameObject.

    Chaque tag correspond à un bit unique dans un entier de 32 bits.
    Limite de 32 tags différents.

    Attributes
    ----------
    NONE : Tag
        Aucun tag.
    PLAYER : Tag
        Tag pour le joueur.
    ENEMY : Tag
        Tag pour les ennemis.
    PROJECTILE : Tag
        Tag pour les projectiles.
    WALL : Tag
        Tag pour les murs.
    PICKUP : Tag
        Tag pour les objets ramassables.
    """

    NONE = 0
    # Les vrais tags sont définis avec `auto()`
    PLAYER = auto()
    ENEMY = auto()
    PROJECTILE = auto()
    WALL = auto()
    PICKUP = auto()
    # Ajoutez ici vos autres tags jusqu'à 32 max
