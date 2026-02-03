from typing import TYPE_CHECKING, Any, Optional, cast

import pygame
from vect_hunt.engine.components.collider.box_collider_component import (
    BoxColliderComponent,
)
from vect_hunt.engine.core.geometries.box_shape import BoxShape
from vect_hunt.engine.core.geometries.circle_shape import CircleShape
from vect_hunt.engine.core.math.vector import Vector2D
from vect_hunt.engine.core.render_ops import RenderOps
from vect_hunt.engine.rendering.font.font_system import FontSystem

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject
    from vect_hunt.engine.scenes.scene import Scene
    from vect_hunt.engine.components.render_component import RenderComponent
    from vect_hunt.engine.components.collider.collider_component import (
        ColliderComponent
    )

"""
Module de rendu pour le jeu Vector Hunter.
Contient la classe Renderer qui gère l'affichage graphique du jeu.
"""


class Viewport:
    """
    Convertit les coordonnées monde (Y-up) vers l'espace écran Pygame (Y-down).

    Par défaut, l'origine monde (0,0) est mappée en bas-gauche de l'écran.
    """

    __slots__ = ("width", "height", "scale", "origin")

    def __init__(
        self,
        width: int,
        height: int,
        scale: float = 1.0,
        origin: Optional[Vector2D] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.origin = origin if origin is not None else Vector2D(0.0, float(height))

    @classmethod
    def from_screen(
        cls,
        screen: pygame.Surface,
        scale: float = 1.0,
        origin: Optional[Vector2D] = None,
    ) -> "Viewport":
        width, height = screen.get_size()
        return cls(width, height, scale=scale, origin=origin)

    def world_to_screen(self, point: Vector2D) -> Vector2D:
        return Vector2D(
            self.origin.x + point.x * self.scale,
            self.origin.y - point.y * self.scale,
        )

    def world_to_screen_xy(self, x: float, y: float) -> tuple[float, float]:
        return (
            self.origin.x + x * self.scale,
            self.origin.y - y * self.scale,
        )

    def screen_to_world(self, point: Vector2D) -> Vector2D:
        return Vector2D(
            (point.x - self.origin.x) / self.scale,
            (self.origin.y - point.y) / self.scale,
        )

    def screen_to_world_xy(self, x: float, y: float) -> tuple[float, float]:
        return (
            (x - self.origin.x) / self.scale,
            (self.origin.y - y) / self.scale,
        )

    def world_vec_to_screen(self, vec: Vector2D) -> Vector2D:
        return Vector2D(vec.x * self.scale, -vec.y * self.scale)

    def screen_vec_to_world(self, vec: Vector2D) -> Vector2D:
        return Vector2D(vec.x / self.scale, -vec.y / self.scale)


class Renderer:
    """
    Classe responsable du rendu graphique du jeu.
    Gère l'affichage du fond de carte, du joueur et des entités.

    Attributes
    ----------
    screen : pygame.Surface
        Surface Pygame de rendu.
    background_color : str
        Couleur de fond en hexadécimal.
    draw_colliders : bool
        Indique si les colliders sont dessinés en debug.
    print_names : bool
        Indique si les noms des GameObjects sont affichés.
    print_fps : bool
        Indique si les FPS sont affichés.
    collider_color : str
        Couleur des colliders en hexadécimal.
    collider_thickness : int
        Épaisseur des colliders en pixels.
    debug_font_style : FontStyle
        Style de police pour le debug.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        config: dict[str, Any],
        font_system: FontSystem,
    ):
        """
        Initialise le renderer.

        Parameters
        ----------
        screen : pygame.Surface
            La surface Pygame où le jeu sera rendu.
        """
        self.screen = screen
        self.background_color = config["background_color"]

        # Options de debug depuis la config
        debug_config = config["debug"]
        self.draw_colliders = debug_config["draw_colliders"]
        self.print_names = debug_config["print_names"]
        self.draw_grid = debug_config["draw_grid"]
        self.grid_spacing_pixels = debug_config["grid_spacing_pixels"]
        self.print_fps = debug_config["print_fps"]
        self.color_for_valid = debug_config["color_for_valid"]
        self.color_for_invalid = debug_config["color_for_invalid"]
        self.collider_thickness = debug_config["collider_thickness"]

        viewport_config = config.get("viewport", {})
        viewport_scale = float(viewport_config.get("scale", 1.0))
        origin_data = viewport_config.get("origin")
        origin = None
        if isinstance(origin_data, (list, tuple)) and len(origin_data) == 2:
            origin = Vector2D(float(origin_data[0]), float(origin_data[1]))

        self.viewport = Viewport.from_screen(
            self.screen, scale=viewport_scale, origin=origin
        )

        # Style de police pour le debug (géré par FontSystem)
        self.debug_font_style = font_system.get("debug")

        self.grid_surface = None
        if self.draw_grid:
            self.grid_surface = self.build_grid_surface(self.grid_spacing_pixels)

    def clear(self) -> None:
        """
        Efface l'écran avec la couleur de fond.
        """
        self.screen.fill(RenderOps.hex_to_rgb(self.background_color))

    def draw_background(self) -> None:
        """
        Dessine le fond de la carte.
        """
        self.clear()

    def draw_game_objects(self, game_objects: dict[int, "GameObject"]) -> None:
        """
        Dessine toutes les cibles de la liste.

        Parameters
        ----------
        game_objects : dict[str, GameObject]
            Objet du jeu à dessiner.
        """
        for game_object in game_objects.values():
            if not game_object.active:
                continue

            # Dessine le GameObject via son composant de rendu
            self.render_game_object(game_object)
            # Dessine le nom
            if self.print_names:
                self.draw_name(game_object)
            # Dessine les colliders
            if self.draw_colliders:
                colliders = cast(list["ColliderComponent"], game_object.get_components("collider"))
                for collider in colliders:
                    self.draw_collider(
                        collider,
                        False,  # TODO : Passer l'info de collision réelle
                    )

    def draw_grid_lines(self, spacing: float) -> None:
        """
        Dessine une grille sur l'écran pour le debug.

        Parameters
        ----------
        spacing : float
            Espacement entre les lignes de la grille en pixels.
        """
        if self.grid_surface is not None:
            self.screen.blit(self.grid_surface, (0, 0))

    def build_grid_surface(self, spacing: float) -> pygame.Surface:
        """
        Construit une surface contenant la grille de debug pré-rendue.

        Cette surface peut ensuite être blitée telle quelle à chaque frame,
        afin d'éviter de redessiner ligne par ligne la grille en permanence.

        Parameters
        ----------
        spacing : float
            Espacement entre les lignes de la grille en pixels.

        Returns
        -------
        pygame.Surface
            Surface contenant la grille pré-rendue.
        """
        width, height = self.screen.get_size()
        color = (200, 200, 200)

        # Surface avec canal alpha pour superposition propre
        grid_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        grid_surface = grid_surface.convert_alpha()

        # Bornes monde visibles
        world_tl = self.viewport.screen_to_world(Vector2D(0.0, 0.0))
        world_br = self.viewport.screen_to_world(Vector2D(float(width), float(height)))
        min_x = min(world_tl.x, world_br.x)
        max_x = max(world_tl.x, world_br.x)
        min_y = min(world_tl.y, world_br.y)
        max_y = max(world_tl.y, world_br.y)

        step = max(1.0, float(spacing))

        # Lignes verticales
        x = (int(min_x // step) * step)
        while x <= max_x:
            screen_x, _ = self.viewport.world_to_screen_xy(x, 0.0)
            screen_x_int = int(screen_x)
            pygame.draw.line(
                grid_surface, color, (screen_x_int, 0), (screen_x_int, height), 1
            )
            pixel_place = self.debug_font_style.render(str(int(x)))
            grid_surface.blit(pixel_place, (screen_x_int, 0))
            x += step

        # Lignes horizontales
        y = (int(min_y // step) * step)
        while y <= max_y:
            _, screen_y = self.viewport.world_to_screen_xy(0.0, y)
            screen_y_int = int(screen_y)
            pygame.draw.line(
                grid_surface, color, (0, screen_y_int), (width, screen_y_int), 1
            )
            pixel_place = self.debug_font_style.render(str(int(y)))
            grid_surface.blit(pixel_place, (0, screen_y_int))
            y += step

        return grid_surface

    def draw_name(self, game_object: "GameObject") -> None:
        """
        Dessine le nom d'un GameObject au-dessus de celui-ci.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu dont le nom doit être dessiné.
        """
        name_surf = self.debug_font_style.render(game_object.name)
        pos = game_object.transform.position
        label_world = Vector2D(pos.x, pos.y + 20.0)
        label_screen = self.viewport.world_to_screen(label_world)
        self.screen.blit(
            name_surf,
            (
                int(label_screen.x - name_surf.get_width() / 2),
                int(label_screen.y),
            ),
        )

    def draw_collider(self, collider: "ColliderComponent", is_colliding: bool = False):
        """
        Dessine un collider pour le debug.

        Parameters
        ----------
        collider : ColliderComponent
            Le collider à dessiner.
        is_colliding : bool
            Indique si le GameObject est actuellement en collision.
        """
        shape = collider.shape

        # Couleur rouge si en collision, vert sinon
        color = self.color_for_invalid if is_colliding else self.color_for_valid

        if isinstance(shape, CircleShape):
            # Pour les cercles, center est local et on ajoute la position du GameObject
            col_tr = collider.get_scene_transform()
            col_pos = col_tr.position
            center_pos = self.viewport.world_to_screen(col_pos)
            center = (int(center_pos.x), int(center_pos.y))
            radius = int(shape.radius * self.viewport.scale)
            pygame.draw.circle(
                self.screen, color, center, radius, self.collider_thickness
            )

        elif isinstance(shape, BoxShape):
            # Pour les polygones, les points incluent déjà la position absolue
            assert isinstance(collider, BoxColliderComponent)
            corners = collider.get_scene_corners()
            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (
                        int(screen_corner.x),
                        int(screen_corner.y),
                    )
                    for screen_corner in (self.viewport.world_to_screen(p) for p in corners)
                ],
                self.collider_thickness,
            )

    def render_game_object(self, game_object: "GameObject") -> None:
        """
        Dessine le composant de rendu d'un GameObject.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à dessiner.
        """

        render_component = cast("RenderComponent | None", game_object.get_component("render"))
        if not render_component:
            return

        # Le composant utilise directement game_object.transform
        render_component.render(self.screen, self.viewport)

    def render(self, scene: "Scene") -> None:
        """
        Rend une frame complète du jeu.

        Parameters
        ----------
        scene : Scene
            L'état actuel de la scène du jeu, contenant les informations
            des objets de jeu.
        """
        self.draw_background()

        if self.draw_grid:
            self.draw_grid_lines(self.grid_spacing_pixels)

        self.draw_game_objects(scene.game_objects)
        pygame.display.flip()

    def set_background_color(self, color: str = "#414141") -> None:
        """
        Définit la couleur de fond.

        Parameters
        ----------
        color : str, optional
            Couleur de fond en hexadécimal, par défaut "#414141".
        """
        self.background_color = color
