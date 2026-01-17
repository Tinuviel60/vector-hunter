import json
from pathlib import Path
from typing import Any
from vect_hunt.engine.resources.paths import DATA_DIR

"""
Chargement des données non graphiques avec système de cache.
"""


class DataLoader:
    """
    Gestionnaire de chargement des fichiers JSON avec mise en cache.

    Les fichiers sont chargés depuis assets/data/ et mis en cache
    pour éviter des lectures multiples.

    Attributes
    ----------
    None
    """

    _cache: dict[Path, dict[str, Any]] = {}

    @classmethod
    def load_json(cls, relative_path: str, use_cache: bool = True) -> dict[str, Any]:
        """
        Charge un fichier JSON depuis le dossier data.

        Parameters
        ----------
        relative_path : str
            Chemin relatif depuis assets/data/
            Exemple : "configs/app.json", "templates/player.json"
        use_cache : bool, optional
            Si True, utilise le cache. Si False, force le rechargement.

        Returns
        -------
        dict[str, Any]
            Données JSON chargées
        """
        path = DATA_DIR / relative_path

        if use_cache and path in cls._cache:
            return cls._cache[path]

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if use_cache:
            cls._cache[path] = data

        return data

    @classmethod
    def reload(cls, relative_path: str) -> dict[str, Any]:
        """
        Force le rechargement d'un fichier JSON.

        Utile pour le hot-reload pendant le développement.

        Parameters
        ----------
        relative_path : str
            Chemin relatif depuis assets/data/

        Returns
        -------
        dict[str, Any]
            Données JSON rechargées
        """
        return cls.load_json(relative_path, use_cache=False)

    @classmethod
    def clear_cache(cls) -> None:
        """
        Vide complètement le cache.
        """
        cls._cache.clear()
