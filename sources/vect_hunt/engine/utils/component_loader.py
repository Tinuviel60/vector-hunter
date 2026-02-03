import importlib
import logging
import os
import sys

logger = logging.getLogger(__name__)


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
                rel_path = os.path.relpath(file_path, _package_root())
                module_name = f"vect_hunt.{rel_path[:-3].replace(os.sep, '.')}"
                py_files.append((module_name, file_path))
    return py_files


def _package_root() -> str:
    """
    Retourne le chemin absolu du package racine (sources/vect_hunt).
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _ensure_package_on_sys_path() -> None:
    """
    S'assure que le parent de sources/vect_hunt est dans sys.path.
    """
    package_parent = os.path.dirname(_package_root())
    if package_parent not in sys.path:
        sys.path.insert(0, package_parent)


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
    _ensure_package_on_sys_path()
    base_dir = _package_root()
    for directory in directories:
        abs_dir = (
            directory if os.path.isabs(directory) else os.path.join(base_dir, directory)
        )
        if not os.path.isdir(abs_dir):
            continue
        for module_name, file_path in _find_py_files_recursively(abs_dir):
            try:
                importlib.import_module(module_name)
            except Exception as e:
                logger.warning(
                    f"Erreur lors de l'import du module {module_name} "
                    f"depuis {file_path}: {e}"
                )
                pass
