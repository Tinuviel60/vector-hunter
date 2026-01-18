from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.resources.loaders.data_loader import DataLoader


class Scene:
    """
    Répresente une scene du jeu, contenant les cibles et le joueur.

    Attributes
    ----------
    game_objects : dict[int, GameObject]
        GameObjects présents dans la scène.
    units : dict
        Configuration des unités de la simulation (pixels/m, gravité...).
    """

    def __init__(self):
        """
        Initialise une scène de jeu vide.
        """
        self.game_objects: dict[int, GameObject] = {}

        self.units = self._load_units()

    @staticmethod
    def _load_units() -> dict:
        """
        Charge la configuration des unites physiques.
        """
        units = DataLoader.load_json("configs/units.json")
        pixels_per_meter = units.get("pixels_per_meter", 100.0)
        gravity_m_s2 = units.get("gravity_m_s2", 9.81)
        return {
            "pixels_per_meter": pixels_per_meter,
            "gravity_m_s2": gravity_m_s2,
        }

    def add_game_object(self, game_object: GameObject) -> None:
        """
        Ajoute un GameObject à la scène.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à ajouter.
        """
        game_object.name = self.validate_name(game_object.name)

        self.game_objects[game_object.id] = game_object

    def remove_game_object(self, game_object: GameObject) -> None:
        """
        Retire un GameObject de la scène.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à retirer.
        """
        if game_object.id in self.game_objects:
            del self.game_objects[game_object.id]

    def validate_name(self, name: str) -> str:
        """
        Valide et ajuste le nom d'un GameObject pour éviter les conflits.

        Parameters
        ----------
        name : str
            Le nom proposé pour le GameObject.

        Returns
        -------
        str
            Un nom unique pour le GameObject.
        """
        # Collecter tous les noms existants
        existing_names = {obj.name for obj in self.game_objects.values()}

        original_name = name
        counter = 1
        while name in existing_names:
            name = f"{original_name}_{counter}"
            counter += 1
        return name
