import pygame
from typing import Tuple
from .render_component import RenderComponent
from vect_hunt.core import Transform, Vector2D
from vect_hunt.utils import hex_to_rgb


class BasicShape(RenderComponent):
    """
    Composant de rendu pour formes géométriques simples.
    """

    def __init__(
        self,
        transform: Transform,
        shape_type: str,
        size: Tuple[int, int] | int,
        color: str = "#FFFFFF",
        outline_color: str | None = None,
        outline_width: int = 1,
    ):
        """
        Parameters
        ----------
        shape_type : str
            "circle" ou "box".
        size : int | Tuple[int, int]
            Rayon pour un cercle, (width, height) pour un rectangle.
        color : str
            Couleur principale en hexadécimal.
        outline_color : str, optional
            Couleur du contour.
        outline_width : int
            Épaisseur du contour.
        """
        self.transform = transform
        self.shape_type = shape_type
        self.size = size
        self.color = color
        self.outline_color = outline_color
        self.outline_width = outline_width

    def render(self, surface, transform: Transform) -> None:
        """
        Dessine la forme sur la surface donnée.
        
        Parameters
        ----------
        surface
            Surface de rendu (ex: pygame.Surface).
        transform : Transform
            Transformation spatiale du GameObject."""
        pos = transform.position
        x, y = int(pos.x), int(pos.y)

        if self.shape_type == "circle":
            assert isinstance(self.size, int), "Size must be an int for circle shape"
            radius = int(self.size)
            pygame.draw.circle(
                surface, hex_to_rgb(self.color), (x, y), radius
            )
            if self.outline_color:
                pygame.draw.circle(
                    surface,
                    hex_to_rgb(self.outline_color),
                    (x, y),
                    radius,
                    self.outline_width,
                )

        elif self.shape_type == "box":
            assert isinstance(
                self.size, tuple
            ), "Size must be a tuple for box shape"
            width, height = self.size
            
            # Calculer les 4 coins du rectangle dans l'espace local (centré sur l'origine)
            half_w, half_h = width / 2, height / 2
            local_corners = [
                Vector2D(-half_w, -half_h),  # Top-left
                Vector2D(half_w, -half_h),   # Top-right
                Vector2D(half_w, half_h),    # Bottom-right
                Vector2D(-half_w, half_h),   # Bottom-left
            ]
            
            # Appliquer la rotation et translater vers la position du GameObject
            # (même logique que ColliderSystem.get_world_corners)
            world_corners = []
            for corner in local_corners:
                corner_rotated = transform.rotation.apply(corner)
                world_corner = transform.position + corner_rotated
                world_corners.append(world_corner)
            
            # Convertir en points pygame
            points = [(int(corner.x), int(corner.y)) for corner in world_corners]
            
            # Dessiner le polygone
            pygame.draw.polygon(surface, hex_to_rgb(self.color), points)
            if self.outline_color:
                pygame.draw.polygon(
                    surface,
                    hex_to_rgb(self.outline_color),
                    points,
                    self.outline_width,
                )
