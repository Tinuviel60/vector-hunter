from vect_hunt.engine.resources.paths import CONFIGS_ROOT
from vect_hunt.engine.resources.readers.base_reader import BaseReader


class ConfigReader(BaseReader):
    """
    Accès aux fichiers de configurations.

    Encapsule la convention de chemin assets/data/configs/.
    """

    _relative_root = CONFIGS_ROOT
    _entry_label = "config"
