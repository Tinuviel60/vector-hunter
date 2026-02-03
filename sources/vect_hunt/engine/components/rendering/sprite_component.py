from typing import Any

import pygame
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.resources.loaders.image_loader import ImageLoader


class SpriteComponent(RenderComponent):
    """
    Composant de rendu base sur une image bitmap.
    """

    component_name = "sprite"

    def __init__(self, image_path: str, scale: float = 1.0):
        """
        Initialise le SpriteComponent avec le chemin de l'image et l'echelle.

        Parameters
        ----------
        image_path : str
            Chemin vers le fichier image.
        scale : float, optional
            Echelle d'affichage de l'image (par defaut 1.0).
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

    @classmethod
    def from_data(
        cls, data: dict[str, Any], context: dict[str, Any]
    ) -> "SpriteComponent":
        """
        Cree un SpriteComponent a partir des donnees.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        context : dict[str, Any]
            Contexte additionnel pour la création (ex: références aux systèmes).

        Returns
        -------
        InputComponent
            Instance du composant créé.
        """
        image_path = data["image"]
        scale = data.get("scale", 1.0)
        return cls(image_path, scale=scale)

    def render(self, surface, viewport=None) -> None:
        """
        Rend le sprite sur la surface donnee.

        Parameters
        ----------
        surface : pygame.Surface
            Surface sur laquelle dessiner le sprite.
        """
        transform = self.parent.transform
        pos = transform.position
        if viewport is not None:
            screen_pos = viewport.world_to_screen(pos)
            center = (int(screen_pos.x), int(screen_pos.y))
        else:
            center = (int(pos.x), int(pos.y))
        rect = self.image.get_rect(center=center)
        surface.blit(self.image, rect)

    def update(self, delta_time: float) -> None:
        """
        Met a jour le sprite si necessaire.

        Parameters
        ----------
        delta_time : float
            Temps ecoule depuis la derniere mise a jour.
        """
        pass
