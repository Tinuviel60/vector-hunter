import pygame
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.resources import ImageLoader


class Sprite(RenderComponent):
    """
    Composant de rendu basé sur une image bitmap.

    Attributes
    ----------
    game_object : GameObject | None
        GameObject auquel ce composant est attaché.
    active : bool
        Indique si le composant est actif.
    original_image : pygame.Surface
        Image source chargée.
    image : pygame.Surface
        Image mise à l'échelle si nécessaire.
    scale : float
        Facteur d'échelle.
    """

    def __init__(self, image_path: str, scale: float = 1.0):
        """
        Parameters
        ----------
        image_path : str
            Chemin relatif vers l'image depuis assets/images/
        scale : float
            Facteur d'échelle.
        """
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

    def render(self, surface) -> None:
        """
        Dessine le sprite sur la surface donnée.

        Parameters
        ----------
        surface
            Surface de rendu (ex: pygame.Surface).
        """
        assert self.game_object is not None, "Component must be attached to GameObject"
        transform = self.game_object.transform
        pos = transform.position
        rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        surface.blit(self.image, rect)
