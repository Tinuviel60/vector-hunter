from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ResourceRegistry:
    """
    Registre typé des ressources chargées au démarrage.

    Attributes
    ----------
    configs : dict[str, dict[str, Any]]
        Configurations (ex: "inputs.json", "renderer.json"...).
    templates : dict[str, dict[str, Any]]
        Templates de GameObjects.
    scenes : dict[str, dict[str, Any]]
        Fichiers de niveaux/scènes.
    materials : dict[str, dict[str, Any]]
        Matériaux physiques.
    """
    configs: dict[str, dict[str, Any]]
    templates: dict[str, dict[str, Any]]
    scenes: dict[str, dict[str, Any]]
    materials: dict[str, dict[str, Any]]