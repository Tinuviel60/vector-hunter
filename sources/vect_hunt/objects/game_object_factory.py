from vect_hunt.core import (
    BoxCollider,
    CircleCollider,
    Tag,
    Transform,
    Vector2D,
)
from vect_hunt.objects import GameObject
from vect_hunt.rendering import BasicShape
from vect_hunt.resources import DataLoader

from typing import Optional

"""
Factory pour créer des GameObjects depuis des templates JSON.
"""


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
    ) -> GameObject:
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
            Rotation initiale en radians (override la rotation du template)

        Returns
        -------
        GameObject
            GameObject complet avec tous ses composants

        Examples
        --------
        >>> player = GameObjectFactory.from_template("player.json")
        >>> target = GameObjectFactory.from_template(
        ...     "targets/basic.json",
        ...     position=Vector2D(400, 300)
        ... )
        """
        # Charger le template
        template = DataLoader.load_json(f"templates/{template_path}")

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

        # Créer le GameObject
        game_object = GameObject(template["name"], transform, tags=tags)

        # Ajouter le collider
        if "collider" in template:
            collider = GameObjectFactory._create_collider(
                game_object, template["collider"]
            )
            game_object.add_collider(collider)

        # Ajouter le renderer
        if "rendering" in template:
            renderer = GameObjectFactory._create_renderer(
                transform, template["rendering"]
            )
            game_object.set_renderer(renderer)

        # TODO: Ajouter physics, controls, behavior selon les besoins futurs

        return game_object

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
        rotation = transform_data.get("rotation", 0.0)

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
    def _create_renderer(transform: Transform, rendering_data: dict):
        """
        Crée un composant de rendu depuis les données du template.

        Parameters
        ----------
        transform : Transform
            Transform du GameObject
        rendering_data : dict
            Données de rendu du template

        Returns
        -------
        RenderComponent
            Composant de rendu (actuellement BasicShape)
        """
        render_type = rendering_data["type"]

        if render_type == "basic_shape":
            shape = rendering_data["shape"]
            color = rendering_data["color"]

            # Dimensions selon la forme
            if shape == "circle":
                # Pour un cercle, size doit être un int (le rayon)
                size = rendering_data["radius"]
            elif shape == "rectangle" or shape == "box":
                # Pour un rectangle, size doit être un tuple (width, height)
                size = (
                    rendering_data.get("width", 20),
                    rendering_data.get("height", 20),
                )
            else:
                size = 20  # Défaut pour cercle

            # Couleur de bordure et épaisseur optionnelles
            border_color = rendering_data.get("border_color", "#000000")
            border_thickness = rendering_data.get("border_thickness", 2)

            return BasicShape(
                transform, shape, size, color, border_color, border_thickness
            )

        # TODO: Gérer sprite, animated_sprite, etc.
        else:
            raise ValueError(f"Type de rendu inconnu : {render_type}")
