import pytest

from vect_hunt.worlds import World
from vect_hunt.objects import GameObject
from vect_hunt.systems import ColliderSystem


class DummyColliderSystem(ColliderSystem):
    """
    ColliderSystem minimal pour les tests.
    Permet de vérifier si un GameObject est enregistré/désenregistré.
    """

    def __init__(self):
        self.registered = set()

    def register(self, game_object: GameObject):
        self.registered.add(game_object.name)

    def unregister(self, game_object: GameObject):
        self.registered.discard(game_object.name)


@pytest.fixture
def empty_world():
    """
    Retourne un World vide avec un DummyColliderSystem pour tests.
    """
    w = World()
    w.collider_system = DummyColliderSystem()
    return w


@pytest.mark.parametrize(
    "object_name", ["Player", "Enemy", "Wall", "Target", "Item_123"]
)
def test_add_game_object_registers_in_world(empty_world, object_name):
    world = empty_world
    obj = GameObject(object_name)

    world.add_game_object(obj)

    # Vérifie que l'objet est ajouté au dictionnaire
    assert obj.name in world.game_objects
    assert world.game_objects[obj.name] is obj

    # Vérifie que ColliderSystem l'a enregistré
    assert obj.name in world.collider_system.registered


@pytest.mark.parametrize(
    "base_name, count, expected_names",
    [
        ("Wall", 3, ["Wall", "Wall_1", "Wall_2"]),
        ("Player", 2, ["Player", "Player_1"]),
        ("Enemy", 5, ["Enemy", "Enemy_1", "Enemy_2", "Enemy_3", "Enemy_4"]),
        ("Item", 1, ["Item"]),
    ],
)
def test_add_game_object_same_name(empty_world, base_name, count, expected_names):
    world = empty_world
    objects = [GameObject(base_name) for _ in range(count)]

    for obj in objects:
        world.add_game_object(obj)

    # Vérifie que les noms ont été ajustés pour éviter les conflits
    assert len(world.game_objects) == count

    for obj, expected_name in zip(objects, expected_names):
        assert obj.name == expected_name
        assert world.game_objects[expected_name] is obj
        assert expected_name in world.collider_system.registered


@pytest.mark.parametrize(
    "object_names",
    [
        (["Enemy"]),
        (["Player", "Enemy", "Wall"]),
        (["Item1", "Item2", "Item3", "Item4"]),
    ],
)
def test_remove_game_object_unregisters_from_world(empty_world, object_names):
    world = empty_world
    objects = [GameObject(name) for name in object_names]

    # Ajouter tous les objets
    for obj in objects:
        world.add_game_object(obj)

    # Retirer le premier objet
    world.remove_game_object(objects[0])

    # Vérifie que l'objet n'est plus dans le dictionnaire
    assert objects[0].name not in world.game_objects
    assert objects[0].name not in world.collider_system.registered

    # Vérifie que les autres sont toujours là
    for obj in objects[1:]:
        assert obj.name in world.game_objects
        assert obj.name in world.collider_system.registered


@pytest.mark.parametrize(
    "name", ["UniqueObject", "Player", "AnotherOne", "X", "VeryLongNameForAnObject"]
)
def test_validate_name_returns_same_if_unique(empty_world, name):
    world = empty_world
    validated = world.validate_name(name)
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
    empty_world, base_name, existing_count, expected_suffix
):
    world = empty_world

    # Ajouter des objets existants
    for _ in range(existing_count):
        obj = GameObject(base_name)
        world.add_game_object(obj)

    # Valider un nouveau nom qui devrait avoir un suffixe
    new_name = world.validate_name(base_name)
    assert new_name == f"{base_name}{expected_suffix}"
