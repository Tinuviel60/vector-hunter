import pygame
from typing import Tuple, TYPE_CHECKING

from vect_hunt.engine.core.math import hex_to_rgb
from vect_hunt.engine.physics.collider_system import ColliderSystem
from vect_hunt.engine.rendering.font import FontSystem
from vect_hunt.engine.components.render_component import RenderComponent
from vect_hunt.engine.components.collider import ColliderComponent, BoxColliderComponent
from vect_hunt.engine.resources.loaders.data_loader import DataLoader
from vect_hunt.engine.core.geometries import BoxShape, CircleShape

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject
    from vect_hunt.engine.scenes import Scene

"""
Module de rendu pour le jeu Vector Hunter.
Contient la classe Renderer qui gère l'affichage graphique du jeu.
"""


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

    def __init__(self, screen: pygame.Surface):
        """
        Initialise le renderer.

        Parameters
        ----------
        screen : pygame.Surface
            La surface Pygame où le jeu sera rendu.
        """
        # Charger la configuration du renderer
        config = DataLoader.load_json("configs/renderer.json")

        self.screen = screen
        self.background_color = config["background_color"]

        # Options de debug depuis la config
        debug_config = config["debug"]
        self.draw_colliders = debug_config["draw_colliders"]
        self.print_names = debug_config["print_names"]
        self.print_fps = debug_config["print_fps"]
        self.color_for_valid = debug_config["color_for_valid"]
        self.color_for_invalid = debug_config["color_for_invalid"]
        self.collider_thickness = debug_config["collider_thickness"]

        # Style de police pour le debug (géré par FontSystem)
        self.debug_font_style = FontSystem.get("debug")

    def clear(self) -> None:
        """
        Efface l'écran avec la couleur de fond.
        """
        self.screen.fill(hex_to_rgb(self.background_color))

    def draw_background(self) -> None:
        """
        Dessine le fond de la carte.
        """
        self.clear()

    def draw_player(
        self, position: Tuple[float, float], radius: int = 15, color: str = "#64C8FF"
    ) -> None:
        """
        Dessine le joueur sous forme de cercle.

        Parameters
        ----------
        position : Tuple[float, float]
            Position (x, y) du joueur.
        radius : int, optional
            Rayon du cercle représentant le joueur, par défaut 15.
        color : str, optional
            Couleur du joueur en hexadécimal, par défaut "#64C8FF".
        """
        pos = (int(position[0]), int(position[1]))
        pygame.draw.circle(self.screen, hex_to_rgb(color), pos, radius)
        # Bordure plus foncée
        pygame.draw.circle(self.screen, (50, 100, 150), pos, radius, 2)

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

            # DEBUG: Affiche le compteur de collisions
            # Dessine le GameObject via son composant de rendu
            self.render_game_object(game_object)
            # Dessine le nom
            if self.print_names:
                self.draw_name(game_object)
            # Dessine les colliders
            if self.draw_colliders:
                colliders = game_object.get_components(ColliderComponent)
                for collider in colliders:
                    self.draw_collider(
                        collider,
                        collider.nb_collision > 0,
                    )

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
        self.screen.blit(
            name_surf,
            (int(pos.x - name_surf.get_width() / 2), int(pos.y - 20)),
        )

    def draw_collider(self, collider: ColliderComponent, is_colliding: bool = False):
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
            col_tr = ColliderSystem.get_collider_scene_transform(collider)
            col_pos = col_tr.position
            center = (int(col_pos.x), int(col_pos.y))
            pygame.draw.circle(
                self.screen, color, center, int(shape.radius), self.collider_thickness
            )

        elif isinstance(shape, BoxShape):
            # Pour les polygones, les points incluent déjà la position absolue
            assert isinstance(collider, BoxColliderComponent)
            corners = ColliderSystem.get_scene_corners(collider)
            pygame.draw.polygon(
                self.screen,
                color,
                [(int(p.x), int(p.y)) for p in corners],
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

        render_component = game_object.get_component(RenderComponent)
        if not render_component:
            return

        # Le composant utilise directement game_object.transform
        render_component.render(self.screen)

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
