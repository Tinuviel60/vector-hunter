import pygame
from .render_component import RenderComponent
from vect_hunt.core import Transform


class Sprite(RenderComponent):
    """
    Composant de rendu basé sur une image bitmap.
    """

    def __init__(self, image_path: str, scale: float = 1.0):
        """
        Parameters
        ----------
        image_path : str
            Chemin vers l'image.
        scale : float
            Facteur d'échelle.
        """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.scale = scale

        if scale != 1.0:
            w, h = self.original_image.get_size()
            self.image = pygame.transform.scale(
                self.original_image, (int(w * scale), int(h * scale))
            )
        else:
            self.image = self.original_image

    def render(self, surface, transform: Transform) -> None:
        pos = transform.position
        rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        surface.blit(self.image, rect)
