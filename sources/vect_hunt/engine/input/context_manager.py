from typing import List, Optional
from enum import Enum

"""Gestionnaire de contextes de jeu."""


class GameContext(Enum):
    """
    Contextes de jeu disponibles.

    Attributes
    ----------
    GLOBAL : GameContext
        Actions disponibles dans tous les contextes.
    MENU : GameContext
        Actions pour la navigation dans les menus.
    PLAYING : GameContext
        Actions pendant le gameplay.
    """

    GLOBAL = "global"
    MENU = "menu"
    PLAYING = "playing"


class ContextManager:
    """
    Gestionnaire de pile de contextes de jeu.

    - Empile/dépile des contextes (ex: pause par-dessus playing)
    - Utilisé par Input, Renderer, Audio, etc.

    Notes
    -----
    Le contexte GLOBAL est toujours actif, indépendamment de la pile.

    Attributes
    ----------
    None
    """

    def __init__(self, initial_context: GameContext = GameContext.PLAYING):
        """
        Initialise le gestionnaire avec un contexte initial.

        Parameters
        ----------
        initial_context : GameContext
            Contexte de départ.
        """
        self._context_stack: List[GameContext] = [initial_context]
        self._active_context: GameContext = initial_context

    def set_context(self, context: GameContext) -> None:
        """
        Remplace la pile par un seul contexte.

        Parameters
        ----------
        context : GameContext
            Le nouveau contexte.
        """
        self._context_stack = [context]
        self._active_context = context

    def push_context(self, context: GameContext) -> None:
        """
        Empile un contexte par-dessus le contexte actuel.

        Parameters
        ----------
        context : GameContext
            Le contexte à empiler.
        """
        self._context_stack.append(context)
        self._active_context = context

    def pop_context(self) -> Optional[GameContext]:
        """
        Dépile le contexte actuel.

        Returns
        -------
        Optional[GameContext]
            Le contexte dépilé, ou None si pile minimale.

        Notes
        -----
        La pile ne peut jamais être vide (minimum 1 contexte).
        """
        if len(self._context_stack) > 1:
            popped = self._context_stack.pop()
            self._active_context = self._context_stack[-1]
            return popped
        return None

    def get_context(self) -> GameContext:
        """
        Retourne le contexte actif.

        Returns
        -------
        GameContext
            Le contexte au sommet de la pile.
        """
        return self._active_context

    def get_stack_size(self) -> int:
        """
        Retourne la taille de la pile de contextes.

        Returns
        -------
        int
            Nombre de contextes dans la pile.
        """
        return len(self._context_stack)

    def clear_stack(self, new_context: GameContext) -> None:
        """
        Vide la pile et définit un nouveau contexte unique.

        Parameters
        ----------
        new_context : GameContext
            Le contexte qui deviendra le seul dans la pile.
        """
        self._context_stack = [new_context]
        self._active_context = new_context
