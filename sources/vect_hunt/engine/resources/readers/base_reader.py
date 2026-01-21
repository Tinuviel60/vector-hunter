from typing import Any
from vect_hunt.engine.resources.loaders.data_loader import DataLoader

"""
Classe de base pour les readers de JSON sous assets/data/.
"""


class BaseReader:
    """
    Classe de base pour les readers de donnees JSON.

    Les chemins sont relatifs a assets/data/.
    """

    _relative_root: str = ""
    _entry_label: str = "resource"

    def __init__(self) -> None:
        """
        Initialise le reader et charge toutes les ressources.

        Attributes
        ----------
        configs : dict[str, dict[str, Any]]
            Dictionnaire mappant les chemins relatifs aux donnees JSON.
        """
        self.configs = self.read_all()

    def load(self, relative_path: str) -> dict[str, Any]:
        """
        Charge une ressource JSON par chemin relatif.

        Parameters
        ----------
        relative_path : str
            Chemin relatif sous assets/data/.

        Returns
        -------
        dict[str, Any]
            Donnees JSON.
        """
        if self._relative_root:
            path = f"{self._relative_root}/{relative_path}"
        else:
            path = relative_path
        return DataLoader.load_json(path)

    def read_all(self) -> dict[str, dict[str, Any]]:
        """
        Charge toutes les ressources du repertoire.

        Returns
        -------
        dict[str, dict[str, Any]]
            Dictionnaire mappant les chemins relatifs aux donnees JSON.
        """
        configs: dict[str, dict[str, Any]] = {}

        files_paths = DataLoader.get_file_path_in_dir(self._relative_root)
        for name in files_paths:
            relative_name = name
            if self._relative_root:
                prefix = f"{self._relative_root}/"
                if name.startswith(prefix):
                    relative_name = name[len(prefix) :]

            data = self.load(relative_name)

            if relative_name in configs:
                raise ValueError(
                    f"Duplicate {self._entry_label} name detected: {relative_name}"
                )

            configs[relative_name] = data

        return configs

    def reload(self, relative_path: str) -> dict[str, Any]:
        """
        Force le rechargement d'une ressource JSON.

        Parameters
        ----------
        relative_path : str
            Chemin relatif sous assets/data/.

        Returns
        -------
        dict[str, Any]
            Donnees JSON.
        """
        if self._relative_root:
            path = f"{self._relative_root}/{relative_path}"
        else:
            path = relative_path
        return DataLoader.reload(path)
