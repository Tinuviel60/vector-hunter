import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject


class Component(ABC):
    """
    Classe abstraite de base pour tous les composants attachables à un GameObject.

    Un Component représente une capacité ou un comportement spécifique
    (rendu, physique, input, IA, etc.).

    Il est attaché à un unique GameObject et peut réagir aux événements
    du cycle de vie de l'objet (update, collisions, triggers).

    Attributes
    ----------
    component_name : str
        Nom unique du type de composant.
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    """

    component_name: ClassVar[str] = "Component"
    _name_registry: ClassVar[dict[str, type["Component"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Valide les sous-classes de Component lors de leur définition.
        Assure l'unicité et la validité de `component_name`.

        Parameters
        ----------
        **kwargs : Any
            Arguments supplémentaires pour la sous-classe.
        """
        super().__init_subclass__(**kwargs)

        # Ignore la classe de base elle-même
        if cls is Component:
            return

        # Ignore les classes abstraites
        if inspect.isabstract(cls):
            return

        # Validation de component_name
        if "component_name" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define `component_name` explicitly.")
        component_name = cls.__dict__["component_name"]

        # S'assurer que c'est une chaîne non vide
        if not isinstance(component_name, str) or not component_name.strip():
            raise TypeError(
                f"{cls.__name__}.component_name must be a non-empty string."
            )

        # S'assure de l'unicité du nom
        existing = Component._name_registry.get(component_name)
        if existing is not None and existing is not cls:
            raise TypeError(
                f"Duplicate component_name '{component_name}': "
                f"{existing.__name__} and {cls.__name__}."
            )

        Component._name_registry[component_name] = cls

    @property
    def parent(self) -> "GameObject":
        """
        Retourne le GameObject parent.

        Ce composant doit être attaché avant utilisation.

        Returns
        -------
        GameObject
            Le GameObject auquel ce composant est attaché.
        """
        if self.game_object is None:
            raise RuntimeError("Component not attached to any GameObject")
        return self.game_object

    @classmethod
    def get_registered_components(cls) -> dict[str, type["Component"]]:
        """
        Retourne une copie du dictionnaire des composants enregistrés.

        Returns
        -------
        dict[str, type[Component]]
            Dictionnaire mappant les noms de composants à leurs classes.
        """
        return dict(cls._name_registry)

    def __init__(self) -> None:
        """
        Initialise le composant.

        Le GameObject sera assigné lors de l'appel à on_attach().
        """
        self.game_object: "GameObject | None" = None
        self.active: bool = True

    def on_attach(self, game_object: "GameObject") -> None:
        """
        Appelé lorsque le composant est attaché à un GameObject.

        Assigne le GameObject et permet des initialisations supplémentaires
        dans les sous-classes.

        Parameters
        ----------
        game_object : GameObject
            Le GameObject auquel ce composant est attaché.
        """
        self.game_object = game_object

    def on_detach(self) -> None:
        """
        Appelé lors du détachement du composant.

        Libère la référence au GameObject et permet du nettoyage
        supplémentaire dans les sous-classes.
        """
        self.game_object = None

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Mise à jour du composant appelée chaque frame.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass

    def on_collision(self, other: "GameObject") -> None:
        """
        Appelé lors d'une collision persistante.
        """
        pass

    def on_enter_collision(self, other: "GameObject") -> None:
        """
        Appelé au début d'une collision.
        """
        pass

    def on_exit_collision(self, other: "GameObject") -> None:
        """
        Appelé à la fin d'une collision.
        """
        pass

    def on_trigger(self, other: "GameObject") -> None:
        """
        Appelé lors d'un trigger persistante.
        """
        pass

    def on_enter_trigger(self, other: "GameObject") -> None:
        """
        Appelé au début d'un trigger.
        """
        pass

    def on_exit_trigger(self, other: "GameObject") -> None:
        """
        Appelé à la fin d'un trigger.
        """
        pass

    @classmethod
    @abstractmethod
    def from_data(cls, data: dict[str, Any], context: dict[str, Any]) -> "Component":
        """
        Crée une instance du composant à partir de données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration du composant.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        Component
            Instance du composant créé.
        """
        raise NotImplementedError(
            "Cette methode doit etre implementee dans les sous-classes."
        )

    def awake(self) -> None:
        """
        Appelé une fois après que tous les composants du GameObject
        ont été attachés.

        Permet des initialisations dépendant d'autres composants.
        """
        pass

    def start(self) -> None:
        """
        Appelé une fois avant la première mise à jour (update).

        Permet des initialisations finales avant le début du cycle de vie.
        """
        pass
