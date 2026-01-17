from .tag import Tag
from typing import Dict
import json
import os

# Chemin du fichier de configuration JSON
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets/data/configs/collision.json",
)


def _load_collision_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _tag_from_str(tag_str: str) -> Tag:
    try:
        return Tag[tag_str]
    except KeyError:
        return Tag.NONE


def _build_mask(matrix_dict) -> Dict[Tag, Tag]:
    mask = {}
    for tag_str, targets in matrix_dict.items():
        tag = _tag_from_str(tag_str)
        value = Tag.NONE
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
        Vérifie si deux tags peuvent collisionner selon la matrice chargée.
        """
        return bool(
            CAN_COLLIDE.get(tag1, Tag.NONE) & tag2
            or CAN_COLLIDE.get(tag2, Tag.NONE) & tag1
        )

    @staticmethod
    def can_destroy(tag1: Tag, tag2: Tag) -> bool:
        return bool(CAN_DESTROY.get(tag1, Tag.NONE) & tag2)

    @staticmethod
    def can_pickup(tag1: Tag, tag2: Tag) -> bool:
        return bool(CAN_PICKUP.get(tag1, Tag.NONE) & tag2)
