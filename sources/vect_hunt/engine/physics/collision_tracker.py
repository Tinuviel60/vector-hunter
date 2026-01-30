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
        # Début : entrées cette frame
        self._entered_collisions: Set[Tuple[int, int]] = set()
        self._entered_triggers: Set[Tuple[int, int]] = set()

        # Milieu : actifs (durée cumulée en secondes)
        self._active_collisions: Dict[Tuple[int, int], float] = {}
        self._active_triggers: Dict[Tuple[int, int], float] = {}

        # Fin : sorties cette frame
        self._exited_collisions: Set[Tuple[int, int]] = set()
        self._exited_triggers: Set[Tuple[int, int]] = set()

    # -------------------------
    # Getters
    # -------------------------

    @property
    def entered_collisions(self) -> Set[Tuple[int, int]] :
        """Paires entrées en collision cette frame (lecture)."""
        return self._entered_collisions
    
    @property
    def entered_triggers(self) -> Set[Tuple[int, int]] :
        """Paires entrées en trigger cette frame (lecture)."""
        return self._entered_triggers
    
    @property
    def active_collisions(self) -> Dict[Tuple[int, int], float]:
        """Paires sorties d'une collision cette frame (lecture)."""
        return self._active_collisions
    
    @property
    def active_triggers(self) -> Dict[Tuple[int, int], float]:
        """Paires sorties d'un trigger cette frame (lecture)."""
        return self._active_triggers
    
    @property
    def exited_collisions(self) -> Set[Tuple[int, int]] :
        """Collisions actives et leur durée cumulée (lecture)."""
        return self._exited_collisions
    
    @property
    def exited_triggers(self) -> Set[Tuple[int, int]] :
        """Triggers actifs et leur durée cumulée (lecture)."""
        return self._exited_triggers
    
    # -------------------------
    # Core
    # -------------------------

    def update(
            self,
            collisions: Set[Tuple[int, int]],
            triggers: Set[Tuple[int, int]],
            delta_time: float,
        ) -> None:
            """
            Met à jour le tracking pour la frame courante.

            Parameters
            ----------
            collisions : Set[Tuple[int, int]]
                Paires de colliders en collision pour cette frame.
            triggers : Set[Tuple[int, int]]
                Paires de colliders en trigger pour cette frame.
            delta_time : float
                Temps de frame (secondes).
            """
            self._entered_collisions.clear()
            self._entered_triggers.clear()
            self._exited_collisions.clear()
            self._exited_triggers.clear()

            normalized_collisions = {self._normalize_pair(a, b) for (a, b) in collisions}
            normalized_triggers = {self._normalize_pair(a, b) for (a, b) in triggers}

            self._update_collision(
                current=normalized_collisions,
                delta_time=delta_time,
            )

            self._update_trigger(
                current=normalized_triggers,
                delta_time=delta_time,
            )

    def _update_collision(
        self,
        current: Set[Tuple[int, int]],
        delta_time: float,
    ) -> None:
        """
        Met à jour les collisions.

        Règles
        ------
        - Si pair ∈ current et pas dans active : entered + durée = delta_time
        - Si pair ∈ current et déjà active : durée += delta_time
        - Si pair ∉ current et dans active : exited + suppression de active
        """
        # Entrées + update durée
        for pair in current:
            if pair not in self._active_collisions:
                self._entered_collisions.add(pair)
                self._active_collisions[pair] = delta_time
            else:
                self._active_collisions[pair] += delta_time
        # Sorties
        to_remove: list[Tuple[int, int]] = []
        for pair in self._active_collisions.keys():
            if pair not in current:
                self._exited_collisions.add(pair)
                to_remove.append(pair)

        for pair in to_remove:
            del self._active_collisions[pair]

    def _update_trigger(
        self,
        current: Set[Tuple[int, int]],
        delta_time: float,
    ) -> None:
        """
        Met à jour les triggers.

        Règles
        ------
        - Si pair ∈ current et pas dans active : entered + durée = delta_time
        - Si pair ∈ current et déjà active : durée += delta_time
        - Si pair ∉ current et dans active : exited + suppression de active
        """
        # Entrées + update durée
        for pair in current:
            if pair not in self._active_triggers:
                self._entered_triggers.add(pair)
                self._active_triggers[pair] = delta_time
            else:
                self._active_triggers[pair] += delta_time
        # Sorties
        to_remove: list[Tuple[int, int]] = []
        for pair in self._active_triggers.keys():
            if pair not in current:
                self._exited_triggers.add(pair)
                to_remove.append(pair)

        for pair in to_remove:
            del self._active_triggers[pair]

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

    def clear(self):
        """Réinitialise complètement le tracker."""
        self._entered_collisions.clear()
        self._entered_triggers.clear()
        self._active_collisions.clear()
        self._active_triggers.clear()
        self._exited_collisions.clear()
        self._exited_triggers.clear()

    # -------------------------
    # Queries utiles
    # -------------------------

    def is_collision_active(self, col1_id: int, col2_id: int) -> bool:
        """Retourne True si la collision est active pour cette paire."""
        return self._normalize_pair(col1_id, col2_id) in self._active_collisions

    def is_trigger_active(self, col1_id: int, col2_id: int) -> bool:
        """Retourne True si le trigger est actif pour cette paire."""
        return self._normalize_pair(col1_id, col2_id) in self._active_triggers

    def get_all_active_collisions(self) -> Set[Tuple[int, int]]:
        """Retourne toutes les collisions actives (paires)."""
        return set(self._active_collisions.keys())

    def get_all_active_triggers(self) -> Set[Tuple[int, int]]:
        """Retourne tous les triggers actifs (paires)."""
        return set(self._active_triggers.keys())

    def get_all_entered_collisions(self) -> Set[Tuple[int, int]]:
        """Retourne les collisions entrées cette frame."""
        return self._entered_collisions

    def get_all_entered_triggers(self) -> Set[Tuple[int, int]]:
        """Retourne les triggers entrés cette frame."""
        return self._entered_triggers

    def get_all_exited_collisions(self) -> Set[Tuple[int, int]]:
        """Retourne les collisions sorties cette frame."""
        return self._exited_collisions

    def get_all_exited_triggers(self) -> Set[Tuple[int, int]]:
        """Retourne les triggers sortis cette frame."""
        return self._exited_triggers

    def get_collision_duration(self, col1_id: int, col2_id: int) -> Optional[float]:
        """Retourne la durée de collision (secondes) ou None si inactive."""
        return self._active_collisions.get(self._normalize_pair(col1_id, col2_id))