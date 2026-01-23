import pytest
from vect_hunt.engine.components.collider import ColliderComponent
from vect_hunt.engine.core import Tag, Transform, Vector2D
from vect_hunt.engine.core.geometries import BoxShape
from vect_hunt.engine.objects import GameObject


class DummyColliderComponent(ColliderComponent):
    """
    Collider minimal pour les tests unitaires.

    Aucune logique de collision n'est utilisée ici.
    """

    component_name = "dummy_collider"

    def __init__(self):
        super().__init__(shape=BoxShape(1.0, 1.0))

    @classmethod
    def from_data(cls, data, context):
        return cls()


def test_game_object_initialization_defaults():
    obj = GameObject(name="Player")

    assert obj.name == "Player"
    assert isinstance(obj.transform, Transform)
    assert obj.transform.position == Vector2D(0.0, 0.0)
    assert obj.get_component(ColliderComponent) is None
    assert obj.active is True
    assert obj.tags == Tag.NONE


@pytest.mark.parametrize(
    "name, position, rotation, tags",
    [
        ("Player", Vector2D(0.0, 0.0), 0.0, Tag.NONE),
        ("Enemy", Vector2D(5.0, -3.0), 1.2, Tag.ENEMY),
        ("OBJECT", Vector2D(-10.0, 4.5), -0.5, Tag.PLAYER | Tag.PROJECTILE),
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
    obj = GameObject("OBJECT")
    for _ in range(nb_colliders):
        collider = DummyColliderComponent()
        obj.add_component(collider)
        assert collider in obj.components

    assert len(obj.get_components(DummyColliderComponent)) == nb_colliders


@pytest.mark.parametrize(
    "nb_initial_colliders, nb_colliders_to_remove", [(1, 1), (5, 2), (3, 0)]
)
def test_remove_existing_collider(nb_initial_colliders, nb_colliders_to_remove):
    obj = GameObject("OBJECT")
    colliders = [DummyColliderComponent() for _ in range(nb_initial_colliders)]

    for collider in colliders:
        obj.add_component(collider)

    for i in range(nb_colliders_to_remove):
        obj.remove_component(colliders[i])

    remaining = obj.get_components(DummyColliderComponent)
    assert len(remaining) == nb_initial_colliders - nb_colliders_to_remove
    for i in range(nb_colliders_to_remove):
        assert colliders[i] not in remaining
    for i in range(nb_colliders_to_remove, nb_initial_colliders):
        assert colliders[i] in remaining


def test_remove_non_existing_collider():
    obj = GameObject("OBJECT")
    collider = DummyColliderComponent()

    obj.remove_component(collider)

    assert obj.get_components(DummyColliderComponent) == []


@pytest.mark.parametrize(
    "initial_tags, tag_to_check, expected_result",
    [
        (Tag.PLAYER | Tag.OBJECT, Tag.PLAYER, Tag.PLAYER | Tag.OBJECT),
        (Tag.ENEMY, Tag.OBJECT, Tag.ENEMY | Tag.OBJECT),
        (Tag.ENEMY, Tag.PLAYER, Tag.ENEMY | Tag.PLAYER),
        (
            Tag.PROJECTILE | Tag.OBJECT,
            Tag.ENEMY,
            Tag.PROJECTILE | Tag.OBJECT | Tag.ENEMY,
        ),
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
        (Tag.NONE, [Tag.PLAYER, Tag.OBJECT], Tag.PLAYER | Tag.OBJECT),
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
        (Tag.PLAYER | Tag.OBJECT, Tag.PLAYER, Tag.OBJECT),
        (Tag.ENEMY | Tag.OBJECT, Tag.OBJECT, Tag.ENEMY),
        (Tag.ENEMY | Tag.PLAYER, Tag.PLAYER, Tag.ENEMY),
        (Tag.PROJECTILE | Tag.OBJECT, Tag.ENEMY, Tag.PROJECTILE | Tag.OBJECT),
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
