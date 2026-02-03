from dataclasses import dataclass
from typing import Dict, Set, Tuple

from vect_hunt.engine.core.collisions.collision_info import CollisionInfo


# TODO : Pour le moment on stock des paires de parents, on perds l'info des colliders.
#       A voir si on veut garder ça comme ça (plus simple pour le reste du moteur)
#       ou si on veut stocker les colliders eux-mêmes (plus d'infos, mais plus lourd).
@dataclass(frozen=True)
class CollisionResult:
    """
    Conteneur du résultat de la détection de collisions.

    Attributes
    ----------
    collisions : Set[Tuple[int, int]]
        Paires (id_a, id_b) en collision (non trigger), id_a < id_b.
    triggers : Set[Tuple[int, int]]
        Paires (id_a, id_b) en trigger, id_a < id_b.
    collision_info : Dict[Tuple[int, int], CollisionInfo]
        Map pair -> infos de collision (principalement pour collisions, mais peut aussi
        contenir des triggers si tu veux des points/normal/depth pour eux).
    """

    collisions: Set[Tuple[int, int]]
    triggers: Set[Tuple[int, int]]
    collision_info: Dict[Tuple[int, int], CollisionInfo]
