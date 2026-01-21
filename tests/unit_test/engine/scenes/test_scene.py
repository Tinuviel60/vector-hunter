import pytest

from vect_hunt.engine.scenes import Scene
from vect_hunt.engine.objects import GameObject


@pytest.fixture
def empty_scene():
    """
    Retourne une Scene vide pour tests.
    """
    return Scene(units={"pixels_per_meter": 100.0, "gravity_m_s2": 9.81})


@pytest.mark.parametrize(
    "object_name", ["Player", "Enemy", "Wall", "Target", "Item_123"]
)
def test_add_game_object_registers_in_scene(empty_scene, object_name):
    scene = empty_scene
    obj = GameObject(object_name)

    scene.add_game_object(obj)

    # Vérifie que l'objet est ajouté au dictionnaire (par ID)
    assert obj.id in scene.game_objects
    assert scene.game_objects[obj.id] is obj


@pytest.mark.parametrize(
    "base_name, count, expected_names",
    [
        ("Wall", 3, ["Wall", "Wall_1", "Wall_2"]),
        ("Player", 2, ["Player", "Player_1"]),
        ("Enemy", 5, ["Enemy", "Enemy_1", "Enemy_2", "Enemy_3", "Enemy_4"]),
        ("Item", 1, ["Item"]),
    ],
)
def test_add_game_object_same_name(empty_scene, base_name, count, expected_names):
    scene = empty_scene
    objects = [GameObject(base_name) for _ in range(count)]

    for obj in objects:
        scene.add_game_object(obj)

    # Vérifie que les noms ont été ajustés pour éviter les conflits
    assert len(scene.game_objects) == count

    for obj, expected_name in zip(objects, expected_names):
        assert obj.name == expected_name
        assert scene.game_objects[obj.id] is obj


@pytest.mark.parametrize(
    "object_names",
    [
        (["Enemy"]),
        (["Player", "Enemy", "Wall"]),
        (["Item1", "Item2", "Item3", "Item4"]),
    ],
)
def test_remove_game_object_unregisters_from_scene(empty_scene, object_names):
    scene = empty_scene
    objects = [GameObject(name) for name in object_names]

    # Ajouter tous les objets
    for obj in objects:
        scene.add_game_object(obj)

    # Retirer le premier objet
    scene.remove_game_object(objects[0])

    # Vérifie que l'objet n'est plus dans le dictionnaire
    assert objects[0].id not in scene.game_objects

    # Vérifie que les autres sont toujours là
    for obj in objects[1:]:
        assert obj.id in scene.game_objects


@pytest.mark.parametrize(
    "name", ["UniqueObject", "Player", "AnotherOne", "X", "VeryLongNameForAnObject"]
)
def test_validate_name_returns_same_if_unique(empty_scene, name):
    scene = empty_scene
    validated = scene.validate_name(name)
    assert validated == name


@pytest.mark.parametrize(
    "base_name, existing_count, expected_suffix",
    [
        ("Target", 1, "_1"),
        ("Target", 2, "_2"),
        ("Player", 1, "_1"),
        ("Enemy", 5, "_5"),
    ],
)
def test_validate_name_appends_suffix_if_conflict(
    empty_scene, base_name, existing_count, expected_suffix
):
    scene = empty_scene

    # Ajouter des objets existants
    for i in range(existing_count):
        obj = GameObject(base_name)
        scene.add_game_object(obj)

    # Valider un nouveau nom qui devrait avoir un suffixe
    new_name = scene.validate_name(base_name)
    assert new_name == f"{base_name}{expected_suffix}"


def test_game_object_gets_unique_id(empty_scene):
    """Vérifie que chaque GameObject reçoit un ID unique."""
    scene = empty_scene
    objects = [GameObject(f"Obj{i}") for i in range(5)]

    for obj in objects:
        scene.add_game_object(obj)

    # Vérifier que tous les IDs sont uniques
    ids = [obj.id for obj in objects]
    assert len(ids) == len(set(ids))

    # Vérifier que tous sont dans le dictionnaire
    for obj in objects:
        assert scene.game_objects[obj.id] is obj


def test_scene_has_collision_tracker(empty_scene):
    """Vérifie que Scene n'expose pas de CollisionTracker par défaut."""
    scene = empty_scene
    assert not hasattr(scene, "collision_tracker")
