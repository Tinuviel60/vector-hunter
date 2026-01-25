from dataclasses import dataclass
from enum import Enum
from logging import getLogger

from vect_hunt.engine.core.math.numeric import Numeric

logger = getLogger(__name__)


class CombineMode(Enum):
    """
    Enumération des modes de combinaison des propriétés physiques.
    Ils sont classés par priorité.

    Attributes
    ----------
    MIN : CombineMode
        Utilise la valeur minimale des deux matériaux.
    AVERAGE : CombineMode
        Utilise la moyenne des deux valeurs.
    MULTIPLY : CombineMode
        Multiplie les deux valeurs.
    MAX : CombineMode
        Utilise la valeur maximale des deux matériaux.
    priority : int
        Priorité de combinaison (plus grand = plus prioritaire).
    """

    MIN = 1
    AVERAGE = 2
    MULTIPLY = 3
    MAX = 4

    @property
    def priority(self) -> int:
        return self.value


@dataclass(slots=True)
class PhysicMaterial:
    """
    Classe représentant les propriétés physiques d'un matériau.

    Parameters
    ----------
    friction : float, optional
        Coefficient de friction (0.0 à 1.0).
        Correspond à la résistance au glissement entre surfaces.
        Par défaut 0.6.
    restitution : float, optional
        Coefficient de restitution (0.0 à 1.0).
        Correspond à la restitution d'énergie lors des collisions.
        Par défaut 0.0.
    friction_mode : CombineMode, optional
        Mode de combinaison de la friction entre deux matériaux.
        Par défaut CombineMode.MAX.
    restitution_mode : CombineMode, optional
        Mode de combinaison de la restitution entre deux matériaux.
        Par défaut CombineMode.MIN.
    linear_damping : float, optional
        Amortissement linéaire (0.0 à 1.0).
        Correspond à la perte de vélocité au fil du temps.
        Par défaut 0.0.
    anglular_damping : float, optional
        Amortissement angulaire (0.0 à 1.0).
        Correspond à la perte de vitesse angulaire au fil du temps.
        Par défaut 0.0.
    bounce_velocity_threshold : float, optional
        Vitesse minimale (valeur absolue) pour autoriser un rebond.
        En dessous, la restitution est ignorée.
        Par défaut 10.0.

    Attributes
    ----------
    friction : float
        Coefficient de friction (0.0 à 1.0).
    restitution : float
        Coefficient de restitution (0.0 à 1.0).
    friction_mode : CombineMode
        Mode de combinaison de la friction.
    restitution_mode : CombineMode
        Mode de combinaison de la restitution.
    linear_damping : float
        Amortissement linéaire (0.0 à 1.0).
    angular_damping : float
        Amortissement angulaire (0.0 à 1.0).
    bounce_velocity_threshold : float
        Seuil de vitesse pour autoriser un rebond.
    """

    friction: float = 0.6
    restitution: float = 0.0
    friction_mode: CombineMode = CombineMode.MAX
    restitution_mode: CombineMode = CombineMode.MIN
    linear_damping: float = 0.0
    angular_damping: float = 0.0
    bounce_velocity_threshold: float = 10.0

    # TODO : Nouveau paramètre pour plus tard très probable
    # self.static_friction:
    #   Pour gérer la friction dans le cas où un objet est immobile
    # self.dynamic_friction:
    #   Pour gérer la friction dans le cas où un objet est en mouvement
    # self.angular_damping:

    # TODO : Nouveau paramètre pour plus tard probable
    # self.surface_type:
    #   Pour définir le type de surface (ex: glace, caoutchouc, métal)
    # self.rolling_friction:
    #   Pour gérer la friction de roulement pour les objets sphériques

    def __post_init__(self) -> None:
        """
        Valide et clamp les valeurs des propriétés physiques après l'initialisation.
        """
        if not (0.0 <= self.friction <= 1.0):
            logger.warning(
                f"Friction {self.friction} hors limites, " f"clamp entre 0.0 et 1.0."
            )
            self.friction = Numeric.clamp(self.friction, 0.0, 1.0)
        if not (0.0 <= self.restitution <= 1.0):
            logger.warning(
                f"Restitution {self.restitution} hors limites, "
                f"clamp entre 0.0 et 1.0."
            )
            self.restitution = Numeric.clamp(self.restitution, 0.0, 1.0)
        if not (0.0 <= self.linear_damping <= 1.0):
            logger.warning(
                f"Linear Damping {self.linear_damping} hors limites, "
                f"clamp entre 0.0 et 1.0."
            )
            self.linear_damping = Numeric.clamp(self.linear_damping, 0.0, 1.0)
        if self.bounce_velocity_threshold < 0.0:
            logger.warning(
                f"Bounciness Threshold {self.bounce_velocity_threshold} hors limites, "
                "clamp à 0.0."
            )
            self.bounce_velocity_threshold = 0.0
        if not (0.0 <= self.angular_damping <= 1.0):
            logger.warning(
                f"Angular Damping {self.angular_damping} hors limites, "
                f"clamp entre 0.0 et 1.0."
            )
            self.angular_damping = Numeric.clamp(self.angular_damping, 0.0, 1.0)

    @staticmethod
    def resolve_combine_mode(mode_a: CombineMode, mode_b: CombineMode) -> CombineMode:
        """
        Résout le mode de combinaison à utiliser entre deux matériaux
        en fonction de leur priorité.

        Parameters
        ----------
        mode_a : CombineMode
            Mode de combinaison du premier matériau.
        mode_b : CombineMode
            Mode de combinaison du second matériau.

        Returns
        -------
        CombineMode
            Le mode de combinaison à utiliser.
        """
        if mode_a.priority >= mode_b.priority:
            return mode_a
        else:
            return mode_b

    @staticmethod
    def combine_values(value_a: float, value_b: float, mode: CombineMode) -> float:
        """
        Combine deux valeurs physiques selon le mode spécifié.

        Parameters
        ----------
        value_a : float
            Valeur du premier matériau.
        value_b : float
            Valeur du second matériau.
        mode : CombineMode
            Mode de combinaison à utiliser.

        Returns
        -------
        float
            La valeur combinée résultante.
        """
        if mode == CombineMode.MIN:
            return min(value_a, value_b)
        elif mode == CombineMode.AVERAGE:
            return (value_a + value_b) / 2.0
        elif mode == CombineMode.MULTIPLY:
            return value_a * value_b
        elif mode == CombineMode.MAX:
            return max(value_a, value_b)
        else:
            logger.warning(f"CombineMode inconnu {mode}, retourne la moyenne.")
            return (value_a + value_b) / 2.0

    def combine_with(self, other: "PhysicMaterial") -> "PhysicMaterial":
        """
        Combine ce matériau avec un autre pour produire un matériau effectif.

        Cette méthode calcule les propriétés effectives lors d'un contact entre
        deux surfaces : friction, restitution, damping.

        Parameters
        ----------
        other : PhysicMaterial
            L'autre matériau avec lequel combiner.

        Returns
        -------
        PhysicMaterial
            Le matériau résultant de la combinaison.
        """
        combined_friction_mode = self.resolve_combine_mode(
            self.friction_mode, other.friction_mode
        )
        combined_restitution_mode = self.resolve_combine_mode(
            self.restitution_mode, other.restitution_mode
        )

        combined_friction = self.combine_values(
            self.friction, other.friction, combined_friction_mode
        )
        combined_restitution = self.combine_values(
            self.restitution, other.restitution, combined_restitution_mode
        )

        combined_linear_damping = max(self.linear_damping, other.linear_damping)
        combined_bounce_velocity_threshold = max(
            self.bounce_velocity_threshold,
            other.bounce_velocity_threshold,
        )

        return PhysicMaterial(
            friction=combined_friction,
            restitution=combined_restitution,
            friction_mode=combined_friction_mode,
            restitution_mode=combined_restitution_mode,
            linear_damping=combined_linear_damping,
            bounce_velocity_threshold=combined_bounce_velocity_threshold,
        )
