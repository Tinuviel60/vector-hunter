from typing import Any, Tuple

import pygame
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.render_ops import RenderOps


class BasicShapeComponent(RenderComponent):
    """
    Composant de rendu pour formes geometriques simples.
    """

    component_name = "basic_shape"

    def __init__(
        self,
        shape_type: str,
        size: Tuple[int, int] | int,
        color: str = "#FFFFFF",
        outline_color: str | None = None,
        outline_width: int = 1,
    ):
        super().__init__()
        self.shape_type = shape_type
        self.size = size
        self.color = color
        self.outline_color = outline_color
        self.outline_width = outline_width

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "BasicShapeComponent":
        """
        Cree un BasicShapeComponent a partir des données sérialisées.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        BasicShapeComponent
            Instance du composant créé.
        """
        render_type = data.get("type")
        if render_type != "basic_shape":
            raise ValueError(f"Type de rendu inconnu : {render_type}")

        shape = data["shape"]
        color = data["color"]

        if shape == "circle":
            size = data["radius"]
            shape_type = "circle"
        elif shape in ("rectangle", "box"):
            size = (data.get("width", 20), data.get("height", 20))
            shape_type = "box"
        else:
            raise ValueError(f"Forme inconnue : {shape}")

        outline_color = data.get("outline_color")
        outline_width = data.get("outline_width", 1)

        return cls(shape_type, size, color, outline_color, outline_width)

    def render(self, surface) -> None:
        transform = self.parent.transform
        pos = transform.position
        x, y = int(pos.x), int(pos.y)

        if self.shape_type == "circle":
            assert isinstance(self.size, int), "Size must be an int for circle shape"
            radius = int(self.size)
            pygame.draw.circle(
                surface, RenderOps.hex_to_rgb(self.color), (x, y), radius
            )
            if self.outline_color:
                pygame.draw.circle(
                    surface,
                    RenderOps.hex_to_rgb(self.outline_color),
                    (x, y),
                    radius,
                    self.outline_width,
                )

        elif self.shape_type == "box":
            assert isinstance(self.size, tuple), "Size must be a tuple for box shape"
            width, height = self.size

            half_w, half_h = width / 2, height / 2
            local_corners = [
                Vector2D(-half_w, -half_h),
                Vector2D(half_w, -half_h),
                Vector2D(half_w, half_h),
                Vector2D(-half_w, half_h),
            ]

            scene_corners = []
            for corner in local_corners:
                corner_rotated = transform.rotation.apply(corner)
                scene_corner = transform.position + corner_rotated
                scene_corners.append(scene_corner)

            points = [(int(corner.x), int(corner.y)) for corner in scene_corners]

            pygame.draw.polygon(surface, RenderOps.hex_to_rgb(self.color), points)
            if self.outline_color:
                pygame.draw.polygon(
                    surface,
                    RenderOps.hex_to_rgb(self.outline_color),
                    points,
                    self.outline_width,
                )

    def update(self, delta_time: float) -> None:
        """
        Met a jour le composant de forme basique si necessaire.

        Parameters
        ----------
        delta_time : float
            Temps écoulé depuis la dernière frame (en secondes).
        """
        pass
