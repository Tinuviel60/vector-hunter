from typing import Dict, Set, Tuple, Optional, List

"""Module de tracking des collisions entre objets du jeu."""


class CollisionTracker:
    """
    Gestionnaire de suivi des collisions entre objets.

    Cette classe suit les collisions et triggers entre frames pour détecter
    les événements on_enter, on_exit et on_stay.

    Attributes
    ----------
    _active_collisions : Dict[Tuple[int, int], float]
        Dictionnaire des collisions actives.
        Le couple d'objets est la clé, la valeur est le temps écoulé en secondes.
    _active_triggers : Dict[Tuple[int, int], float]
        Dictionnaire des triggers actifs.
        Le couple d'objets est la clé, la valeur est le temps écoulé en secondes.
    _entered_this_frame : Set[Tuple[int, int]]
        Ensemble des nouvelles collisions détectées cette frame
    _exited_this_frame : Set[Tuple[int, int]]
        Ensemble des collisions terminées cette frame

    Notes
    -----
    Les paires d'IDs sont toujours stockées dans l'ordre (min_id, max_id)
    pour éviter les doublons.
    """

    def __init__(self):
        """Initialise le tracker de collisions."""
        self._active_collisions: Dict[Tuple[int, int], float] = {}
        self._active_triggers: Dict[Tuple[int, int], float] = {}
        self._entered_this_frame: Set[Tuple[int, int]] = set()
        self._exited_this_frame: Set[Tuple[int, int]] = set()
        self._collision_info: Dict[Tuple[int, int], dict] = {}

    def _normalize_pair(self, obj1_id: int, obj2_id: int) -> Tuple[int, int]:
        """
        Normalise une paire d'IDs pour assurer l'ordre (min, max).

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        Tuple[int, int]
            Paire d'IDs ordonnée
        """
        return (min(obj1_id, obj2_id), max(obj1_id, obj2_id))

    def update(
        self,
        current_collisions: Set[Tuple[int, int]],
        current_triggers: Set[Tuple[int, int]],
        collision_info: Dict[Tuple[int, int], dict],
        delta_time: float,
    ):
        """
        Met à jour le tracking des collisions pour la frame courante.

        Parameters
        ----------
        current_collisions : Set[Tuple[int, int]]
            Ensemble des collisions détectées cette frame
        current_triggers : Set[Tuple[int, int]]
            Ensemble des triggers détectés cette frame
        collision_info : Dict[Tuple[int, int], dict]
            Dictionnaire des informations de collision pour chaque paire
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes
        """
        # Réinitialiser les événements de la frame
        self._entered_this_frame.clear()
        self._exited_this_frame.clear()

        # Séparer et normaliser les paires, construire le mapping infos
        self._collision_info.clear()
        normalized_collisions = set()

        for pair in current_collisions:
            norm_pair = self._normalize_pair(*pair)
            normalized_collisions.add(norm_pair)
            info = collision_info.get(pair)
            if info is None:
                info = collision_info.get((pair[1], pair[0]))
            if info is not None:
                self._collision_info[norm_pair] = info

        normalized_triggers = {self._normalize_pair(*pair) for pair in current_triggers}

        # Traiter les collisions
        self._update_category(
            normalized_collisions, self._active_collisions, delta_time
        )

        # Traiter les triggers
        self._update_category(normalized_triggers, self._active_triggers, delta_time)

    def _update_category(
        self,
        current: Set[Tuple[int, int]],
        active: Dict[Tuple[int, int], float],
        delta_time: float,
    ):
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
                pairs_to_remove.append(pair)

        # Retirer les paires inactives
        for pair in pairs_to_remove:
            del active[pair]

    def is_collision_active(self, obj1_id: int, obj2_id: int) -> bool:
        """
        Vérifie si une collision est active entre deux objets.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        bool
            True si la collision est active
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return pair in self._active_collisions

    def is_trigger_active(self, obj1_id: int, obj2_id: int) -> bool:
        """
        Vérifie si un trigger est actif entre deux objets.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        bool
            True si le trigger est actif
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return pair in self._active_triggers

    def did_enter(self, obj1_id: int, obj2_id: int) -> bool:
        """
        Vérifie si une collision/trigger vient de commencer cette frame.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        bool
            True si la collision vient de commencer
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return pair in self._entered_this_frame

    def did_exit(self, obj1_id: int, obj2_id: int) -> bool:
        """
        Vérifie si une collision/trigger vient de se terminer cette frame.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        bool
            True si la collision vient de se terminer
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return pair in self._exited_this_frame

    def get_all_collisions(self) -> List[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions actives.

        Returns
        -------
        List[Tuple[int, int]]
            Liste des paires d'IDs en collision
        """
        return list(self._active_collisions.keys())

    def get_all_triggers(self) -> List[Tuple[int, int]]:
        """
        Retourne la liste de tous les triggers actifs.

        Returns
        -------
        List[Tuple[int, int]]
            Liste des paires d'IDs en trigger
        """
        return list(self._active_triggers.keys())

    def get_collision_info(self, obj1_id: int, obj2_id: int) -> Optional[dict]:
        """
        Retourne les informations de collision pour une paire d'objets.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        Optional[dict]
            Dictionnaire des informations de collision, ou None si pas active
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return self._collision_info.get(pair)

    def get_all_entered(self) -> List[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions/triggers commencées cette frame.

        Returns
        -------
        List[Tuple[int, int]]
            Liste des paires d'IDs qui viennent d'entrer en interaction
        """
        return list(self._entered_this_frame)

    def get_all_exited(self) -> List[Tuple[int, int]]:
        """
        Retourne la liste de toutes les collisions/triggers terminées cette frame.

        Returns
        -------
        List[Tuple[int, int]]
            Liste des paires d'IDs qui viennent de quitter l'interaction
        """
        return list(self._exited_this_frame)

    def get_collision_duration(self, obj1_id: int, obj2_id: int) -> Optional[float]:
        """
        Retourne la durée d'une collision en secondes.

        Parameters
        ----------
        obj1_id : int
            ID du premier objet
        obj2_id : int
            ID du second objet

        Returns
        -------
        Optional[float]
            Durée de la collision en secondes, None si pas active
        """
        pair = self._normalize_pair(obj1_id, obj2_id)
        return self._active_collisions.get(pair)

    def get_colliding_objects(self, obj_id: int) -> List[int]:
        """
        Retourne la liste des objets en collision avec l'objet spécifié.

        Parameters
        ----------
        obj_id : int
            ID de l'objet

        Returns
        -------
        List[int]
            Liste des IDs d'objets en collision avec obj_id
        """
        result = []
        for pair in self._active_collisions:
            if pair[0] == obj_id:
                result.append(pair[1])
            elif pair[1] == obj_id:
                result.append(pair[0])
        return result

    def get_triggering_objects(self, obj_id: int) -> List[int]:
        """
        Retourne la liste des objets en trigger avec l'objet spécifié.

        Parameters
        ----------
        obj_id : int
            ID de l'objet

        Returns
        -------
        List[int]
            Liste des IDs d'objets en trigger avec obj_id
        """
        result = []
        for pair in self._active_triggers:
            if pair[0] == obj_id:
                result.append(pair[1])
            elif pair[1] == obj_id:
                result.append(pair[0])
        return result

    def get_entered_objects(self, obj_id: int) -> List[int]:
        """
        Retourne la liste des objets qui viennent d'entrer en collision/trigger
        avec l'objet spécifié cette frame.

        Parameters
        ----------
        obj_id : int
            ID de l'objet

        Returns
        -------
        List[int]
            Liste des IDs d'objets qui viennent d'entrer en interaction
        """
        result = []
        for pair in self._entered_this_frame:
            if pair[0] == obj_id:
                result.append(pair[1])
            elif pair[1] == obj_id:
                result.append(pair[0])
        return result

    def get_exited_objects(self, obj_id: int) -> List[int]:
        """
        Retourne la liste des objets qui viennent de quitter la collision/trigger
        avec l'objet spécifié cette frame.

        Parameters
        ----------
        obj_id : int
            ID de l'objet

        Returns
        -------
        List[int]
            Liste des IDs d'objets qui viennent de quitter l'interaction
        """
        result = []
        for pair in self._exited_this_frame:
            if pair[0] == obj_id:
                result.append(pair[1])
            elif pair[1] == obj_id:
                result.append(pair[0])
        return result

    def clear(self):
        """Réinitialise complètement le tracker."""
        self._active_collisions.clear()
        self._active_triggers.clear()
        self._entered_this_frame.clear()
        self._exited_this_frame.clear()
