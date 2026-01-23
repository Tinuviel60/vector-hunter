from vect_hunt.engine.resources.paths import TEMPLATE_ROOT
from vect_hunt.engine.resources.readers.base_reader import BaseReader


class TemplateReader(BaseReader):
    """
    Accès aux templates de GameObjects.

    Encapsule la convention de chemin assets/data/templates/.
    """

    _relative_root = TEMPLATE_ROOT
    _entry_label = "template"
