from typing import List, Tuple

from vect_hunt.engine.components.collider.collider_component import ColliderComponent
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

        Stratégie actuelle : O(n²) avec test AABB.
        Améliorable plus tard (spatial hash, quadtree, sweep&prune, etc.).

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

        for i in range(count):
            c1 = colliders[i]
            aabb1 = c1.get_scene_aabb()

            for j in range(i + 1, count):
                c2 = colliders[j]

                aabb2 = c2.get_scene_aabb()
                if self.aabb_overlap(aabb1, aabb2):
                    candidates.append((c1, c2))

        return candidates
