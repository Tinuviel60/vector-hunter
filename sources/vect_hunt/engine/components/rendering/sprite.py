from typing import Any

import pygame

from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.resources import ImageLoader


class Sprite(RenderComponent):
    """
    Composant de rendu base sur une image bitmap.
    """

    def __init__(self, image_path: str, scale: float = 1.0):
        super().__init__()
        self.original_image = ImageLoader.load(image_path)
        self.scale = scale

        if scale != 1.0:
            w, h = self.original_image.get_size()
            self.image = pygame.transform.scale(
                self.original_image, (int(w * scale), int(h * scale))
            )
        else:
            self.image = self.original_image

    @classmethod
    def from_data(
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "Sprite":
        image_path = data["image"]
        scale = data.get("scale", 1.0)
        return cls(image_path, scale=scale)

    def render(self, surface) -> None:
        assert self.game_object is not None, "Component must be attached to GameObject"
        transform = self.game_object.transform
        pos = transform.position
        rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        surface.blit(self.image, rect)
