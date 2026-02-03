from collections import OrderedDict
from pathlib import Path
from typing import Any

"""
Utilitaires de securite communs aux loaders de ressources.
"""


class BaseLoader:
    """
    Classe de base pour securiser la resolution des chemins de ressources.
    """

    # Cache par defaut; les subclasses doivent le surcharger.
    _cache: "OrderedDict[object, object]" = OrderedDict()

    _MISSING = object()

    @classmethod
    def _cache_get(cls, key) -> Any:
        """
        Recupere une entree du cache en mode LRU.
        """
        cache = cls._cache
        if key in cache:
            cache.move_to_end(key)
            return cache[key]
        return cls._MISSING

    @classmethod
    def _cache_put(cls, key, value, max_items: int | None) -> None:
        """
        Ajoute une entree au cache en mode LRU avec limite d'elements.
        """
        cache = cls._cache
        cache[key] = value
        cache.move_to_end(key)
        if max_items is not None and len(cache) > max_items:
            cache.popitem(last=False)

    @classmethod
    def _raise_if_too_large(cls, path: Path, max_bytes: int) -> None:
        """
        Leve une erreur si le fichier depasse la limite.

        Parameters
        ----------
        path : Path
            Chemin du fichier a verifier
        max_bytes : int
            Taille maximale autorisee en bytes
        """
        size = path.stat().st_size
        if size > max_bytes:
            raise ValueError(
                f"Ressource trop volumineuse: {size} bytes (max {max_bytes})"
            )

    @classmethod
    def _resolve_path(
        cls,
        root_dir: Path,
        relative_path: str,
        allowed_extensions: set[str] | None = None,
        max_bytes: int = 1 * 1024 * 1024,
        must_be_file: bool = True,
    ) -> Path:
        """
        Resolve et valide un chemin relatif dans un dossier racine.

        Refuse:
        - chemins absolus
        - segments "." ou ".."
        - fichiers hors de la racine
        - symlinks dans le chemin
        - extensions non autorisees
        - taille de fichier au-dela de la limite

        Parameters
        ----------
        root_dir : Path
            Dossier racine des ressources
        relative_path : str
            Chemin relatif depuis la racine
        allowed_extensions : set[str] | None, optional
            Extensions autorisees (avec le point), par exemple {".png", ".jpg"}
            Si None, toutes les extensions sont autorisees.
        max_bytes : int, optional
            Taille maximale du fichier en bytes. Par defaut 1 Mo.

        Returns
        -------
        Path
            Chemin absolu valide du fichier ressource
        """
        rel = Path(relative_path)

        if not relative_path:
            raise ValueError("Chemin de ressource vide.")

        if rel.is_absolute() or str(relative_path).startswith("~"):
            raise ValueError(f"Chemin absolu interdit: {relative_path}")

        if any(part in (".", "..") for part in rel.parts):
            raise ValueError(f"Segments '.' ou '..' interdits: {relative_path}")

        root = root_dir.resolve()
        candidate = (root / rel).resolve()

        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Chemin hors de la racine: {relative_path}") from exc

        if allowed_extensions is not None:
            if candidate.suffix.lower() not in allowed_extensions:
                raise ValueError(
                    f"Extension non autorisee: {candidate.suffix} ({relative_path})"
                )

        if not candidate.exists():
            raise FileNotFoundError(f"Ressource introuvable: {candidate}")

        if must_be_file and not candidate.is_file():
            raise FileNotFoundError(f"Ressource invalide (pas un fichier): {candidate}")

        if max_bytes is not None and must_be_file:
            cls._raise_if_too_large(candidate, max_bytes)

        current = root
        for part in rel.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f"Symlink interdit dans le chemin: {relative_path}")

        return candidate
