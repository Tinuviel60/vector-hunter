from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Union

from vect_hunt.core import Vector2D

"""Définition des types d'actions d'input."""


class ActionType(Enum):
    """
    Types d'actions possibles dans l'Input System.

    Attributes
    ----------
    BOOL : ActionType
        Action booléenne (pressée ou non).
    FLOAT : ActionType
        Action à valeur scalaire continue.
    VECTOR2D : ActionType
        Action vectorielle à deux dimensions.
    """

    BOOL = auto()
    FLOAT = auto()
    VECTOR2D = auto()


@dataclass
class InputAction:
    """
    Définit une action d'input avec son type et ses paramètres.

    Notes
    -----
    Pour VECTOR2D avec clavier, keys est un dict {'up': [...], 'down': [...], 'left': [...], 'right': [...]}.
    Pour les autres types, keys est une liste de touches.
    """

    name: str
    action_type: ActionType
    keys: Optional[Union[List[str], Dict[str, List[str]]]] = None
    mouse_buttons: Optional[List[str]] = None
    mouse_delta: bool = False
    mouse_position: bool = False
    mouse_wheel: bool = False
    normalize: bool = False
    sensitivity: float = 1.0
    modifiers: Optional[List[str]] = None
    description: str = ""

    def __post_init__(self):
        """Initialise les valeurs par défaut."""
        if self.keys is None:
            self.keys = [] if self.action_type != ActionType.VECTOR2D else {}
        if self.mouse_buttons is None:
            self.mouse_buttons = []
        if self.modifiers is None:
            self.modifiers = []


@dataclass
class ActionState:
    """
    État actuel d'une action pour une frame.

    Notes
    -----
    Seule la valeur correspondant au type de l'action est significative.
    """

    action_name: str
    action_type: ActionType
    bool_value: bool = False
    float_value: float = 0.0
    vector_value: Optional[Vector2D] = None

    def __post_init__(self):
        """Initialise les valeurs par défaut."""
        if self.vector_value is None:
            self.vector_value = Vector2D(0.0, 0.0)

    @property
    def is_active(self) -> bool:
        """
        Vérifie si l'action a une valeur significative.

        Returns
        -------
        bool
            True si active, False sinon.
        """
        if self.action_type == ActionType.BOOL:
            return self.bool_value
        elif self.action_type == ActionType.FLOAT:
            return abs(self.float_value) > 0.001
        elif self.action_type == ActionType.VECTOR2D:
            return (
                self.vector_value is not None and self.vector_value.magnitude() > 0.001
            )
        return False

    def reset(self) -> None:
        """
        Réinitialise l'état à ses valeurs par défaut.
        """
        self.bool_value = False
        self.float_value = 0.0
        self.vector_value = Vector2D(0.0, 0.0)


def action_from_config(name: str, config: Dict[str, Any]) -> InputAction:
    """
    Crée une InputAction depuis une configuration JSON.

    Parameters
    ----------
    name : str
        Nom de l'action.
    config : Dict[str, Any]
        Configuration de l'action depuis le JSON.

    Returns
    -------
    InputAction
        L'action configurée.

    Raises
    ------
    ValueError
        Si le type d'action est invalide.
    """
    # Déterminer le type
    type_str = config.get("type", "bool").lower()
    if type_str == "bool":
        action_type = ActionType.BOOL
    elif type_str == "float":
        action_type = ActionType.FLOAT
    elif type_str == "vector2d":
        action_type = ActionType.VECTOR2D
    else:
        raise ValueError(f"Type d'action invalide : {type_str}")

    # Extraire les paramètres
    return InputAction(
        name=name,
        action_type=action_type,
        keys=config.get("keys", [] if action_type != ActionType.VECTOR2D else {}),
        mouse_buttons=config.get("mouse_buttons", []),
        mouse_delta=config.get("mouse_delta", False),
        mouse_position=config.get("mouse_position", False),
        mouse_wheel=config.get("mouse_wheel", False),
        normalize=config.get("normalize", False),
        sensitivity=config.get("sensitivity", 1.0),
        modifiers=config.get("modifiers", []),
        description=config.get("description", ""),
    )
