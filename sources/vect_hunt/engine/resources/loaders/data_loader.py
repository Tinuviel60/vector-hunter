import json
from collections import OrderedDict
from pathlib import Path
from typing import Any
from vect_hunt.engine.resources.loaders.base_loader import BaseLoader
from vect_hunt.engine.resources.paths import DATA_DIR

"""
Chargement des données non graphiques avec système de cache.
"""


class DataLoader(BaseLoader):
    """
    Gestionnaire de chargement des fichiers JSON avec mise en cache.

    Les fichiers sont chargés depuis assets/data/ et mis en cache
    pour éviter des lectures multiples.

    Attributes
    ----------
    None
    """

    _cache: "OrderedDict[Path, dict[str, Any]]" = OrderedDict()
    # Taille maximale d'un fichier JSON (1 Mo)
    _max_bytes = 1 * 1024 * 1024
    # Nombre maximal d'entrees en cache
    _max_items = 256

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

        path = cls._resolve_path(
            DATA_DIR,
            relative_path,
            allowed_extensions={".json"},
            max_bytes=cls._max_bytes,
        )

        if use_cache:
            cached = cls._cache_get(path)
            if cached is not cls._MISSING:
                return cached

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if use_cache:
            cls._cache_put(path, data, cls._max_items)

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
