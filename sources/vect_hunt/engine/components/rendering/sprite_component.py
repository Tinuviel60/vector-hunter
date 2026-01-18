from typing import Any

import pygame

from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.resources import ImageLoader


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
        cls, data: dict[str, Any], game_object, context: dict[str, Any]
    ) -> "SpriteComponent":
        """
        Cree un SpriteComponent a partir des donnees.

        Parameters
        ----------
        data : dict[str, Any]
            Données de configuration.
        game_object : GameObject
            Le GameObject auquel ce composant sera attaché.
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

    def render(self, surface) -> None:
        """
        Rend le sprite sur la surface donnee.

        Parameters
        ----------
        surface : pygame.Surface
            Surface sur laquelle dessiner le sprite.
        """
        assert self.game_object is not None, "Component must be attached to GameObject"
        transform = self.game_object.transform
        pos = transform.position
        rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
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
