from pathlib import Path

"""
Gestion centralisée des chemins de ressources.
"""

# __file__ = .../vector-hunter/sources/vect_hunt/engine/resources/paths.py
# parents[0] = resources/, parents[1] = engine/, parents[2] = vect_hunt/
# parents[3] = sources/, parents[4] = vector-hunter/ (PROJECT_ROOT)
PROJECT_ROOT = Path(__file__).resolve().parents[4]

COMPONENTS_DIR = PROJECT_ROOT / "sources" / "vect_hunt" / "engine" / "components"
GAME_DIR = PROJECT_ROOT / "sources" / "vect_hunt" / "game"

ASSETS_ROOT = PROJECT_ROOT / "sources" / "vect_hunt" / "assets"
IMAGES_DIR = ASSETS_ROOT / "images"
SOUNDS_DIR = ASSETS_ROOT / "sounds"
FONTS_DIR = ASSETS_ROOT / "fonts"
DATA_DIR = ASSETS_ROOT / "data"

TEMPLATE_DIR = DATA_DIR / "templates"
CONFIGS_DIR = DATA_DIR / "configs"
SCENES_DIR = DATA_DIR / "scenes"
MATERIALS_DIR = DATA_DIR / "materials"

TEMPLATE_ROOT = "templates"
CONFIGS_ROOT = "configs"
SCENES_ROOT = "scenes"
MATERIALS_ROOT = "materials"




class Paths:
    """
    Classe wrapper pour accès aux chemins.

    Attributes
    ----------
    PROJECT_ROOT : Path
        Racine du projet.
    COMPONENTS_DIR : Path
        Dossier des components.
    GAME_DIR : Path
        Dossier du jeu.
    ASSETS_ROOT : Path
        Racine des assets.
    IMAGES_DIR : Path
        Dossier des images.
    SOUNDS_DIR : Path
        Dossier des sons.
    DATA_DIR : Path
        Dossier des données.
    FONTS_DIR : Path
        Dossier des polices.
    TEMPLATE_DIR : Path
        Dossier des templates.
    CONFIGS_DIR : Path
        Dossier des configurations.
    SCENES_DIR : Path
        Dossier des scènes.
    MATERIALS_DIR : Path
        Dossier des materials.
    TEMPLATE_ROOT : str
        Racine relative des templates.
    CONFIGS_ROOT : str
        Racine relative des configurations.
    SCENES_ROOT : str
        Racine relative des scenes.
    MATERIALS_ROOT : str
        Racine relative des materials.
    """

    PROJECT_ROOT = PROJECT_ROOT
    COMPONENTS_DIR = COMPONENTS_DIR
    GAME_DIR = GAME_DIR
    ASSETS_ROOT = ASSETS_ROOT
    IMAGES_DIR = IMAGES_DIR
    SOUNDS_DIR = SOUNDS_DIR
    DATA_DIR = DATA_DIR
    FONTS_DIR = FONTS_DIR
    TEMPLATE_DIR = TEMPLATE_DIR
    CONFIGS_DIR = CONFIGS_DIR
    SCENES_DIR = SCENES_DIR
    MATERIALS_DIR = MATERIALS_DIR
    TEMPLATE_ROOT = TEMPLATE_ROOT
    CONFIGS_ROOT = CONFIGS_ROOT
    SCENES_ROOT = SCENES_ROOT
    MATERIALS_ROOT = MATERIALS_ROOT

path = Paths()
