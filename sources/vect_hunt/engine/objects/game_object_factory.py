"""
Factory pour créer des GameObjects depuis des templates JSON.
"""

import math
from typing import Optional, TYPE_CHECKING

from vect_hunt.engine.components import (
    ColliderComponent,
    IaComponent,
    PhysicBodyComponent,
)
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.core import Tag
from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.core.transform import Transform
from vect_hunt.engine.physics.collider import BoxCollider, CircleCollider
from vect_hunt.engine.rendering.basic_shape import BasicShape
from vect_hunt.engine.resources import DataLoader

from .game_object import GameObject

if TYPE_CHECKING:
    from vect_hunt.engine.input import InputSystem


class GameObjectFactory:
    """
    Factory responsable de la création de GameObjects depuis des templates.

    Charge les définitions depuis assets/data/templates/ et instancie
    des GameObjects configurés avec tous leurs composants.
    """

    @staticmethod
    def from_template(
        template_path: str,
        position: Optional[Vector2D] = None,
        rotation: Optional[float] = None,
        input_system: Optional["InputSystem"] = None,
    ) -> "GameObject":
        """
        Crée un GameObject depuis un template JSON.

        Parameters
        ----------
        template_path : str
            Chemin relatif du template depuis assets/data/templates/
            Exemple : "player.json", "targets/basic.json"
        position : Vector2D, optional
            Position initiale (override la position du template)
        rotation : float, optional
            Rotation initiale en degrés (override la rotation du template)
        input_system : InputSystem, optional
            Système d'inputs nécessaire pour les objets de type "player"

        Returns
        -------
        GameObject
            GameObject configuré selon le template

        Examples
        --------
        >>> player = GameObjectFactory.from_template(
        ...     "player.json",
        ...     input_system=game.input_system
        ... )
        >>> enemy = GameObjectFactory.from_template("targets/basic.json")
        """
        # Charger le template
        template = DataLoader.load_json(f"templates/{template_path}")

        # Créer le GameObject avec transform et tags
        game_object = GameObjectFactory._create_base_object(
            template, position, math.radians(rotation) if rotation is not None else None
        )

        # Ajouter les composants selon le template
        GameObjectFactory._add_components(game_object, template, input_system)

        return game_object

    @staticmethod
    def _create_base_object(
        template: dict,
        position: Optional[Vector2D],
        rotation: Optional[float],
    ) -> GameObject:
        """
        Crée le GameObject de base avec transform et tags.

        Parameters
        ----------
        template : dict
            Données du template
        position : Vector2D, optional
            Position initiale (override)
        rotation : float, optional
            Rotation initiale (override)

        Returns
        -------
        GameObject
            GameObject avec transform et tags configurés
        """
        # Extraire les données de transform
        transform_data = template["transform"]
        pos = (
            position
            if position is not None
            else Vector2D(transform_data["position"][0], transform_data["position"][1])
        )
        rot = rotation if rotation is not None else transform_data["rotation"]

        transform = Transform(position=pos, rotation=rot)

        # Créer les tags
        tags = GameObjectFactory._parse_tags(template.get("tags", []))

        return GameObject(template["name"], transform, tags=tags)

    @staticmethod
    def _add_components(
        game_object: GameObject,
        template: dict,
        input_system: Optional["InputSystem"],
    ) -> None:
        """
        Ajoute tous les composants au GameObject selon le template.

        Parameters
        ----------
        game_object : GameObject
            GameObject cible
        template : dict
            Données du template
        input_system : InputSystem, optional
            Système d'inputs pour InputComponent
        """
        object_type = template.get("type", "gameobject")

        # Ajouter PhysicBodyComponent si présent dans physics
        if "physics" in template:
            speed = template["physics"].get("speed", 300.0)
            is_kinematic = template["physics"].get("is_kinematic", False)
            physic_body = PhysicBodyComponent(speed=speed, is_kinematic=is_kinematic)
            game_object.add_component(physic_body)

        # Ajouter InputComponent pour le joueur
        if object_type == "player":
            if input_system is None:
                raise ValueError(
                    "InputSystem requis pour créer un objet de type 'player'"
                )
            from vect_hunt.engine.components import InputComponent

            input_comp = InputComponent(input_system)
            game_object.add_component(input_comp)

        # Ajouter IaComponent pour les ennemis
        elif object_type == "enemy":
            ia_comp = IaComponent()
            game_object.add_component(ia_comp)

        # Ajouter ColliderComponent
        if "collider" in template:
            GameObjectFactory._add_collider(game_object, template["collider"])

        # Ajouter RenderComponent
        if "rendering" in template:
            renderer = GameObjectFactory._create_renderer(template["rendering"])
            game_object.add_component(renderer)

    @staticmethod
    def _add_collider(game_object: GameObject, collider_data: dict) -> None:
        """
        Ajoute un ColliderComponent avec un collider au GameObject.

        Parameters
        ----------
        game_object : GameObject
            GameObject cible
        collider_data : dict
            Données du collider du template
        """
        collider = GameObjectFactory._create_collider(game_object, collider_data)

        # Créer ou récupérer le ColliderComponent
        collider_comp = game_object.get_component(ColliderComponent)
        if collider_comp is None:
            collider_comp = ColliderComponent()
            game_object.add_component(collider_comp)

        collider_comp.add_collider(collider)

    @staticmethod
    def _parse_tags(tags_list: list[str]) -> Tag:
        """
        Convertit une liste de tags string en Tag (enum flags).

        Parameters
        ----------
        tags_list : list[str]
            Liste de noms de tags (ex: ["PLAYER", "ENEMY"])

        Returns
        -------
        Tag
            Combinaison de flags Tag
        """
        result = Tag.NONE
        for tag_name in tags_list:
            if hasattr(Tag, tag_name):
                result |= getattr(Tag, tag_name)
        return result

    @staticmethod
    def _create_collider(game_object: GameObject, collider_data: dict):
        """
        Crée un collider depuis les données du template.

        Parameters
        ----------
        game_object : GameObject
            GameObject parent du collider
        collider_data : dict
            Données du collider du template

        Returns
        -------
        Collider
            CircleCollider ou BoxCollider selon le type
        """
        collider_type = collider_data["type"]
        solid = collider_data.get("solid", True)

        # Lire le transform du collider (en coordonnées locales)
        # Par défaut position=[0, 0] et rotation=0.0 (centré sur le GameObject)
        transform_data = collider_data.get(
            "transform", {"position": [0, 0], "rotation": 0.0}
        )
        position_data = transform_data.get("position", [0, 0])
        rotation = math.radians(transform_data.get("rotation", 0.0))

        center = Vector2D(position_data[0], position_data[1])

        if collider_type == "circle":
            radius = collider_data.get("radius", 10.0)
            return CircleCollider(
                game_object, center=center, radius=radius, solid=solid
            )

        elif collider_type == "box":
            width = collider_data.get("width", 10.0)
            height = collider_data.get("height", 10.0)
            # Pour BoxCollider, orientation = rotation locale du collider
            return BoxCollider(
                game_object,
                width=width,
                height=height,
                center=center,
                orientation=rotation,
                solid=solid,
            )

        else:
            raise ValueError(f"Type de collider inconnu : {collider_type}")

    @staticmethod
    def _create_renderer(rendering_data: dict) -> "RenderComponent":
        """
        Crée un composant de rendu depuis les données du template.

        Parameters
        ----------
        rendering_data : dict
            Données de rendu du template

        Returns
        -------
        RenderComponent
            Composant de rendu (actuellement BasicShape)

        Raises
        ------
        ValueError
            Si le type de rendu est inconnu
        """
        render_type = rendering_data["type"]

        if render_type == "basic_shape":
            shape = rendering_data["shape"]
            color = rendering_data["color"]

            # Dimensions selon la forme
            if shape == "circle":
                size = rendering_data["radius"]
            elif shape in ("rectangle", "box"):
                size = (
                    rendering_data.get("width", 20),
                    rendering_data.get("height", 20),
                )
            else:
                raise ValueError(f"Forme inconnue : {shape}")

            # Couleur de bordure et épaisseur optionnelles
            outline_color = rendering_data.get("outline_color")
            outline_width = rendering_data.get("outline_width", 1)

            return BasicShape(shape, size, color, outline_color, outline_width)

        # TODO: Gérer sprite, animated_sprite, etc.
        else:
            raise ValueError(f"Type de rendu inconnu : {render_type}")
