import pygame
from typing import Tuple, TYPE_CHECKING

from vect_hunt.utils import hex_to_rgb
from vect_hunt.systems import ColliderSystem, FontSystem
from vect_hunt.resources import DataLoader

if TYPE_CHECKING:
    from vect_hunt.objects import GameObject
    from vect_hunt.worlds import World

"""
Module de rendu pour le jeu Vector Hunter.
Contient la classe Renderer qui gère l'affichage graphique du jeu.
"""


class Renderer:
    """
    Classe responsable du rendu graphique du jeu.
    Gère l'affichage du fond de carte, du joueur et des entités.
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
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.background_color = config["background_color"]

        # Options de debug depuis la config
        debug_config = config["debug"]
        self.draw_colliders = debug_config["draw_colliders"]
        self.print_names = debug_config["print_names"]
        self.print_fps = debug_config["print_fps"]
        self.collider_color = debug_config["collider_color"]
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

            # Dessine le GameObject
            if game_object.render_component:
                self.draw_render(game_object)
            # Dessine le nom
            if self.print_names:
                self.draw_name(game_object)
            # Dessine les colliders
            if self.draw_colliders:
                for collider in game_object.colliders:
                    self.draw_collider(collider, game_object.transform)

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

    def draw_collider(self, collider, transform):
        """
        Dessine un collider pour le debug.

        Parameters
        ----------
        collider : Collider
            Le collider à dessiner.
        transform : Transform
            La transformation du GameObject auquel le collider appartient."""
        geom = collider.get_geometry()

        if geom["type"] == "circle":
            # Pour les cercles, center est local et on ajoute la position du GameObject
            center_vec = transform.position + collider.transform.position
            center = (int(center_vec.x), int(center_vec.y))
            pygame.draw.circle(
                self.screen,
                (0, 255, 0),
                center,
                int(geom["radius"]),
                1,
            )

        elif geom["type"] == "box":
            # Pour les polygones, les points incluent déjà la position absolue
            points = ColliderSystem.get_world_corners(geom["points"], transform)
            pygame.draw.polygon(
                self.screen,
                (0, 255, 0),
                [(int(p.x), int(p.y)) for p in points],
                1,
            )

    def draw_render(self, game_object: "GameObject") -> None:
        """
        Dessine le composant de rendu d'un GameObject.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à dessiner.
        """
        if not game_object.render_component:
            return

        # On utilise directement le transform du GameObject pour le rendu
        game_object.render_component.render(self.screen, game_object.transform)

    def render(self, world: "World") -> None:
        """
        Rend une frame complète du jeu.

        Parameters
        ----------
        world : World
            L'état actuel du monde du jeu, contenant les informations des objets de jeu.
        """
        self.draw_background()
        self.draw_game_objects(world.game_objects)
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
