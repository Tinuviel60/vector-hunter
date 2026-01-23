import importlib
import importlib.util
import logging
import os
import sys
from types import ModuleType

logger = logging.getLogger(__name__)


def _import_module_from_path(module_name: str, file_path: str) -> ModuleType:
    """Importe dynamiquement un module Python à partir de son chemin absolu.

    Parameters
    ----------
    module_name : str
        Nom du module à importer.
    file_path : str
        Chemin absolu vers le fichier .py du module.

    Returns
    -------
    ModuleType
        Le module importé.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"Cannot import module {module_name} from {file_path}")


def _find_py_files_recursively(root_dir: str) -> list[tuple[str, str]]:
    """
    Retourne une liste de tuples (module_name, file_path)
    pour tous les .py dans root_dir.

    Parameters
    ----------
    root_dir : str
        Dossier racine à scanner.

    Returns
    -------
    list[tuple[str, str]]
        Liste des tuples (module_name, file_path) pour tous les modules Python trouvés.
    """
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                file_path = os.path.join(dirpath, filename)
                # module_name: chemin relatif en notation package
                # (ex: vect_hunt.game.montruc.monmodule)
                rel_path = os.path.relpath(
                    file_path, os.path.dirname(os.path.dirname(__file__))
                )
                module_name = rel_path[:-3].replace(os.sep, ".")
                py_files.append((module_name, file_path))
    return py_files


def load_all_components(directories: list[str]) -> None:
    """
    Importe dynamiquement tous les modules Python dans les dossiers fournis (récursif).
    Cela permet d'enregistrer automatiquement tous les Component sans import explicite.

    Parameters
    ----------
    directories : list[str]
        Liste des dossiers à scanner
        (ex: ['sources/vect_hunt/engine/components', 'sources/vect_hunt/game'])
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # sources/vect_hunt
    for directory in directories:
        abs_dir = (
            directory if os.path.isabs(directory) else os.path.join(base_dir, directory)
        )
        if not os.path.isdir(abs_dir):
            continue
        for module_name, file_path in _find_py_files_recursively(abs_dir):
            try:
                _import_module_from_path(module_name, file_path)
            except Exception as e:
                logger.warning(
                    f"Erreur lors de l'import du module {module_name} "
                    f"depuis {file_path}: {e}"
                )
                pass
