from .tag import Tag
from typing import Dict
from logging import getLogger
from vect_hunt.engine.resources.loaders.data_loader import DataLoader

logger = getLogger(__name__)


def _load_collision_config() -> dict:
    """
    Charge la configuration de collision depuis un fichier JSON.

    Returns
    -------
    dict
        Dictionnaire contenant la configuration de collision.
    """
    return DataLoader.load_json("configs/collision.json")


def _tag_from_str(tag_str: str) -> Tag:
    """
    Convertit une chaîne en Tag, avec gestion des erreurs.

    Parameters
    ----------
    tag_str : str
        Chaîne représentant le tag.

    Returns
    -------
    Tag
        Le tag correspondant, ou Tag.NONE si inconnu.
    """
    try:
        return Tag[tag_str]
    except KeyError:
        logger.warning(f"Tag inconnu dans la configuration de collision : {tag_str}")
        return Tag.NONE


def _build_mask(matrix_dict) -> Dict[Tag, Tag]:
    """
    Construit une matrice de masque de collision à partir d'un dictionnaire.
    Parameters
    ----------
    matrix_dict : dict
        Dictionnaire représentant la matrice de collision.

    Returns
    -------
    Dict[Tag, Tag]
        Dictionnaire mappant chaque Tag à son masque de collision.
    """
    mask = {}
    for tag_str, targets in matrix_dict.items():
        tag = _tag_from_str(tag_str)
        value = Tag.NONE
        if isinstance(targets, list):
            for t in targets:
                value |= _tag_from_str(t)
        mask[tag] = value
    return mask


# Charger la configuration JSON
_config = _load_collision_config()
CAN_COLLIDE = _build_mask(_config["collision_matrix"])
CAN_DESTROY = _build_mask(_config.get("destruction_matrix", {}))
CAN_PICKUP = _build_mask(_config.get("pickup_matrix", {}))


class TagSystem:
    """
    Système utilitaire pour gérer les tags et tester les collisions.

    Attributes
    ----------
    None
    """

    @staticmethod
    def can_collide(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si deux tags peuvent collisionner selon la matrice de collision.

        Parameters
        ----------
        tag1 : Tag
            Premier tag.
        tag2 : Tag
            Second tag.

        Returns
        -------
        bool
            True si les deux tags peuvent collisionner, False sinon.
        """
        return bool(
            CAN_COLLIDE.get(tag1, Tag.NONE) & tag2
            or CAN_COLLIDE.get(tag2, Tag.NONE) & tag1
        )

    @staticmethod
    def can_destroy(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si deux tags peuvent collisionner selon la matrice de destruction.

        Parameters
        ----------
        tag1 : Tag
            Premier tag.
        tag2 : Tag
            Second tag.

        Returns
        -------
        bool
            True si le tag1 peut détruire le tag2, False sinon.
        """
        return bool(CAN_DESTROY.get(tag1, Tag.NONE) & tag2)

    @staticmethod
    def can_pickup(tag1: Tag, tag2: Tag) -> bool:
        """
        Vérifie si deux tags peuvent collisionner selon la matrice de ramassage.

        Parameters
        ----------
        tag1 : Tag
            Premier tag.
        tag2 : Tag
            Second tag.

        Returns
        -------
        bool
            True si le tag1 peut ramasser le tag2, False sinon.
        """
        return bool(CAN_PICKUP.get(tag1, Tag.NONE) & tag2)
