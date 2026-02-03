from vect_hunt.engine.resources.paths import SCENES_ROOT
from vect_hunt.engine.resources.readers.base_reader import BaseReader


class SceneReader(BaseReader):
    """
    Accès aux niveaux (scènes).

    Encapsule la convention de chemin assets/data/scenes/.
    """

    _relative_root = SCENES_ROOT
    _entry_label = "scene"
