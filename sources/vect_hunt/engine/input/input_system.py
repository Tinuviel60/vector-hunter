import pygame
from typing import Dict, Set, Optional, List, Any

from vect_hunt.engine.core.math.vector import Vector2D
from .input_tracker import InputTracker
from vect_hunt.engine.input.input_action import (
    InputAction,
    ActionState,
    ActionType,
    action_from_config,
)
from .context_manager import (
    ContextManager,
    GameContext,
)

"""Système de gestion des entrées utilisateur."""


class InputSystem:
    """
    Système de gestion des entrées utilisateur.

    - Lit les entrées matérielles (clavier, souris)
    - Traduit en actions logiques selon le contexte
    - Maintient l'état temporel (press / hold / release)
    - Retourne des valeurs brutes (sensibilité appliquée par le gameplay)

    Notes
    -----
    Toutes les actions dépendent du contexte actif (GameContext).
    Les actions GLOBAL sont toujours disponibles.

    Attributes
    ----------
    None
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialise le système d'inputs.

        Parameters
        ----------
        config : dict[str, Any]
            Configuration chargee depuis inputs.json.
        """
        self._actions: Dict[str, InputAction] = {}
        self._contexts: Dict[GameContext, List[str]] = {}
        self._context_manager = ContextManager(GameContext.PLAYING)
        self._tracker = InputTracker()
        self._action_states: Dict[str, ActionState] = {}
        self._settings: Dict[str, Any] = {}

        # État souris
        self._mouse_delta = Vector2D(0.0, 0.0)
        self._mouse_position = Vector2D(0.0, 0.0)
        self._mouse_wheel_delta = 0.0
        self._previous_mouse_position = Vector2D(0.0, 0.0)

        # Mapping pygame → noms de touches
        self._pygame_key_mapping = self._build_key_mapping()
        self._pygame_mouse_mapping = {
            1: "LEFT",
            2: "MIDDLE",
            3: "RIGHT",
            4: "WHEEL_UP",
            5: "WHEEL_DOWN",
        }

        # Charger la configuration
        self._load_config(config)

    def _build_key_mapping(self) -> Dict[int, str]:
        """
        Construit le mapping codes pygame vers noms de touches.

        Returns
        -------
        Dict[int, str]
            Mapping code → nom.
        """
        mapping = {}

        # Lettres
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            key_code = getattr(pygame, f"K_{letter.lower()}", None)
            if key_code is not None:
                mapping[key_code] = letter

        # Chiffres
        for num in range(10):
            key_code = getattr(pygame, f"K_{num}", None)
            if key_code is not None:
                mapping[key_code] = str(num)

        # Touches spéciales
        special_keys = {
            pygame.K_SPACE: "SPACE",
            pygame.K_RETURN: "RETURN",
            pygame.K_ESCAPE: "ESCAPE",
            pygame.K_LSHIFT: "LSHIFT",
            pygame.K_RSHIFT: "RSHIFT",
            pygame.K_LCTRL: "LCTRL",
            pygame.K_RCTRL: "RCTRL",
            pygame.K_LALT: "LALT",
            pygame.K_RALT: "RALT",
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_TAB: "TAB",
            pygame.K_BACKSPACE: "BACKSPACE",
            pygame.K_DELETE: "DELETE",
            pygame.K_HOME: "HOME",
            pygame.K_END: "END",
            pygame.K_PAGEUP: "PAGEUP",
            pygame.K_PAGEDOWN: "PAGEDOWN",
            pygame.K_PLUS: "PLUS",
            pygame.K_MINUS: "MINUS",
            pygame.K_EQUALS: "EQUALS",
        }

        # Touches de fonction
        for i in range(1, 13):
            key_code = getattr(pygame, f"K_F{i}", None)
            if key_code is not None:
                mapping[key_code] = f"F{i}"

        mapping.update(special_keys)
        return mapping

    def _load_config(self, config: dict[str, Any]) -> None:
        """
        Charge la configuration depuis le fichier JSON.

        Parameters
        ----------
        config : dict[str, Any]
            Configuration chargee depuis inputs.json.
        """
        # Charger les settings
        self._settings = config.get("settings", {})

        # Charger les contextes et actions
        contexts_data = config.get("contexts", {})
        for context_name, actions_data in contexts_data.items():
            # Créer l'enum de contexte
            try:
                context = GameContext(context_name)
            except ValueError:
                continue

            action_names = []
            for action_name, action_config in actions_data.items():
                if action_name.startswith("_comment"):
                    continue

                # Créer l'action
                action = action_from_config(action_name, action_config)
                self._actions[action_name] = action

                # Créer l'état initial
                self._action_states[action_name] = ActionState(
                    action_name=action_name, action_type=action.action_type
                )

                action_names.append(action_name)

            self._contexts[context] = action_names

    def update(self, delta_time: float) -> None:
        """
        Met à jour le système d'inputs pour la frame courante.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame.
        """
        # Lire l'état du clavier et de la souris
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Calculer le delta de la souris
        current_mouse_position = Vector2D(float(mouse_pos[0]), float(mouse_pos[1]))
        self._mouse_delta = current_mouse_position - self._previous_mouse_position
        self._previous_mouse_position = current_mouse_position
        self._mouse_position = current_mouse_position

        # Réinitialiser le delta de molette (mis à jour dans process_event)
        # On ne le reset pas ici car les events sont traités avant update

        # Réinitialiser les états d'actions
        for state in self._action_states.values():
            state.reset()

        # Récupérer les actions du contexte actif
        active_actions = self._get_active_actions()

        # Évaluer chaque action
        evaluated_actions: Set[str] = set()
        for action_name in active_actions:
            action = self._actions[action_name]
            state = self._action_states[action_name]

            # Évaluer selon le type
            if action.action_type == ActionType.BOOL:
                state.bool_value = self._evaluate_bool_action(
                    action, keys_pressed, mouse_buttons
                )
                if state.bool_value:
                    evaluated_actions.add(action_name)

            elif action.action_type == ActionType.FLOAT:
                state.float_value = self._evaluate_float_action(
                    action, keys_pressed, mouse_buttons
                )
                if abs(state.float_value) > 0.001:
                    evaluated_actions.add(action_name)

            elif action.action_type == ActionType.VECTOR2D:
                state.vector_value = self._evaluate_vector_action(
                    action, keys_pressed, mouse_buttons
                )
                if state.vector_value.magnitude() > 0.001:
                    evaluated_actions.add(action_name)

        # Mettre à jour le tracker
        self._tracker.update(evaluated_actions, delta_time)

        # Réinitialiser le delta de molette après évaluation
        self._mouse_wheel_delta = 0.0

    def process_event(self, event: pygame.event.Event) -> None:
        """
        Traite un événement pygame.

        Parameters
        ----------
        event : pygame.event.Event
            L'événement à traiter.
        """
        if event.type == pygame.MOUSEWHEEL:
            self._mouse_wheel_delta += float(event.y)

    def _get_active_actions(self) -> List[str]:
        """
        Retourne les actions disponibles dans le contexte actuel.

        Returns
        -------
        List[str]
            Noms des actions (GLOBAL + contexte actif).
        """
        actions = []

        # Toujours inclure les actions globales
        if GameContext.GLOBAL in self._contexts:
            actions.extend(self._contexts[GameContext.GLOBAL])

        # Ajouter les actions du contexte actif
        active_context = self._context_manager.get_context()
        if active_context in self._contexts:
            actions.extend(self._contexts[active_context])

        return actions

    def _evaluate_bool_action(
        self,
        action: InputAction,
        keys_pressed: pygame.key.ScancodeWrapper,
        mouse_buttons: tuple,
    ) -> bool:
        """
        Évalue une action booléenne.

        Parameters
        ----------
        action : InputAction
            L'action à évaluer.
        keys_pressed : pygame.key.ScancodeWrapper
            État des touches du clavier.
        mouse_buttons : tuple
            État des boutons de la souris.

        Returns
        -------
        bool
            True si l'action est active, False sinon.
        """
        # Vérifier les modificateurs (n'importe quelle touche)
        if action.modifiers and not self._check_modifiers(
            action.modifiers, keys_pressed
        ):
            return False

        # Vérifier les touches clavier
        if isinstance(action.keys, list):
            for key_name in action.keys:
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    return True

        # Vérifier les boutons souris
        if action.mouse_buttons:
            for button_name in action.mouse_buttons:
                button_index = self._get_mouse_button_index(button_name)
                if button_index is not None and button_index < len(mouse_buttons):
                    if mouse_buttons[button_index]:
                        return True

        return False

    def _evaluate_float_action(
        self,
        action: InputAction,
        keys_pressed: pygame.key.ScancodeWrapper,
        mouse_buttons: tuple,
    ) -> float:
        """
        Évalue une action scalaire (float).

        Parameters
        ----------
        action : InputAction
            L'action à évaluer.
        keys_pressed : pygame.key.ScancodeWrapper
            État des touches du clavier.
        mouse_buttons : tuple
            État des boutons de la souris.

        Returns
        -------
        float
            Valeur brute de l'action (sans sensibilité appliquée).
        """
        # Vérifier les modificateurs (n'importe quelle touche)
        if action.modifiers and not self._check_modifiers(
            action.modifiers, keys_pressed
        ):
            return 0.0

        value = 0.0

        # Molette de souris (valeur brute : -1, 0, +1)
        if action.mouse_wheel:
            value = self._mouse_wheel_delta

        # Touches clavier (0 ou 1)
        if isinstance(action.keys, list):
            for key_name in action.keys:
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    value = 1.0
                    break

        return value

    # TODO : revoir cette méthode pour gérer les orgine des vecteurs
    def _evaluate_vector_action(
        self,
        action: InputAction,
        keys_pressed: pygame.key.ScancodeWrapper,
        mouse_buttons: tuple,
    ) -> Vector2D:
        """
        Évalue une action vectorielle (Vector2D).

        Parameters
        ----------
        action : InputAction
            L'action à évaluer.
        keys_pressed : pygame.key.ScancodeWrapper
            État des touches du clavier.
        mouse_buttons : tuple
            État des boutons de la souris.

        Returns
        -------
        Vector2D
            Valeur vectorielle de l'action.
        """
        # Vérifier les modificateurs (n'importe quelle touche)
        if action.modifiers and not self._check_modifiers(
            action.modifiers, keys_pressed
        ):
            return Vector2D(0.0, 0.0)

        vector = Vector2D(0.0, 0.0)

        # Delta souris (valeur brute, sensibilité à appliquer côté gameplay)
        if action.mouse_delta:
            return self._mouse_delta

        # Position souris
        if action.mouse_position:
            return self._mouse_position

        # Touches clavier (directionnelles)
        if isinstance(action.keys, dict):
            # Format : {"up": ["W", "Z"], "down": ["S"], ...}
            x_input = 0.0
            y_input = 0.0

            for key_name in action.keys.get("right", []):
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    x_input += 1.0

            for key_name in action.keys.get("left", []):
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    x_input -= 1.0

            for key_name in action.keys.get("down", []):
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    y_input += 1.0

            for key_name in action.keys.get("up", []):
                pygame_key = self._get_pygame_key(key_name)
                if pygame_key is not None and keys_pressed[pygame_key]:
                    y_input -= 1.0

            vector = Vector2D(x_input, y_input)

            # Normaliser si demandé
            if action.normalize and vector.magnitude() > 0.0:
                vector = vector.normalized()

        return vector

    def _get_pygame_key(self, key_name: str) -> Optional[int]:
        """
        Convertit un nom de touche en code pygame.

        Parameters
        ----------
        key_name : str
            Nom de la touche.

        Returns
        -------
        Optional[int]
            Code pygame de la touche, ou None si introuvable.
        """
        # Chercher dans le mapping inversé
        for code, name in self._pygame_key_mapping.items():
            if name == key_name:
                return code
        return None

    def _check_modifiers(
        self, modifiers: List[str], keys_pressed: pygame.key.ScancodeWrapper
    ) -> bool:
        """
        Vérifie si toutes les touches modificatrices sont actives.

        Système flexible : accepte n'importe quelle touche comme modificateur.

        Parameters
        ----------
        modifiers : List[str]
            Liste des touches qui doivent être pressées simultanément.
        keys_pressed : pygame.key.ScancodeWrapper
            État des touches du clavier.

        Returns
        -------
        bool
            True si toutes les touches modificatrices sont actives, False sinon.

        Examples
        --------
        modifiers = ["O", "LSHIFT"]  # O + Shift doivent être pressés
        modifiers = ["U", "E"]        # U + E doivent être pressés
        """
        if not modifiers:
            return True

        # Vérifier que toutes les touches modificatrices sont pressées
        for modifier_key in modifiers:
            pygame_key = self._get_pygame_key(modifier_key)
            if pygame_key is None or not keys_pressed[pygame_key]:
                return False

        return True

    def _get_mouse_button_index(self, button_name: str) -> Optional[int]:
        """
        Convertit un nom de bouton souris en index.

        Parameters
        ----------
        button_name : str
            Nom du bouton souris.

        Returns
        -------
        Optional[int]
            Index du bouton (0-indexed pour pygame), ou None si introuvable.
        """
        for code, name in self._pygame_mouse_mapping.items():
            if name == button_name:
                # pygame.mouse.get_pressed() retourne 0-indexed
                return code - 1
        return None

    # --------------------
    # API publique pour les GameObjects
    # --------------------

    def is_pressed(self, action_name: str) -> bool:
        """
        Vérifie si une action vient d'être pressée cette frame.

        Détecte la transition OFF → ON (première frame uniquement).

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        bool
            True si pressée cette frame, False sinon.

        Notes
        -----
        Dépend du contexte actif (GameContext).
        Pour tester l'état actif continu, utiliser is_held() ou get_bool().
        """
        return self._tracker.is_pressed(action_name)

    def is_held(self, action_name: str) -> bool:
        """
        Vérifie si une action est maintenue.

        Inclut la frame de pressed (première frame).

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        bool
            True si active, False sinon.

        Notes
        -----
        Dépend du contexte actif (GameContext).
        """
        return self._tracker.is_held(action_name)

    def is_released(self, action_name: str) -> bool:
        """
        Vérifie si une action vient d'être relâchée cette frame.

        Détecte la transition ON → OFF (frame de relâchement).

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        bool
            True si relâchée cette frame, False sinon.

        Notes
        -----
        Dépend du contexte actif (GameContext).
        Déclenché aussi si les modifiers ne sont plus valides.
        """
        return self._tracker.is_released(action_name)

    def get_hold_duration(self, action_name: str) -> float:
        """
        Retourne la durée de maintien d'une action.

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        float
            Durée en secondes.
        """
        return self._tracker.get_hold_duration(action_name)

    def get_bool(self, action_name: str) -> bool:
        """
        Retourne la valeur booléenne d'une action.

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        bool
            True si active (pressed ou held), False sinon.

        Notes
        -----
        Dépend du contexte actif (GameContext).
        """
        if action_name not in self._action_states:
            return False
        return self._action_states[action_name].bool_value

    def get_float(self, action_name: str) -> float:
        """
        Retourne la valeur scalaire d'une action.

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        float
            Valeur brute (sensibilité non appliquée).

        Notes
        -----
        Dépend du contexte actif (GameContext).
        """
        if action_name not in self._action_states:
            return 0.0
        return self._action_states[action_name].float_value

    def get_vector(self, action_name: str) -> Vector2D:
        """
        Retourne la valeur vectorielle d'une action.

        Parameters
        ----------
        action_name : str
            Nom de l'action.

        Returns
        -------
        Vector2D
            Vecteur (sensibilité non appliquée).

        Notes
        -----
        Dépend du contexte actif (GameContext).
        """
        if action_name not in self._action_states:
            return Vector2D(0.0, 0.0)
        vector = self._action_states[action_name].vector_value
        return vector if vector is not None else Vector2D(0.0, 0.0)

    def get_mouse_position(self) -> Vector2D:
        """
        Retourne la position absolue de la souris.

        Returns
        -------
        Vector2D
            Position en pixels.
        """
        return self._mouse_position

    def get_mouse_delta(self) -> Vector2D:
        """
        Retourne le déplacement de la souris depuis la frame précédente.

        Returns
        -------
        Vector2D
            Delta en pixels.
        """
        return self._mouse_delta

    # --------------------
    # Gestion des contextes
    # --------------------

    def set_context(self, context: GameContext) -> None:
        """
        Change le contexte actif (remplace la pile).

        Parameters
        ----------
        context : GameContext
            Le nouveau contexte.
        """
        self._context_manager.set_context(context)
        self._tracker.reset()

    def push_context(self, context: GameContext) -> None:
        """
        Empile un nouveau contexte.

        Parameters
        ----------
        context : GameContext
            Le contexte à empiler.
        """
        self._context_manager.push_context(context)

    def pop_context(self) -> Optional[GameContext]:
        """
        Dépile le contexte actuel.

        Returns
        -------
        Optional[GameContext]
            Le contexte dépilé, ou None si pile minimale.
        """
        return self._context_manager.pop_context()

    def get_context(self) -> GameContext:
        """
        Retourne le contexte actif.

        Returns
        -------
        GameContext
            Le contexte au sommet de la pile.
        """
        return self._context_manager.get_context()

    def reset(self) -> None:
        """
        Réinitialise le système d'inputs.
        """
        self._tracker.reset()
        for state in self._action_states.values():
            state.reset()
        self._mouse_delta = Vector2D(0.0, 0.0)
        self._mouse_wheel_delta = 0.0
