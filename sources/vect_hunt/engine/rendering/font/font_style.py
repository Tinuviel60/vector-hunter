import pygame
from typing import Optional

"""
Représentation d'un style de police pour le rendu.
"""


class FontStyle:
    """
    Représente un style de police complet avec tous ses attributs de rendu.

    Cette classe est responsable du rendu visuel du texte via pygame.

    Attributes
    ----------
    font : pygame.font.Font
        Police pygame chargée
    color : tuple[int, int, int]
        Couleur RGB du texte
    antialias : bool
        Si True, active l'antialiasing
    """

    def __init__(
        self,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        antialias: bool = True,
    ):
        """
        Initialise un style de police.

        Parameters
        ----------
        font : pygame.font.Font
            Police pygame à utiliser
        color : tuple[int, int, int]
            Couleur RGB du texte (0-255)
        antialias : bool, optional
            Active l'antialiasing, par défaut True
        """
        self.font = font
        self.color = color
        self.antialias = antialias

    def render(
        self, text: str, background: Optional[tuple[int, int, int]] = None
    ) -> pygame.Surface:
        """
        Rend du texte avec ce style.

        Parameters
        ----------
        text : str
            Texte à afficher
        background : tuple[int, int, int], optional
            Couleur de fond RGB. Si None, fond transparent.

        Returns
        -------
        pygame.Surface
            Surface contenant le texte rendu
        """
        return self.font.render(text, self.antialias, self.color, background)
