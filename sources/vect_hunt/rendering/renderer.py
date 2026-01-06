import pygame
from typing import List, Tuple

from vect_hunt.worlds import World
from vect_hunt.utils import hex_to_rgb

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
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.background_color = "#414141"  # Gris par défaut

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


    def draw_player(self, position: Tuple[float, float], radius: int = 15, 
                   color: str = "#64C8FF") -> None:
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

    def draw_entity(self, position: Tuple[float, float], radius: int = 10,
                   color: str = "#FF6464") -> None:
        """
        Dessine une entité sous forme de cercle.

        Parameters
        ----------
        position : Tuple[float, float]
            Position (x, y) de l'entité.
        radius : int, optional
            Rayon du cercle représentant l'entité, par défaut 10.
        color : str, optional
            Couleur de l'entité en hexadécimal, par défaut "#FF6464".
        """
        pos = (int(position[0]), int(position[1]))
        pygame.draw.circle(self.screen, hex_to_rgb(color), pos, radius)
        # Bordure plus foncée
        pygame.draw.circle(self.screen, hex_to_rgb("#963232"), pos, radius, 2)

    def draw_targets(self, targets: List[dict]) -> None:
        """
        Dessine toutes les cibles de la liste.

        Parameters
        ----------
        targets : List[dict]
            Liste de dictionnaires contenant les informations des cibles.
            Chaque dict doit avoir: 'position', 'radius' (optionnel), 'color' (optionnel)
        """
        for target in targets:
            position = target.get('position', (0, 0))
            radius = target.get('radius', 10)
            color = target.get('color', "#FF6464")
            self.draw_entity(position, radius, color)

    def render(self, world : World) -> None:
        """
        Rend une frame complète du jeu.

        Parameters
        ----------
        world : World
            L'état actuel du monde du jeu, contenant les informations du joueur et des entités.
        """
        self.draw_background()
        # TODO : Implementer le dessin des entités et du joueur
        #self.draw_entities(world.targets)
        #self.draw_player(world.player.position)
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