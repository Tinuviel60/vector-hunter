from typing import Dict, Set

"""Module de tracking des états d'inputs entre frames."""


class InputTracker:
    """
    Gestionnaire de suivi des états d'inputs entre frames.

    Cette classe suit les actions actives entre frames pour détecter
    les événements on_press, on_hold et on_release.

    Similaire au CollisionTracker, mais pour les actions d'input.

    Attributes
    ----------
    _active_actions : Dict[str, float]
        Dictionnaire des actions actives.
        La clé est le nom de l'action, la valeur est le temps maintenu en secondes.
    _pressed_this_frame : Set[str]
        Ensemble des nouvelles actions pressées cette frame.
    _released_this_frame : Set[str]
        Ensemble des actions relâchées cette frame.

    Notes
    -----
    Une action passe par trois états possibles :
    - on_press : transition OFF → ON (première frame)
    - on_hold : maintenu (frames suivantes tant que l'action est active)
    - on_release : transition ON → OFF (frame de relâchement)

    Attributes
    ----------
    None
    """

    def __init__(self):
        """Initialise le tracker d'inputs."""
        self._active_actions: Dict[str, float] = {}
        self._pressed_this_frame: Set[str] = set()
        self._released_this_frame: Set[str] = set()

    def update(self, current_actions: Set[str], delta_time: float) -> None:
        """
        Met à jour le tracking des actions pour la frame courante.

        Parameters
        ----------
        current_actions : Set[str]
            Ensemble des actions actives détectées cette frame.
        delta_time : float
            Temps écoulé depuis la dernière frame en secondes.
        """
        # Réinitialiser les événements de la frame
        self._pressed_this_frame.clear()
        self._released_this_frame.clear()

        # Détecter les nouvelles actions (on_press)
        for action in current_actions:
            if action not in self._active_actions:
                # Nouvelle action pressée
                self._active_actions[action] = 0.0
                self._pressed_this_frame.add(action)
            else:
                # Action maintenue, incrémenter le temps
                self._active_actions[action] += delta_time

        # Détecter les actions relâchées (on_release)
        released = set(self._active_actions.keys()) - current_actions
        for action in released:
            self._released_this_frame.add(action)
            del self._active_actions[action]

    def is_pressed(self, action: str) -> bool:
        """
        Vérifie si une action vient d'être pressée cette frame.

        Parameters
        ----------
        action : str
            Nom de l'action à vérifier.

        Returns
        -------
        bool
            True si l'action vient d'être pressée, False sinon.
        """
        return action in self._pressed_this_frame

    def is_held(self, action: str) -> bool:
        """
        Vérifie si une action est maintenue.

        Parameters
        ----------
        action : str
            Nom de l'action à vérifier.

        Returns
        -------
        bool
            True si l'action est maintenue (active), False sinon.
        """
        return action in self._active_actions

    def is_released(self, action: str) -> bool:
        """
        Vérifie si une action vient d'être relâchée cette frame.

        Parameters
        ----------
        action : str
            Nom de l'action à vérifier.

        Returns
        -------
        bool
            True si l'action vient d'être relâchée, False sinon.
        """
        return action in self._released_this_frame

    def get_hold_duration(self, action: str) -> float:
        """
        Retourne le temps pendant lequel une action est maintenue.

        Parameters
        ----------
        action : str
            Nom de l'action.

        Returns
        -------
        float
            Durée en secondes, ou 0.0 si l'action n'est pas active.
        """
        return self._active_actions.get(action, 0.0)

    def reset(self) -> None:
        """
        Réinitialise complètement le tracker.

        Utile lors de la perte de focus ou changement de contexte.
        """
        self._active_actions.clear()
        self._pressed_this_frame.clear()
        self._released_this_frame.clear()

    def get_all_active(self) -> Set[str]:
        """
        Retourne l'ensemble de toutes les actions actuellement actives.

        Returns
        -------
        Set[str]
            Ensemble des noms d'actions actives.
        """
        return set(self._active_actions.keys())

    def get_all_pressed(self) -> Set[str]:
        """
        Retourne l'ensemble des actions pressées cette frame.

        Returns
        -------
        Set[str]
            Ensemble des noms d'actions pressées.
        """
        return self._pressed_this_frame.copy()

    def get_all_released(self) -> Set[str]:
        """
        Retourne l'ensemble des actions relâchées cette frame.

        Returns
        -------
        Set[str]
            Ensemble des noms d'actions relâchées.
        """
        return self._released_this_frame.copy()
