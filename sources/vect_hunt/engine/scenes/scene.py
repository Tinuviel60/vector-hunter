from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vect_hunt.engine.objects.game_object import GameObject


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

    def __init__(self, units: dict[str, float]):
        """
        Initialise une scène de jeu vide.
        """
        self.game_objects: dict[int, "GameObject"] = {}
        self.units = units

    @classmethod
    def from_data(cls, scene_data: Optional[dict[str, Any]] = None) -> "Scene":
        """
        Cree une Scene depuis des donnees JSON.

        Parameters
        ----------
        scene_data : dict[str, Any] | None
            Donnees de scene. Doit contenir 'units'.
        """
        if scene_data is None:
            raise ValueError("La scene doit definir les données.")

        units_data = scene_data.get("units")
        if units_data is None:
            raise ValueError("La scene doit definir les 'unités'.")

        pixels_per_meter = units_data.get("pixels_per_meter", 100.0)
        gravity_m_s2 = units_data.get("gravity_m_s2", 9.81)
        units = {
            "pixels_per_meter": pixels_per_meter,
            "gravity_m_s2": gravity_m_s2,
        }
        return cls(units)

    def add_game_object(self, game_object: "GameObject") -> None:
        """
        Ajoute un GameObject à la scène.

        Parameters
        ----------
        game_object : GameObject
            L'objet de jeu à ajouter.
        """
        game_object.name = self.validate_name(game_object.name)

        self.game_objects[game_object.id] = game_object

    def remove_game_object(self, game_object: "GameObject") -> None:
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
