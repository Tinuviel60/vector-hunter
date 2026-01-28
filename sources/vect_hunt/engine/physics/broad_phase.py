from typing import List, Tuple

from vect_hunt.engine.components.collider.collider_component import ColliderComponent
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D


class BroadPhase:
    """
    Réalise la broad phase : produire des paires candidates à tester.

    L'objectif est d'éliminer un maximum de couples impossibles (trop loin)
    avant de faire les tests géométriques précis (narrow phase).
    """

    def __init__(self) -> None:
        """
        Initialise la broad phase.
        """

    def aabb_overlap(
        self, a: Tuple[Vector2D, Vector2D], b: Tuple[Vector2D, Vector2D]
    ) -> bool:
        """
        Détermine si deux AABB se chevauchent.

        Parameters
        ----------
        a : tuple[Vector2D, Vector2D]
            AABB A sous forme (min, max).
        b : tuple[Vector2D, Vector2D]
            AABB B sous forme (min, max).

        Returns
        -------
        bool
            True si les AABB se chevauchent, sinon False.
        """
        a_min, a_max = a
        b_min, b_max = b

        # Séparation sur X
        if a_max.x < b_min.x or b_max.x < a_min.x:
            return False

        # Séparation sur Y
        if a_max.y < b_min.y or b_max.y < a_min.y:
            return False

        return True

    def compute_candidate_pairs(
        self, colliders: List[ColliderComponent]
    ) -> List[Tuple[ColliderComponent, ColliderComponent]]:
        """
        Produit la liste des paires candidates à tester en narrow phase.

        Utilisation d'un algorithme de balayage (sweep and prune)
        sur l'axe X pour réduire le nombre de tests AABB.

        Parameters
        ----------
        colliders : List[ColliderComponent]
            Liste des colliders actifs.

        Returns
        -------
        List[Tuple[ColliderComponent, ColliderComponent]]
            Paires candidates (id_a, id_b) avec id_a < id_b.
        """
        candidates: List[Tuple[ColliderComponent, ColliderComponent]] = []
        count = len(colliders)

        aabbs: List[Tuple[Vector2D, Vector2D]] = [c.get_scene_aabb() for c in colliders]

        indices = list(range(count))

        # Trie des indices de colliders par min.x
        indices.sort(key=lambda i: aabbs[i][0].x)

        active: List[int] = []

        for i in indices:
            min_x = aabbs[i][0].x

            # Retirer ceux qui ne peuvent plus overlap sur X
            kept: List[int] = []
            for j in active:
                if aabbs[j][1].x + Tolerence.COLLISION >= min_x:
                    kept.append(j)
            active = kept

            # Tester contre ceux qui overlap sur X
            for j in active:
                if self.aabb_overlap(aabbs[i], aabbs[j]):
                    if colliders[i].parent.id < colliders[j].parent.id:
                        candidates.append((colliders[i], colliders[j]))
                    else:
                        candidates.append((colliders[j], colliders[i]))

            active.append(i)

        return candidates
