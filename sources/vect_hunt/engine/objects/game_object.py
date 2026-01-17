from typing import List, Optional, TypeVar, TYPE_CHECKING
from vect_hunt.engine.core import Tag
from vect_hunt.engine.core.transform import Transform

if TYPE_CHECKING:
    from vect_hunt.engine.components.component import Component

# Type générique pour les composants
T = TypeVar("T", bound="Component")


class GameObject:
    """
    Représente un objet du jeu, avec sa transformation spatiale et ses composants.

    Un GameObject est une entité logique qui peut être :
    - déplacée dans l'espace via son Transform,
    - équipée de composants (rendu, physique, collision, scripts...),
    - enrichie avec des comportements via le système de composants.

    Attributes
    ----------
    id : int
        Identifiant unique de l'objet (généré automatiquement).
    name : str
        Nom de l'objet pour identification.
    transform : Transform
        Transformation spatiale de l'objet.
    active : bool
        Indique si l'objet est actif dans le monde.
    tags : Tag
        Tags associés à l'objet.
    components : List[Component]
        Liste des composants attachés à cet objet.
    """

    _next_id: int = 1  # Compteur de classe pour générer des IDs uniques

    def __init__(
        self, name: str, transform: Optional[Transform] = None, tags: Tag = Tag.NONE
    ):
        """
        Initialise un GameObject.

        Parameters
        ----------
        name : str
            Nom de l'objet.
        transform : Transform, optional
            Transformation initiale de l'objet. Par défaut, un Transform
            avec position (0,0) et rotation 0.
        tags : Tag
            Tags initiaux pour cet objet. Par défaut Tag.NONE.
        """
        self.id = GameObject._next_id
        GameObject._next_id += 1

        # Implementation des attributs
        self.name = name
        self.transform = transform if transform is not None else Transform()
        self.active = True
        self.tags = tags

        # Système de composants
        self.components: List["Component"] = []

    def add_component(self, component: "Component") -> "Component":
        """
        Attache un composant au GameObject.

        Le composant est ajouté à la liste des composants et sa méthode
        on_attach() est appelée pour assigner le GameObject et permettre
        une initialisation supplémentaire si nécessaire.

        Parameters
        ----------
        component : Component
            Le composant à attacher à ce GameObject.

        Returns
        -------
        Component
            Le composant qui vient d'être attaché, permettant un
            chaînage de méthodes si nécessaire.
        """
        self.components.append(component)
        component.on_attach(self)
        return component

    def remove_component(self, component: "Component") -> None:
        """
        Détache un composant du GameObject.

        Le composant est retiré de la liste des composants et sa méthode
        on_detach() est appelée pour permettre un nettoyage si nécessaire.

        Parameters
        ----------
        component : Component
            Le composant à détacher de ce GameObject.
        """
        if component in self.components:
            component.on_detach()
            self.components.remove(component)

    def get_component(self, component_type: type[T]) -> Optional[T]:
        """
        Récupère le premier composant d'un type donné attaché à ce GameObject.

        Cette méthode est utile lorsqu'on sait qu'un seul composant d'un
        type donné est attaché (par exemple, Transform, Rigidbody).

        Parameters
        ----------
        component_type : type[T]
            Le type de composant recherché.

        Returns
        -------
        T or None
            Le premier composant du type spécifié, ou None si aucun
            composant de ce type n'est trouvé.
        """
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp
        return None

    def get_components(self, component_type: type[T]) -> List[T]:
        """
        Récupère tous les composants d'un type donné attachés à ce GameObject.

        Cette méthode est utile lorsque plusieurs composants du même type
        peuvent être attachés (par exemple, plusieurs Collider).

        Parameters
        ----------
        component_type : type[T]
            Le type de composant recherché.

        Returns
        -------
        List[T]
            Liste de tous les composants du type spécifié. La liste est
            vide si aucun composant de ce type n'est trouvé.
        """
        return [comp for comp in self.components if isinstance(comp, component_type)]

    def add_tag(self, tag: Tag) -> None:
        """
        Ajoute un tag à ce GameObject.

        Parameters
        ----------
        tag : Tag
            Le tag à ajouter.
        """
        self.tags |= tag  # Bitwise OR pour ajouter le tag

    def remove_tag(self, tag: Tag) -> None:
        """
        Retire un tag de ce GameObject.
        """
        self.tags &= ~tag  # Bitwise AND avec NOT pour retirer le tag

    def has_tag(self, tag: Tag) -> bool:
        """
        Vérifie si ce GameObject possède un tag donné.
        """
        return bool(self.tags & tag)

    def list_tags(self) -> list[Tag]:
        """
        Retourne tous les tags actifs de ce GameObject sous forme de liste.
        """
        return [t for t in Tag if t != Tag.NONE and self.has_tag(t)]

    # TODO : Créer une liste de gameobject qui ont déclenché une collision cette frame ?
    # NOTE : voir si garde cela ici
    def on_collision(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject est en collision physique persistante.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        for component in self.components:
            if component.active:
                component.on_collision(other)

    # TODO : Créer une liste de gameobject qui ont déclenché un trigger cette frame ?
    # NOTE : voir si garde cela ici
    def on_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject est dans un trigger persistant.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        for component in self.components:
            if component.active:
                component.on_trigger(other)

    def on_enter_collision(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject commence une collision physique avec un autre.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        for component in self.components:
            if component.active:
                component.on_enter_collision(other)

    def on_exit_collision(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject termine une collision physique avec un autre.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        for component in self.components:
            if component.active:
                component.on_exit_collision(other)

    def on_enter_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject entre dans un trigger avec un autre.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        for component in self.components:
            if component.active:
                component.on_enter_trigger(other)

    def on_exit_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject sort d'un trigger avec un autre.

        Propage l'événement à tous les composants actifs.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        for component in self.components:
            if component.active:
                component.on_exit_trigger(other)

    def update(self, delta_time: float) -> None:
        """
        Met à jour tous les composants actifs du GameObject.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        for component in self.components:
            if component.active:
                component.update(delta_time)
