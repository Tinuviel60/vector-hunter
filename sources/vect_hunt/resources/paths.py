from pathlib import Path

"""
Gestion centralisée des chemins de ressources.
"""

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSETS_ROOT = PROJECT_ROOT / "sources" / "vect_hunt" / "assets"

IMAGES_DIR = ASSETS_ROOT / "images"
SOUNDS_DIR = ASSETS_ROOT / "sounds"
DATA_DIR = ASSETS_ROOT / "data"
FONTS_DIR = ASSETS_ROOT / "fonts"
