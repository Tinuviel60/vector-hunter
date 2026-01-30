from typing import Dict, List, Optional, Set, Tuple

from vect_hunt.engine.core.collisions.collision_info import CollisionInfo

"""Module de tracking des collisions entre colliders du jeu."""


class CollisionTracker:
    """
    Gestionnaire de suivi des collisions entre colliders.

    Cette classe suit les collisions et triggers entre frames pour détecter
    les événements on_enter, on_exit et on_stay.

    Il s'agit de l'état des collisions pré-correction des collisions.

    Attributes
    ----------
    None

    Notes
    -----
    Les paires d'IDs sont toujours stockées dans l'ordre (min_id, max_id)
    pour éviter les doublons.
    """

    def __init__(self):
        """
        Initialise le tracker de collisions.
        """
        self._active_collisions: Dict[Tuple[int, int], float] = {}
        self._active_triggers: Dict[Tuple[int, int], float] = {}
        self._entered_this_frame: Set[Tuple[int, int]] = set()
        self._exited_this_frame: Set[Tuple[int, int]] = set()
        self._exited_collisions: Set[Tuple[int, int]] = set()
        self._exited_triggers: Set[Tuple[int, int]] = set()

    def _normalize_pair(self, col1_id: int, col2_id: int) -> Tuple[int, int]:
        """
        Normalise une paire d'IDs pour assurer l'ordre (min, max).

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        Tuple[int, int]
            Paire d'IDs ordonnée
        """
        return (min(col1_id, col2_id), max(col1_id, col2_id))

    def update(
        self,
        collisions: Set[Tuple[int, int]],
        triggers: Set[Tuple[int, int]],
        delta_time: float,
    ):
        """
        Met à jour le tracking des collisions pour la frame courante.

        Parameters
        ----------
        collisions : Set[Tuple[int, int]]
            Ensemble des paires de colliders en collision pour cette frame.
        triggers : Set[Tuple[int, int]]
            Ensemble des paires de colliders en trigger pour cette frame.
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes
        """
        # Réinitialiser les événements de la frame
        self._entered_this_frame.clear()
        self._exited_this_frame.clear()
        self._exited_collisions.clear()
        self._exited_triggers.clear()

        # Séparer et normaliser les paires, construire le mapping infos
        normalized_collisions = set()

        for pair in collisions:
            norm_pair = self._normalize_pair(*pair)
            normalized_collisions.add(norm_pair)

        normalized_triggers = {self._normalize_pair(*pair) for pair in triggers}
        # Traiter les collisions
        self._update_category(
            normalized_collisions,
            self._active_collisions,
            delta_time,
            self._exited_collisions,
        )

        # Traiter les triggers
        self._update_category(
            normalized_triggers,
            self._active_triggers,
            delta_time,
            self._exited_triggers,
        )

    def _update_category(
        self,
        current: Set[Tuple[int, int]],
        active: Dict[Tuple[int, int], float],
        delta_time: float,
        exited_store: Set[Tuple[int, int]],
    ) -> None:
        """
        Met à jour une catégorie de collisions (collisions ou triggers).

        Parameters
        ----------
        current : Set[Tuple[int, int]]
            Ensemble des paires actives cette frame
        active : Dict[Tuple[int, int], float]
            Dictionnaire des paires actives de la catégorie avec durée en secondes
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes
        exited_store : Set[Tuple[int, int]]
            Ensemble dans lequel stocker les paires sorties cette frame
        """
        # Détecter les nouvelles entrées
        for pair in current:
            if pair not in active:
                self._entered_this_frame.add(pair)
                active[pair] = delta_time
            else:
                active[pair] += delta_time

        # Détecter les sorties
        pairs_to_remove = []
        for pair in active:
            if pair not in current:
                self._exited_this_frame.add(pair)
                exited_store.add(pair)
                pairs_to_remove.append(pair)

        # Retirer les paires inactives
        for pair in pairs_to_remove:
            del active[pair]

    def is_collision_active(self, col1_id: int, col2_id: int) -> bool:
        """
        Vérifie si une collision est active entre deux colliders.

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        bool
            True si la collision est active
        """
        pair = self._normalize_pair(col1_id, col2_id)
        return pair in self._active_collisions

    def is_trigger_active(self, col1_id: int, col2_id: int) -> bool:
        """
        Vérifie si un trigger est actif entre deux colliders.

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        bool
            True si le trigger est actif
        """
        pair = self._normalize_pair(col1_id, col2_id)
        return pair in self._active_triggers

    def did_enter(self, col1_id: int, col2_id: int) -> bool:
        """
        Vérifie si une collision/trigger vient de commencer cette frame.

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        bool
            True si la collision vient de commencer
        """
        pair = self._normalize_pair(col1_id, col2_id)
        return pair in self._entered_this_frame

    def did_exit(self, col1_id: int, col2_id: int) -> bool:
        """
        Vérifie si une collision/trigger vient de se terminer cette frame.

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        bool
            True si la collision vient de se terminer
        """
        pair = self._normalize_pair(col1_id, col2_id)
        return pair in self._exited_this_frame

    def get_all_collisions(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions actives.

        Returns
        -------
        set[Tuple[int, int]]
            Liste des paires d'IDs en collision
        """
        return set(self._active_collisions.keys())

    def get_all_triggers(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de tous les triggers actifs.

        Returns
        -------
        set[Tuple[int, int]]
            Liste des paires d'IDs en trigger
        """
        return set(self._active_triggers.keys())

    def get_all_entered(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions/triggers commencées cette frame.

        Returns
        -------
        set[Tuple[int, int]]
            Liste des paires d'IDs qui viennent d'entrer en interaction
        """
        return self._entered_this_frame

    def get_all_exited(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions/triggers terminées cette frame.

        Returns
        -------
        set[Tuple[int, int]]
            Liste des paires d'IDs qui viennent de quitter l'interaction
        """
        return self._exited_this_frame

    def get_all_exited_collisions(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions terminées cette frame.

        Returns
        -------
        set[Tuple[int, int]]
            Liste des paires d'IDs qui viennent de quitter une collision
        """
        return self._exited_collisions

    def get_all_exited_triggers(self) -> set[Tuple[int, int]]:
        """
        Retourne la liste de tous les triggers terminés cette frame.

        Returns
        -------
        List[Tuple[int, int]]
            Liste des paires d'IDs qui viennent de quitter un trigger
        """
        return self._exited_triggers

    def get_collision_duration(self, col1_id: int, col2_id: int) -> Optional[float]:
        """
        Retourne la durée d'une collision en secondes.

        Parameters
        ----------
        col1_id : int
            ID du premier collider
        col2_id : int
            ID du second collider

        Returns
        -------
        Optional[float]
            Durée de la collision en secondes, None si pas active
        """
        pair = self._normalize_pair(col1_id, col2_id)
        return self._active_collisions.get(pair)

    def get_colliding_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders en collision avec le collider spécifié.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders en collision avec col_id
        """
        result = set()
        for pair in self._active_collisions:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def get_triggering_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders en trigger avec le collider spécifié.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders en trigger avec col_id
        """
        result = set()
        for pair in self._active_triggers:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def get_entered_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders qui viennent d'entrer en collision/trigger
        avec le collider spécifié cette frame.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders qui viennent d'entrer en interaction
        """
        result = set()
        for pair in self._entered_this_frame:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def get_exited_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders qui viennent de quitter la collision/trigger
        avec le collider spécifié cette frame.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders qui viennent de quitter l'interaction
        """
        result = set()
        for pair in self._exited_this_frame:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def get_exited_collision_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders qui viennent de quitter une collision
        avec le collider spécifié cette frame.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders qui viennent de quitter une collision
        """
        result = set()
        for pair in self._exited_collisions:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def get_exited_trigger_colliders(self, col_id: int) -> set[int]:
        """
        Retourne la liste des colliders qui viennent de quitter un trigger
        avec le collider spécifié cette frame.

        Parameters
        ----------
        col_id : int
            ID du collider

        Returns
        -------
        set[int]
            Liste des IDs de colliders qui viennent de quitter un trigger
        """
        result = set()
        for pair in self._exited_triggers:
            if pair[0] == col_id:
                result.add(pair[1])
            elif pair[1] == col_id:
                result.add(pair[0])
        return result

    def clear(self):
        """Réinitialise complètement le tracker."""
        self._active_collisions.clear()
        self._active_triggers.clear()
        self._entered_this_frame.clear()
        self._exited_this_frame.clear()
        self._exited_collisions.clear()
        self._exited_triggers.clear()
