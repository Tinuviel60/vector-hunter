import logging
import math
from typing import Any, Optional, TYPE_CHECKING

from vect_hunt.engine.core import Tag
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.transform.transform import Transform

from vect_hunt.engine.components.component import Component
from .game_object import GameObject

if TYPE_CHECKING:
    from vect_hunt.engine.input import InputSystem

logger = logging.getLogger(__name__)


class GameObjectFactory:
    """
    Factory responsable de la creation de GameObjects depuis des templates JSON.

    Format attendu :
    {
        "name": "Player",
        "tags": ["PLAYER"],
        "transform": {"position": [0, 0], "rotation": 0.0},
        "components": [
            {"component": "physic_body", "data": {...}},
            {"component": "circle_collider", "data": {...}},
            ...
        ]
    }
    """

    def __init__(
        self,
        templates: dict[str, dict[str, Any]] | None = None,
        materials: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self._templates = templates or {}
        self._materials = materials or {}
        self._registry = Component.get_registered_components()
        for key in self._registry:
            logger.debug(f"Component registered in GameObjectFactory: {key}")

    def from_template(
        self,
        template_path: str,
        position: Optional[Vector2D] = None,
        rotation: Optional[float] = None,
        input_system: Optional["InputSystem"] = None,
    ) -> GameObject:
        template = self._templates.get(template_path)
        if template is None:
            raise FileNotFoundError(
                f"Template introuvable dans le registre: {template_path}"
            )

        game_object = self._create_base_object(template, position, rotation)

        context = {"input_system": input_system, "materials": self._materials}
        self._add_components(game_object, template, context)

        return game_object

    def _create_base_object(
        self,
        template: dict[str, Any],
        position: Optional[Vector2D],
        rotation: Optional[float],
    ) -> GameObject:
        transform_data = template.get("transform", {})
        pos = position if position is not None else self._parse_position(transform_data)
        rot_deg = (
            rotation if rotation is not None else transform_data.get("rotation", 0.0)
        )
        rot_rad = math.radians(rot_deg)
        transform = Transform(position=pos, rotation=rot_rad)

        tags = self._parse_tags(template.get("tags", []))

        name = template.get("name", "GameObject")
        return GameObject(name, transform, tags=tags)

    def _add_components(
        self,
        game_object: GameObject,
        template: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        components_data = template.get("components", [])
        if not isinstance(components_data, list):
            raise ValueError("Le champ 'components' doit etre une liste.")

        for entry in components_data:
            component_name = entry.get("component")
            if not component_name:
                raise ValueError("Un composant doit definir le champ 'component'.")

            data = entry.get("data", {})
            if data is None:
                data = {}

            component_cls = self._registry.get(component_name)
            if component_cls is None:
                raise ValueError(f"Composant inconnu : {component_name}")

            component = component_cls.from_data(data, context)
            game_object.add_component(component)

    @staticmethod
    def _parse_position(transform_data: dict[str, Any]) -> Vector2D:
        pos = transform_data.get("position", [0, 0])
        return Vector2D(pos[0], pos[1])

    @staticmethod
    def _parse_tags(tags_list: list[str]) -> Tag:
        result = Tag.NONE
        for tag_name in tags_list:
            if hasattr(Tag, tag_name):
                result |= getattr(Tag, tag_name)
        return result
