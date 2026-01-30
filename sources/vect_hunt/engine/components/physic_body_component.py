"""
Composant de corps physique pour gérer les déplacements et forces.
"""

from typing import TYPE_CHECKING, Any, cast, List

from vect_hunt.engine.components.component import Component
from vect_hunt.engine.core.math.tolerance import Tolerence
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.physics.physic_material import CombineMode, PhysicMaterial

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.components.collider.collider_component import ColliderComponent

import logging

logger = logging.getLogger(__name__)


class PhysicBodyComponent(Component):
    """
    Composant gérant les aspects physiques d'un GameObject.

    Reçoit des intentions de mouvement (vélocité, forces) et applique
    les déplacements sur le Transform du GameObject.
    Le système de collision se charge des limitations.

    Notes
    -----
    - Le centre de masse local (ici basé sur la géométrie/aire) est calculé
      une fois que le composant est attaché au GameObject (via `on_attach`).
    - L'inertie totale prend en compte :
        1) la redistribution de la masse au prorata des aires
        2) le décalage des colliders par rapport au centre de masse (axes parallèles)

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
    angular_velocity : float
        Vitesse angulaire actuelle en radians/seconde.
    angular_acceleration : float
        Accélération angulaire en radians/seconde².
    inertia : float
        Moment d'inertie du corps.
    mass_center : Vector2D
        Centre de masse (géométrique pondéré par aire) en coordonnées locales.
    is_kinematic : bool
        Indique si le corps est cinématique.
    use_gravity : bool
        Indique si le corps est affecté par la gravité.
    is_controlled : bool
        Indique si le corps est contrôlé par un composant externe.
    material : PhysicMaterial
        Matériau physique associé.
    """
    # TODO : A Mettre dans une config globale ou par scène
    SLEEP_LINEAR_VEL = 0.5      # px/s
    SLEEP_ANGULAR_VEL = 0.05   # rad/s
    SLEEP_TIME = 0.5           # secondes

    component_name = "physic_body"

    def __init__(
        self,
        mass: float = 1.0,
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
        is_kinematic : bool, optional
            Indique si le corps est cinématique (par défaut False).
        material : PhysicMaterial | None, optional
            Matériau physique à utiliser (par défaut PhysicMaterial standard).
        angular_damping : float, optional
            Amortissement angulaire (par défaut 0.0).
        """
        super().__init__()
        if mass <= 0:
            logger.warning(
                "La masse doit être positive. \
                           Valeur par défaut 1.0 utilisée."
            )
            mass = 1.0

        self.mass = mass
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)

        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0

        # Propriétés de masse : initialisées ici, calculées réellement à l'attache
        self.inertia = 1.0
        self.mass_center = Vector2D(0, 0)

        self.is_kinematic = is_kinematic
        self.use_gravity = use_gravity
        self.is_controlled = is_controlled

        self.is_sleeping: bool = False
        self.sleep_timer: float = 0.0

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
        materials = context.get("materials", {})
        material = cls._create_physic_material(data.get("material"), materials)
        return cls(
            mass=data.get("mass", 1.0),
            is_kinematic=data.get("is_kinematic", False),
            use_gravity=data.get("use_gravity", True),
            is_controlled=data.get("is_controlled", False),
            material=material,
        )

    def on_attach(self, game_object: "GameObject") -> None:
        """
        Appelé lorsque le composant est attaché à un GameObject.

        Calcule le centre de masse et le moment d'inertie.

        Parameters
        ----------
        game_object : GameObject
            GameObject auquel le composant est attaché.
        """
        super().on_attach(game_object)

    def awake(self) -> None:
        """
        Appelé lorsque le composant est initialisé dans la scène.
        """
        super().awake()
        self.mass_center = self.define_gravity_center()
        self.inertia = self.calculate_inertia()

    # TODO : Bouger dans material ?
    @staticmethod
    def _create_physic_material(
        material_path: Any, materials: dict[str, dict[str, Any]]
    ) -> PhysicMaterial:
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

        if not materials:
            raise ValueError("Registre de materials manquant pour charger le material.")

        material_data = materials.get(material_path)
        if material_data is None:
            raise FileNotFoundError(
                f"Material introuvable dans le registre: {material_path}"
            )
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
        static_friction = material_data.get("static_friction", 0.5)
        dynamic_friction = material_data.get("dynamic_friction", 0.65)
        restitution = material_data.get("restitution", 0.5)
        linear_damping = material_data.get("linear_damping", 0.0)
        bounce_velocity_threshold = material_data.get("bounce_velocity_threshold", 0.0)
        angular_damping = material_data.get("angular_damping", 0.0)
        friction_mode = PhysicBodyComponent._parse_combine_mode(
            material_data.get("friction_mode"), CombineMode.MAX
        )
        restitution_mode = PhysicBodyComponent._parse_combine_mode(
            material_data.get("restitution_mode"), CombineMode.MIN
        )

        return PhysicMaterial(
            static_friction=static_friction,
            dynamic_friction=dynamic_friction,
            restitution=restitution,
            friction_mode=friction_mode,
            angular_damping=angular_damping,
            restitution_mode=restitution_mode,
            linear_damping=linear_damping,
            bounce_velocity_threshold=bounce_velocity_threshold,
        )

    def invert_mass(self) -> float:
        """
        Calcule l'inverse de la masse.

        Returns
        -------
        float
            Inverse de la masse (0 si masse infinie).
        """
        eps = Tolerence.GENERAL
        if self.mass <= eps or self.is_kinematic:
            return 0.0
        return 1.0 / self.mass

    def invert_inertia(self) -> float:
        """
        Calcule l'inverse de l'inertie.

        Returns
        -------
        float
            Inverse de l'inertie (0 si inertie infinie).
        """
        eps = Tolerence.GENERAL
        if self.inertia <= eps or self.is_kinematic:
            return 0.0
        return 1.0 / self.inertia

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
        Met à jour le corps physique.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass

    def integrate_velocity(self, delta_time: float) -> None:
        """
        Intégrer les vélocités à partir des accélérations.

        cette méthode met à jour :
        - la vélocité linéaire à partir de l'accélération linéaire
        - la vélocité angulaire à partir de l'accélération angulaire
        - applique l'amortissement linéaire et angulaire
        - réinitialise les accélérations à la fin de l'étape

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        if self.is_kinematic:
            self.acceleration = Vector2D(0, 0)
            self.angular_acceleration = 0.0
            return

        # Linear integration
        self.velocity += self.acceleration * delta_time

        linear_damping = self.material.linear_damping
        if linear_damping > Tolerence.GENERAL:
            damping_factor = max(0.0, 1.0 - linear_damping * delta_time)
            self.velocity *= damping_factor

        # Angular integration
        self.angular_velocity += self.angular_acceleration * delta_time

        angular_damping = self.material.angular_damping
        if angular_damping > Tolerence.GENERAL:
            damping_factor = max(0.0, 1.0 - angular_damping * delta_time)
            self.angular_velocity *= damping_factor

        # Reset per-frame accelerations
        self.acceleration = Vector2D(0, 0)
        self.angular_acceleration = 0.0

    def sleep_check(self, delta_time: float) -> None:
        """
        Vérifie si le corps physique peut être mis en veille (sleep).

        Si il est en dessous des seuils de vélocité linéaire et angulaire
        pendant une certaine durée, il est mis en veille.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        if self.is_kinematic:
            self.is_sleeping = False
            self.sleep_timer = 0.0
            return

        # print("is_sleeping:", self.is_sleeping,
        #       "object:", self.parent.name)

        linear_speed_sq = self.velocity.magnitude_squared()
        angular_speed = abs(self.angular_velocity)

        if (
            linear_speed_sq < self.SLEEP_LINEAR_VEL * self.SLEEP_LINEAR_VEL
            and angular_speed < self.SLEEP_ANGULAR_VEL
        ):
            self.sleep_timer += delta_time
            if self.sleep_timer >= self.SLEEP_TIME:
                self.is_sleeping = True
                self.velocity = Vector2D(0, 0)
                self.angular_velocity = 0.0
        else:
            self.is_sleeping = False
            self.sleep_timer = 0.0

    def integrate_transform(self, delta_time: float) -> None:
        """
        Intégrer les transformations à partir des vélocités.

        Cette méthode met à jour :
        - la position à partir de la vélocité linéaire
        - la rotation à partir de la vélocité angulaire

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        if self.is_kinematic:
            return

        if self.velocity.magnitude_squared() > Tolerence.GENERAL * Tolerence.GENERAL:
            old_pos = self.parent.transform.position
            self.parent.transform.move(self.velocity * delta_time)
            new_pos = self.parent.transform.position
            
            # Log position changes for collider 3
            import sys
            for comp in self.parent.get_all_components():
                if hasattr(comp, 'id') and comp.__class__.__name__ == 'ColliderComponent':
                    if comp.id in [3, 8]:
                        displacement = new_pos - old_pos
                        if displacement.magnitude_squared() > Tolerence.GENERAL * Tolerence.GENERAL:
                            print(f"[POS_UPDATE] col_id={comp.id} pos=({new_pos.x:.1f},{new_pos.y:.1f}) displacement=({displacement.x:.3f},{displacement.y:.3f})", file=sys.stderr)
                    break

        if abs(self.angular_velocity) > Tolerence.GENERAL:
            old_angle = self.parent.transform.rotation.angle
            self.parent.transform.rotate(self.angular_velocity * delta_time)
            new_angle = self.parent.transform.rotation.angle
            
            # Log rotation for collider 3
            import sys
            for comp in self.parent.get_all_components():
                if hasattr(comp, 'id') and comp.__class__.__name__ == 'ColliderComponent':
                    if comp.id in [3, 8]:
                        angle_delta = new_angle - old_angle
                        print(f"[ROT_UPDATE] col_id={comp.id} angle={new_angle:.4f} delta_angle={angle_delta:.6f} ang_vel={self.angular_velocity:.6f} dt={delta_time:.4f}", file=sys.stderr)
                    break

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

    def apply_impulse_at_point(self, impulse: Vector2D, scene_point: Vector2D) -> None:
        """
        Applique une impulsion instantanée à un point du corps physique.

        Cette méthode met à jour :
        - la vélocité linéaire (translation)
        - la vélocité angulaire (rotation) via le couple induit au point d'application

        Parameters
        ----------
        impulse : Vector2D
            Impulsion à appliquer en newton*seconde (pixels*kg/s).
        scene_point : Vector2D
            Point d'application de l'impulsion en coordonnées de la scène.
        """
        if self.is_kinematic:
            return
        
        if self.is_sleeping:
            self.is_sleeping = False
            self.sleep_timer = 0.0

        eps = Tolerence.GENERAL
        inv_mass = self.invert_mass()
        inv_inertia = self.invert_inertia()
        if inv_mass <= eps and inv_inertia <= eps:
            return

        # --- Translation ---
        if inv_mass > eps:
            self.velocity += impulse * inv_mass

        # --- Rotation ---
        if inv_inertia > eps:
            parent_tr = self.parent.transform
            com_world = parent_tr.to_scene_point(self.mass_center)
            lever_arm = scene_point - com_world

            # Produit vectoriel 2D -> scalaire (r x J)
            torque_impulse = (lever_arm.x * impulse.y) - (lever_arm.y * impulse.x)
            self.angular_velocity += torque_impulse * inv_inertia

    def add_torque(self, torque: float) -> None:
        """
        Ajoute un couple (torque) au corps physique.

        Le couple est converti en accélération angulaire en fonction de l'inertie.

        Parameters
        ----------
        torque : float
            Couple à appliquer en newton*mètres (kg*m²/s²).
        """
        if self.inertia <= 0.0:
            logger.warning("Inertia <= 0, torque ignoré pour éviter division par zéro.")
            return

        angular_acceleration = torque / self.inertia
        self.angular_acceleration += angular_acceleration

    def define_gravity_center(self) -> Vector2D:
        """
        Définit le centre de gravité local du corps physique, à partir des différents
        colliders attachés au GameObject.

        On considère que chaque collider à une masse proportionnelle à son aire.

        Returns
        -------
        Vector2D
            Centre de gravité en coordonnées locales du GameObject.
        """

        total_area = 0.0
        weighted_position_sum = Vector2D(0, 0)
        for collider in cast(List["ColliderComponent"], self.parent.get_components("collider")):
            if collider.solid is False:
                continue

            area = collider.shape.area()
            local_position = collider.transform.position

            weighted_position_sum += local_position * area
            total_area += area

        if total_area == 0.0:
            return Vector2D(0, 0)

        return weighted_position_sum / total_area

    def calculate_inertia(self) -> float:
        """
        Calcule le moment d'inertie du corps physique, à partir des différents
        colliders attachés au GameObject.

        Détails :
        - masse répartie au prorata des aires
        - inertie locale : I_local = m_i * I_unit(shape)
        - axes parallèles : I = I_local + m_i * d^2

        Returns
        -------
        float
            Moment d'inertie total du corps physique.
        """
        colliders = cast(List["ColliderComponent"], self.parent.get_components("collider"))
        if not colliders:
            logger.warning(
                "Aucun collider attaché au corps physique. "
                "Inertie par défaut 1.0 utilisée."
            )
            return 1.0

        # Somme des aires pour répartir la masse
        areas: list[float] = []
        for collider in colliders:
            if collider.solid is False:
                continue

            area = float(collider.shape.area())
            areas.append(area)

        total_area = sum(areas)
        if total_area == 0.0:
            logger.warning(
                "Aire totale des colliders est nulle. "
                "Inertie par défaut 1.0 utilisée."
            )
            return 1.0

        total_inertia = 0.0
        for collider, area in zip(colliders, areas):
            # Masse du collider au prorata de l'aire
            mass_collider = self.mass * (area / total_area)

            # Inertie centrée du collider
            inertia = mass_collider * collider.shape.inertia

            # Terme des axes parallèles : décalage du collider au centre de masse
            local_position = collider.transform.position
            offset = local_position - self.mass_center

            inertia += mass_collider * offset.magnitude_squared()
            total_inertia += inertia

        # Sécurité : éviter 0 (division par zéro lors d'un torque)
        return max(Tolerence.GENERAL, total_inertia)

    def stop(self) -> None:
        """
        Arrête complètement le mouvement du corps physique.
        """
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)

        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
