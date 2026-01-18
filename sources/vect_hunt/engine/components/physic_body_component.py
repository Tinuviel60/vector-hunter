"""
Composant de corps physique pour gérer les déplacements et forces.
"""

from typing import Any

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.physics.physic_material import CombineMode, PhysicMaterial
from vect_hunt.engine.resources.loaders.data_loader import DataLoader

import logging

logger = logging.getLogger(__name__)


class PhysicBodyComponent(Component):
    """
    Composant gérant les aspects physiques d'un GameObject.

    Reçoit des intentions de mouvement (vélocité, forces) et applique
    les déplacements sur le Transform du GameObject.
    Le système de collision se charge des limitations.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    mass : float
        Masse du corps physique.
    speed : float
        Vitesse de déplacement en pixels/seconde.
    velocity : Vector2D
        Vitesse actuelle en pixels/seconde.
    acceleration : Vector2D
        Accélération accumulée en pixels/seconde².
    is_kinematic : bool
        Indique si le corps est cinématique.
    use_gravity : bool
        Indique si le corps est affecté par la gravité.
    is_controlled : bool
        Indique si le corps est contrôlé par un composant externe.
    material : PhysicMaterial
        Matériau physique associé.
    """

    component_name = "physic_body"

    def __init__(
        self,
        mass: float = 1.0,
        speed: float = 300.0,
        is_kinematic: bool = False,
        use_gravity: bool = True,
        is_controlled: bool = False,
        material: PhysicMaterial | None = None,
    ):
        """
        Initialise le composant de corps physique.

        Parameters
        ----------
        mass : float, optional
            Masse du corps physique (par défaut 1.0).
        speed : float, optional
            Vitesse de déplacement en pixels/seconde (par défaut 300.0).
        is_kinematic : bool, optional
            Indique si le corps est cinématique (par défaut False).
        material : PhysicMaterial | None, optional
            Matériau physique à utiliser (par défaut PhysicMaterial standard).
        """
        super().__init__()
        if mass <= 0:
            logger.warning(
                "La masse doit être positive. \
                           Valeur par défaut 1.0 utilisée."
            )
            mass = 1.0

        self.mass = mass
        self.speed = speed  # TODO : A déplacer
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)

        self.is_kinematic = is_kinematic
        self.use_gravity = use_gravity
        self.is_controlled = is_controlled

        self.material = material if material is not None else PhysicMaterial()

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "PhysicBodyComponent":
        """
        Crée une instance de PhysicBodyComponent à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        InputComponent
            Instance du composant créé.
        """
        material = cls._create_physic_material(data.get("material"))
        return cls(
            mass=data.get("mass", 1.0),
            speed=data.get("speed", 300.0),
            is_kinematic=data.get("is_kinematic", False),
            use_gravity=data.get("use_gravity", True),
            is_controlled=data.get("is_controlled", False),
            material=material,
        )

    @staticmethod
    def _create_physic_material(material_path: Any) -> PhysicMaterial:
        """
        Crée un PhysicMaterial à partir d'un chemin de fichier JSON.

        Parameters
        ----------
        material_path : str | None
            Chemin vers le fichier JSON du matériau physique.

        Returns
        -------
        PhysicMaterial
            Matériau physique chargé ou par défaut.
        """
        if not material_path:
            return PhysicMaterial()

        if not isinstance(material_path, str):
            logger.warning(
                "Le chemin du matériau physique doit être une chaîne de caractères. \
                           Matériau par défaut utilisé."
            )
            return PhysicMaterial()

        material_data = DataLoader.load_json(material_path)
        return PhysicBodyComponent._material_from_data(material_data)

    @staticmethod
    def _material_from_data(material_data: dict[str, Any]) -> PhysicMaterial:
        """
        Crée un PhysicMaterial à partir de données sérialisées.

        Parameters
        ----------
        material_data : dict[str, Any]
            Données de configuration du matériau physique.

        Returns
        -------
        PhysicMaterial
            Matériau physique créé.
        """
        friction = material_data.get("friction", 0.5)
        restitution = material_data.get("restitution", 0.5)
        linear_damping = material_data.get("linear_damping", 0.0)
        bounciness_threshold = material_data.get("bounciness_threshold", 0.0)
        friction_mode = PhysicBodyComponent._parse_combine_mode(
            material_data.get("friction_mode"), CombineMode.MAX
        )
        restitution_mode = PhysicBodyComponent._parse_combine_mode(
            material_data.get("restitution_mode"), CombineMode.MIN
        )

        return PhysicMaterial(
            friction=friction,
            restitution=restitution,
            friction_mode=friction_mode,
            restitution_mode=restitution_mode,
            linear_damping=linear_damping,
            bounciness_threshold=bounciness_threshold,
        )

    @staticmethod
    def _parse_combine_mode(value: str | None, default: CombineMode) -> CombineMode:
        """
        Analyse une chaîne de caractères en CombineMode.

        Parameters
        ----------
        value : str | None
            Chaîne représentant le mode de combinaison.
        default : CombineMode
            Valeur par défaut si l'analyse échoue.
        Returns
        -------
        CombineMode
            Mode de combinaison analysé.
        """
        if value is None:
            return default
        try:
            return CombineMode[value.upper()]
        except KeyError:
            return default

    def update(self, delta_time: float) -> None:
        """
        Met à jour la position du GameObject en fonction de la vélocité.

        Applique :
            - intégration de l'accélération (forces ponctuelles)
            - amortissement linéaire (linear damping)
            - déplacement via le Transform

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        assert (
            self.game_object is not None
        ), "PhysicBodyComponent doit être attaché à un GameObject"

        # Un corps cinématique peut être déplacé par une logique dédiée,
        # mais ne subit pas intégration des forces ici.
        if self.is_kinematic:
            self.acceleration = Vector2D(0, 0)
            return

        # Appliquer l'accélération à la vélocité
        self.velocity += self.acceleration * delta_time

        # Appliquer l'amortissement linéaire (perte de vitesse au fil du temps)
        damping = self.material.linear_damping
        if damping > 0.0:
            damping_factor = max(0.0, 1.0 - damping * delta_time)
            self.velocity *= damping_factor

        # Appliquer la vélocité au déplacement
        if self.velocity.magnitude() > 0:
            displacement = self.velocity * delta_time
            self.game_object.transform.move(displacement)

        # Réinitialiser l'accélération (forces ponctuelles)
        self.acceleration = Vector2D(0, 0)

    def set_velocity(self, velocity: Vector2D) -> None:
        """
        Définit la vélocité du corps physique.

        Parameters
        ----------
        velocity : Vector2D
            Vecteur de vélocité en pixels/seconde.
        """
        if not self.is_controlled:
            logger.debug(
                "Le corps physique n'est pas contrôlé. \
                         La vélocité ne peut pas être définie."
            )
            return
        if self.is_kinematic:
            logger.debug(
                "Le corps physique est cinématique. \
                         La vélocité ne peut pas être définie."
            )
            return

        self.velocity = velocity

    def add_force(self, force: Vector2D) -> None:
        """
        Ajoute une force au corps physique.

        La force est convertie en accélération en fonction de la masse.

        Parameters
        ----------
        force : Vector2D
            Force à appliquer en newtons (pixels*kg/s²).
        """
        self.acceleration += force / self.mass

    def add_acceleration(self, acceleration: Vector2D) -> None:
        """
        Ajoute une accélération au corps physique.

        Parameters
        ----------
        acceleration : Vector2D
            Accélération à ajouter en pixels/seconde².
        """
        self.acceleration += acceleration

    def stop(self) -> None:
        """
        Arrête complètement le mouvement du corps physique.
        """
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
