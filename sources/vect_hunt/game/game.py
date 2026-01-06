
from vect_hunt.rendering import Render

class Game:
    """
    Main game class that handles initialization, update loop, and rendering.
    """
    
    def __init__(self) -> None:
        """
        Initialize le jeu pour la partie.

        """
        self.initialize()
        

        
    def initialize(self) -> None:
        """
        Initialise les composants du jeu.
        """
        # TODO: Initialize game components, load assets, etc.
        pass

        # On affecte un renderer au jeu
        self.renderer = Renderer()
        
    def update(self, delta_time: float) -> None:
        """
        Met à jour la logique du jeu.
        
        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour (en secondes).
        """
        # TODO: Update game state, entities, physics, etc.
        pass
        
    def render(self) -> None:
        """
        Rendu graphique du jeu.
        """

        self.renderer.render()
            

            
