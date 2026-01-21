import pytest

from vect_hunt.engine.core.math import Vector2D
from vect_hunt.engine.objects import GameObject
from vect_hunt.engine.scenes.scene_factory import SceneFactory


@pytest.fixture
def scene_factory(monkeypatch):
    factory = SceneFactory()

    def fake_from_template(
        template_path, position=None, rotation=None, input_system=None
    ):
        obj = GameObject("Template")
        if position is not None:
            obj.transform.position = position
        return obj

    factory._game_object_factory.from_template = fake_from_template
    return factory


def test_parse_position_defaults():
    assert SceneFactory._parse_position(None) == Vector2D(0, 0)


def test_parse_position_valid():
    assert SceneFactory._parse_position([3, 4]) == Vector2D(3, 4)


def test_from_template_builds_scene(monkeypatch, scene_factory):
    def fake_load_json(_):
        return {
            "scene": {"units": {"pixels_per_meter": 100.0, "gravity_m_s2": 9.81}},
            "game_objects": [
                {
                    "template_path": "player.json",
                    "name": "Player",
                    "transform": {"position": [1, 2], "rotation": 0.0},
                }
            ],
        }

    monkeypatch.setattr(
        "vect_hunt.engine.resources.loaders.data_loader.DataLoader.load_json",
        fake_load_json,
    )

    scene = scene_factory.from_template("level_00.json")

    assert scene.units["pixels_per_meter"] == 100.0
    assert len(scene.game_objects) == 1
    obj = next(iter(scene.game_objects.values()))
    assert obj.name == "Player"
    assert obj.transform.position == Vector2D(1, 2)


def test_add_game_objects_invalid_list(monkeypatch, scene_factory):
    def fake_load_json(_):
        return {"scene": {"units": {}}, "game_objects": "not-a-list"}

    monkeypatch.setattr(
        "vect_hunt.engine.resources.loaders.data_loader.DataLoader.load_json",
        fake_load_json,
    )

    with pytest.raises(ValueError):
        scene_factory.from_template("level_00.json")
