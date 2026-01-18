"""
Factory pour creer des scenes depuis des fichiers JSON.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, TYPE_CHECKING

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.objects import GameObjectFactory
from vect_hunt.engine.resources.loaders.data_loader import DataLoader
from .scene import Scene

if TYPE_CHECKING:
    from vect_hunt.engine.input import InputSystem

logger = logging.getLogger(__name__)


class SceneFactory:
    """
    Factory responsable de la creation de scenes a partir de JSON.

    Format attendu :
    {
        "scene": {
            "units": {"pixels_per_meter": 100.0, "gravity_m_s2": 9.81}
        },
        "game_objects": [
            {
                "template_path": "player.json",
                "name": "Player",
                "transform": {"position": [0, 0], "rotation": 0.0}
            }
        ]
    }
    """

    def __init__(self) -> None:
        """
        Initialise la SceneFactory avec une GameObjectFactory interne.
        """
        self._game_object_factory = GameObjectFactory()

    def from_template(
        self,
        template_path: str,
        input_system: Optional["InputSystem"] = None,
    ) -> Scene:
        """
        Charge une scene depuis un fichier JSON (assets/data/levels).

        Parameters
        ----------
        template_path : str
            Chemin relatif dans assets/data/levels.
        input_system : InputSystem | None
            Systeme d'input a injecter dans les GameObjects, si necessaire.
        """
        data = DataLoader.load_json(f"levels/{template_path}")

        scene = Scene.from_data(data.get("scene"))
        self._add_game_objects(scene, data, input_system)

        return scene

    def _add_game_objects(
        self,
        scene: Scene,
        data: dict[str, Any],
        input_system: Optional["InputSystem"],
    ) -> None:
        """
        Ajoute les GameObjects à la scène depuis les données JSON.

        Parameters
        ----------
        scene : Scene
            Scène à laquelle ajouter les GameObjects.
        data : dict[str, Any]
            Données JSON contenant les game_objects.
        input_system : InputSystem | None
            Systeme d'input a injecter dans les GameObjects, si necessaire.
        """
        objects_data = data.get("game_objects", [])
        if not isinstance(objects_data, list):
            raise ValueError("Le champ 'game_objects' doit etre une liste.")

        for entry in objects_data:
            template_path = entry.get("template_path")
            if not template_path:
                raise ValueError("Un game_object doit definir 'template_path'.")

            transform = entry.get("transform", {})
            position = self._parse_position(transform.get("position"))
            rotation = transform.get("rotation")

            game_object = self._game_object_factory.from_template(
                template_path,
                position=position,
                rotation=rotation,
                input_system=input_system,
            )

            name = entry.get("name")
            if name:
                game_object.name = name

            scene.add_game_object(game_object)

    @staticmethod
    def _parse_position(pos_data: Any) -> Vector2D:
        """
        Parse une position depuis les données JSON.

        Parameters
        ----------
        pos_data : Any
            Données de position (liste ou None).

        Returns
        -------
        Vector2D
            Position parsée.
        """
        if pos_data is None:
            return Vector2D(0, 0)
        return Vector2D(pos_data[0], pos_data[1])
