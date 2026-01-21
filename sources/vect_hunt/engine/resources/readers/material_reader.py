from vect_hunt.engine.resources.paths import MATERIALS_ROOT
from vect_hunt.engine.resources.readers.base_reader import BaseReader


class MaterialReader(BaseReader):
    """
    Accès aux materials de GameObjects.

    Encapsule la convention de chemin assets/data/materials/.
    """
    _relative_root = MATERIALS_ROOT
    _entry_label = "material"
