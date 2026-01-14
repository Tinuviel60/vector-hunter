from typing import List, Optional
from vect_hunt.engine.core import Tag
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform
from vect_hunt.engine.physics.collider import Collider
from vect_hunt.engine.rendering.render_component import RenderComponent


class GameObject:
    """
    Représente un objet du jeu, avec sa transformation spatiale et ses colliders.

    Un GameObject est une entité logique qui peut être :
    - déplacée dans l'espace via son Transform,
    - équipée de colliders pour la détection de collisions,
    - enrichie plus tard avec des composants (physique, rendu, scripts...).

    Attributes
    ----------
    id : int
        Identifiant unique de l'objet (généré automatiquement).
    name : str
        Nom de l'objet pour identification.
    transform : Transform
        Transformation spatiale de l'objet.
    colliders : List[Collider]
        Liste des colliders attachés à l'objet. Peut être vide.
    active : bool
        Indique si l'objet est actif dans le monde.
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

        self.type = self.__class__.__name__

        # Implementation des attributs
        self.name = name
        self.transform = transform if transform is not None else Transform()
        self.colliders: List[Collider] = []
        self.active = True
        self.tags = tags

        # État de collision (pour le rendu debug)
        self.nb_collision = False

        # Composant de rendu (optionnel)
        self.render_component: Optional[RenderComponent] = None

    def set_renderer(self, renderer: RenderComponent) -> None:
        """
        Associe un composant de rendu à ce GameObject.
        """
        self.render_component = renderer

    def add_collider(self, collider: Collider) -> None:
        """
        Attache un collider à l'objet.

        Parameters
        ----------
        collider : Collider
            Le collider à ajouter.
        """
        self.colliders.append(collider)

    def remove_collider(self, collider: Collider) -> None:
        """
        Retire un collider de l'objet.

        Parameters
        ----------
        collider : Collider
            Le collider à retirer.
        """
        if collider in self.colliders:
            self.colliders.remove(collider)

    def move(self, displacement: Vector2D) -> None:
        """
        Déplace le GameObject dans l'espace en modifiant son Transform.

        Parameters
        ----------
        displacement : Vector2D
            Vecteur de déplacement à appliquer.
        """
        self.transform.move(displacement)

    def rotate(self, delta: float) -> None:
        """
        Applique une rotation relative au GameObject.

        Parameters
        ----------
        delta : float
            Angle en radians à ajouter à la rotation actuelle.
        """
        self.transform.rotate(delta)

    def set_position(self, position: Vector2D) -> None:
        """
        Définit explicitement la position du GameObject.

        Parameters
        ----------
        position : Vector2D
            Nouvelle position à définir.
        """
        displacement = position - self.transform.position
        self.move(displacement)

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
        Appelé quand ce GameObject entre en collision physique.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        pass

    # TODO : Créer une liste de gameobject qui ont déclenché un trigger cette frame ?
    # NOTE : voir si garde cela ici
    def on_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject entre dans un trigger.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        pass

    def on_enter_collision(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject commence une collision physique avec un autre.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        self.nb_collision += 1

    def on_exit_collision(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject termine une collision physique avec un autre.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans la collision.
        """
        self.nb_collision -= 1

    def on_enter_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject entre dans un trigger avec un autre.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        self.nb_collision += 1

    def on_exit_trigger(self, other: "GameObject") -> None:
        """
        Appelé quand ce GameObject sort d'un trigger avec un autre.

        Parameters
        ----------
        other : GameObject
            L'autre GameObject impliqué dans le trigger.
        """
        self.nb_collision -= 1

    def update(self, delta_time: float) -> None:
        """
        Méthode de mise à jour appelée chaque frame.

        Par défaut, cette méthode ne fait rien.
        Les sous-classes (comme Player) peuvent la surcharger pour
        implémenter un comportement spécifique.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass
