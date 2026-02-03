from logging import getLogger
from typing import Dict

from .tag import Tag


class TagSystem:
    """
    Système utilitaire pour gérer les tags et tester les collisions.

    Attributes
    ----------
    None
    """

    _logger = getLogger(__name__)

    def __init__(self, config: dict) -> None:
        """
        Initialise les matrices de collision depuis la configuration.

        Parameters
        ----------
        config : dict
            Configuration chargee depuis collision.json.
        """
        self._can: Dict[str, Dict[Tag, Tag]] = {
            "collide": {},
            "destroy": {},
            "pickup": {},
        }
        self._can["collide"] = self._build_mask(config["collision_matrix"])
        self._can["destroy"] = self._build_mask(config.get("destruction_matrix", {}))
        self._can["pickup"] = self._build_mask(config.get("pickup_matrix", {}))

    def can(self, kind: str) -> Dict[Tag, Tag]:
        """
        Retourne la matrice de collision demandee.

        Parameters
        ----------
        kind : str
            "collide", "destroy" ou "pickup".
        """
        if kind not in self._can:
            raise KeyError(f"Matrice inconnue: {kind}")
        return self._can[kind]

    @classmethod
    def _tag_from_str(cls, tag_str: str) -> Tag:
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
            cls._logger.warning(
                f"Tag inconnu dans la configuration de collision : {tag_str}"
            )
            return Tag.NONE

    @classmethod
    def _build_mask(cls, matrix_dict: dict) -> Dict[Tag, Tag]:
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
            tag = cls._tag_from_str(tag_str)
            value = Tag.NONE
            if isinstance(targets, list):
                for t in targets:
                    value |= cls._tag_from_str(t)
            mask[tag] = value
        return mask

    def can_collide(self, tag1: Tag, tag2: Tag) -> bool:
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
        matrix = self.can("collide")
        return bool(
            matrix.get(tag1, Tag.NONE) & tag2 or matrix.get(tag2, Tag.NONE) & tag1
        )

    def can_destroy(self, tag1: Tag, tag2: Tag) -> bool:
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
        return bool(self.can("destroy").get(tag1, Tag.NONE) & tag2)

    def can_pickup(self, tag1: Tag, tag2: Tag) -> bool:
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
        return bool(self.can("pickup").get(tag1, Tag.NONE) & tag2)
