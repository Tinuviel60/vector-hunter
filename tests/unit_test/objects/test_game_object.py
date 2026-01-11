import pytest
import math

from vect_hunt.objects import GameObject
from vect_hunt.core import Collider, Tag, Transform, Vector2D


class DummyCollider(Collider):
    """
    Collider minimal pour les tests unitaires.

    Aucune logique de collision n'est utilisée ici.
    """

    def __init__(self):
        pass


def test_game_object_initialization_defaults():
    obj = GameObject(name="Player")

    assert obj.name == "Player"
    assert isinstance(obj.transform, Transform)
    assert obj.transform.position == Vector2D(0.0, 0.0)
    assert obj.colliders == []
    assert obj.active is True
    assert obj.tags == Tag.NONE


@pytest.mark.parametrize(
    "name, position, rotation, tags",
    [
        ("Player", Vector2D(0.0, 0.0), 0.0, Tag.NONE),
        ("Enemy", Vector2D(5.0, -3.0), 1.2, Tag.ENEMY),
        ("Wall", Vector2D(-10.0, 4.5), -0.5, Tag.PLAYER | Tag.PROJECTILE),
    ],
)
def test_game_object_initialization(name, position, rotation, tags):
    transform = Transform(position=position, rotation=rotation)
    obj = GameObject(name=name, transform=transform, tags=tags)

    assert obj.transform is transform
    assert obj.tags == tags
    assert obj.active is True


@pytest.mark.parametrize("nb_colliders", [0, 1, 10])
def test_add_collider(nb_colliders):
    obj = GameObject("Wall")

    for _ in range(nb_colliders):
        collider = DummyCollider()
        obj.add_collider(collider)
        assert collider in obj.colliders

    assert len(obj.colliders) == nb_colliders


@pytest.mark.parametrize(
    "nb_initial_colliders, nb_colliders_to_remove", [(1, 1), (5, 2), (3, 0)]
)
def test_remove_existing_collider(nb_initial_colliders, nb_colliders_to_remove):
    obj = GameObject("Wall")
    colliders = [DummyCollider() for _ in range(nb_initial_colliders)]

    for collider in colliders:
        obj.add_collider(collider)

    for i in range(nb_colliders_to_remove):
        obj.remove_collider(colliders[i])

    assert len(obj.colliders) == nb_initial_colliders - nb_colliders_to_remove
    for i in range(nb_colliders_to_remove):
        assert colliders[i] not in obj.colliders
    for i in range(nb_colliders_to_remove, nb_initial_colliders):
        assert colliders[i] in obj.colliders


def test_remove_non_existing_collider():
    obj = GameObject("Wall")
    collider = DummyCollider()

    obj.remove_collider(collider)

    assert obj.colliders == []


@pytest.mark.parametrize(
    "dx, dy, expected_x, expected_y",
    [
        (5.0, 3.0, 5.0, 3.0),
        (-2.0, 4.0, -2.0, 4.0),
        (0.0, 0.0, 0.0, 0.0),
    ],
)
def test_move_updates_position(dx, dy, expected_x, expected_y):
    obj = GameObject("Player")

    obj.move(dx, dy)

    assert obj.transform.position == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "list_of_moves, expected_x, expected_y",
    [
        ([(1.0, 1.0), (-2.0, 3.0)], -1.0, 4.0),
        ([(0.0, 0.0), (0.0, 0.0)], 0.0, 0.0),
        ([(-1.0, -1.0), (1.0, 1.0), (2.0, 2.0)], 2.0, 2.0),
        ([(3.5, -2.5), (-1.5, 4.5), (0.0, -2.0)], 2.0, 0.0),
    ],
)
def test_move_multiple_times(list_of_moves, expected_x, expected_y):
    obj = GameObject("Player")

    for dx, dy in list_of_moves:
        obj.move(dx, dy)

    assert obj.transform.position == Vector2D(expected_x, expected_y)


@pytest.mark.parametrize(
    "x, y",
    [
        (10.0, -5.0),
        (0.0, 0.0),
        (-3.5, 2.5),
    ],
)
def test_set_position_from_origin(x, y):
    obj = GameObject("Player")

    obj.set_position(x, y)
    assert obj.transform.position == Vector2D(x, y)


@pytest.mark.parametrize(
    "x, y",
    [
        (-1.0, 4.0),
        (2.5, -3.5),
        (0.0, 0.0),
    ],
)
def test_set_position_from_non_zero(x, y):
    obj = GameObject("Player")
    obj.move(2.0, 3.0)

    obj.set_position(x, y)

    assert obj.transform.position == Vector2D(x, y)


@pytest.mark.parametrize("delta", [0.0, 1.57, -3.14, 6.28, -1.057, 3.5, -4.75])
def test_rotate_updates_rotation(delta):
    obj = GameObject("Spinner")

    obj.rotate(delta)
    # L'angle attendu est celui que to_angle() retourne après avoir
    # créé une Rotation avec delta
    assert obj.transform.rotation.to_angle() == pytest.approx(
        math.atan2(math.sin(delta), math.cos(delta))
    )


@pytest.mark.parametrize(
    "initial_rotation, list_of_delta",
    [
        (0.0, (1.0, -0.25)),
        (3.0, (0.5, 0.5, -1.0)),
        (-2.0, (2.0, 2.0, -4.0)),
        (-2.0, (1.0, 1.0, 1.0, -3.0)),
    ],
)
def test_rotate_multiple_times(initial_rotation, list_of_delta):
    from vect_hunt.core import Rotation

    obj = GameObject("Spinner", transform=Transform(rotation=initial_rotation))

    for delta in list_of_delta:
        obj.rotate(delta)

    # Calculer l'angle attendu en utilisant la même méthode que le code
    total_rotation = initial_rotation + sum(list_of_delta)
    expected_rotation = Rotation(total_rotation).to_angle()

    assert obj.transform.rotation.to_angle() == pytest.approx(expected_rotation)


@pytest.mark.parametrize(
    "initial_tags, tag_to_check, expected_result",
    [
        (Tag.PLAYER | Tag.WALL, Tag.PLAYER, Tag.PLAYER | Tag.WALL),
        (Tag.ENEMY, Tag.WALL, Tag.ENEMY | Tag.WALL),
        (Tag.ENEMY, Tag.PLAYER, Tag.ENEMY | Tag.PLAYER),
        (Tag.PROJECTILE | Tag.WALL, Tag.ENEMY, Tag.PROJECTILE | Tag.WALL | Tag.ENEMY),
        (Tag.NONE, Tag.ENEMY, Tag.ENEMY),
    ],
)
def test_add_tag(initial_tags, tag_to_check, expected_result):
    obj = GameObject("Player", tags=initial_tags)

    obj.add_tag(tag_to_check)

    assert obj.has_tag(tag_to_check) is True
    assert obj.tags == expected_result


@pytest.mark.parametrize(
    "initial_tags, tags_to_add, expected_tags",
    [
        (Tag.NONE, [Tag.PLAYER, Tag.WALL], Tag.PLAYER | Tag.WALL),
        (
            Tag.ENEMY,
            [Tag.PROJECTILE, Tag.PICKUP],
            Tag.ENEMY | Tag.PROJECTILE | Tag.PICKUP,
        ),
        (Tag.PLAYER, [Tag.PLAYER, Tag.PICKUP], Tag.PLAYER | Tag.PICKUP),
    ],
)
def test_add_multiple_tags(initial_tags, tags_to_add, expected_tags):
    obj = GameObject("Player", tags=initial_tags)

    for tag in tags_to_add:
        obj.add_tag(tag)

    assert obj.tags == expected_tags


@pytest.mark.parametrize(
    "initial_tags, tag_to_remove, expected_result",
    [
        (Tag.PLAYER | Tag.WALL, Tag.PLAYER, Tag.WALL),
        (Tag.ENEMY | Tag.WALL, Tag.WALL, Tag.ENEMY),
        (Tag.ENEMY | Tag.PLAYER, Tag.PLAYER, Tag.ENEMY),
        (Tag.PROJECTILE | Tag.WALL, Tag.ENEMY, Tag.PROJECTILE | Tag.WALL),
        (Tag.NONE, Tag.ENEMY, Tag.NONE),
    ],
)
def test_remove_tag(initial_tags, tag_to_remove, expected_result):
    obj = GameObject("Player", tags=initial_tags)

    obj.remove_tag(tag_to_remove)

    assert obj.tags == expected_result


def test_remove_non_existing_tag():
    obj = GameObject("Player", tags=Tag.PLAYER)

    obj.remove_tag(Tag.ENEMY)

    assert obj.tags == Tag.PLAYER


def test_has_tag_false_when_none():
    obj = GameObject("Ghost")

    assert obj.has_tag(Tag.PLAYER) is False


def test_list_tags_empty():
    obj = GameObject("Ghost")

    assert obj.list_tags() == []
