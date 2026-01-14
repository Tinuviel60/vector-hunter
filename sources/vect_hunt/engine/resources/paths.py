from pathlib import Path

"""
Gestion centralisée des chemins de ressources.
"""

# __file__ = .../vector-hunter/sources/vect_hunt/engine/resources/paths.py
# parents[0] = resources/, parents[1] = engine/, parents[2] = vect_hunt/
# parents[3] = sources/, parents[4] = vector-hunter/ (PROJECT_ROOT)
PROJECT_ROOT = Path(__file__).resolve().parents[4]
ASSETS_ROOT = PROJECT_ROOT / "sources" / "vect_hunt" / "assets"

IMAGES_DIR = ASSETS_ROOT / "images"
SOUNDS_DIR = ASSETS_ROOT / "sounds"
DATA_DIR = ASSETS_ROOT / "data"
FONTS_DIR = ASSETS_ROOT / "font"  # Note: le dossier s'appelle "font" pas "fonts"


class Paths:
    """Classe wrapper pour accès aux chemins."""

    PROJECT_ROOT = PROJECT_ROOT
    ASSETS_ROOT = ASSETS_ROOT
    IMAGES_DIR = IMAGES_DIR
    SOUNDS_DIR = SOUNDS_DIR
    DATA_DIR = DATA_DIR
    FONTS_DIR = FONTS_DIR
