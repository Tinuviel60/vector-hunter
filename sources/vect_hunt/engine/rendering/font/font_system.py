import pygame
from vect_hunt.engine.rendering.font.font_style import FontStyle
from vect_hunt.engine.resources import DataLoader, FontLoader
from vect_hunt.engine.core.math import hex_to_rgb

"""
Système de gestion centralisée des styles de polices.
"""


class FontSystem:
    """
    Système responsable de la gestion des styles de polices.

    Charge les définitions depuis fonts.json et crée des FontStyle
    prêts à être utilisés par les composants de rendu.

    Ce système ne s'occupe PAS du rendu, seulement de la gestion
    et de la création des styles.

    Attributes
    ----------
    None
    """

    _styles: dict[str, FontStyle] = {}
    _config_loaded: bool = False

    @classmethod
    def _load_config(cls) -> None:
        """
        Charge la configuration des polices depuis fonts.json.

        Initialise tous les styles définis dans la configuration.
        """
        if cls._config_loaded:
            return

        config = DataLoader.load_json("configs/fonts.json")

        for style_name, style_def in config.items():
            # Ignorer les clés de métadonnées
            if style_name.startswith("_"):
                continue

            # Charger la police selon son type
            font_type = style_def["type"]
            size = style_def["size"]
            bold = style_def.get("bold", False)
            italic = style_def.get("italic", False)

            if font_type == "system":
                # Police système (Arial, etc.)
                font = pygame.font.SysFont(
                    style_def["name"], size, bold=bold, italic=italic
                )
            elif font_type == "file":
                # Police custom depuis assets/fonts/
                font = FontLoader.load(style_def["path"], size)
                # Note: bold/italic ne s'appliquent pas aux polices custom
            else:
                raise ValueError(f"Type de police inconnu : {font_type}")

            # Convertir la couleur hex en RGB
            color = hex_to_rgb(style_def["color"])
            antialias = style_def.get("antialias", True)

            cls._styles[style_name] = FontStyle(font, color, antialias)

        cls._config_loaded = True

    @classmethod
    def get(cls, style_name: str) -> FontStyle:
        """
        Récupère un style de police par son nom.

        Parameters
        ----------
        style_name : str
            Nom du style défini dans fonts.json
            Exemple : "debug", "ui_title", "dialog"

        Returns
        -------
        FontStyle
            Style de police prêt à utiliser pour le rendu

        Raises
        ------
        KeyError
            Si le style n'existe pas dans fonts.json
        """
        cls._load_config()

        if style_name not in cls._styles:
            raise KeyError(
                f"Style de police inconnu : '{style_name}'. "
                f"Styles disponibles : {list(cls._styles.keys())}"
            )

        return cls._styles[style_name]

    @classmethod
    def reload(cls) -> None:
        """
        Recharge la configuration des polices.

        Utile pour le hot-reload pendant le développement.
        Vide le cache et force un rechargement complet.
        """
        cls._styles.clear()
        cls._config_loaded = False
        DataLoader.reload("configs/fonts.json")
        cls._load_config()

    @classmethod
    def get_available_styles(cls) -> list[str]:
        """
        Retourne la liste des styles disponibles.

        Returns
        -------
        list[str]
            Liste des noms de styles chargés
        """
        cls._load_config()
        return list(cls._styles.keys())
