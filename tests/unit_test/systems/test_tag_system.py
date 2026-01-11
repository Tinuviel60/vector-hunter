import pytest

from vect_hunt.core import Tag
from vect_hunt.systems import TagSystem
from vect_hunt.systems.tag_system import (
    CAN_COLLIDE,
    CAN_DESTROY,
    CAN_PICKUP,
)


@pytest.mark.parametrize(
    "tag1, tag2, expected",
    [
        # PLAYER
        (Tag.PLAYER, Tag.ENEMY, True),
        (Tag.PLAYER, Tag.WALL, False),
        (Tag.PLAYER, Tag.PROJECTILE, False),
        (Tag.PLAYER, Tag.PICKUP, False),
        # ENEMY
        (Tag.ENEMY, Tag.PLAYER, True),
        (Tag.ENEMY, Tag.WALL, True),
        (Tag.ENEMY, Tag.PROJECTILE, True),
        (Tag.ENEMY, Tag.PICKUP, False),
        # PROJECTILE
        (Tag.PROJECTILE, Tag.ENEMY, True),
        (Tag.PROJECTILE, Tag.WALL, True),
        (Tag.PROJECTILE, Tag.PLAYER, False),
        # WALL
        (Tag.WALL, Tag.PLAYER, True),
        (Tag.WALL, Tag.ENEMY, True),
        (Tag.WALL, Tag.PROJECTILE, True),
        (Tag.WALL, Tag.PICKUP, False),
    ],
)
def test_can_collide(tag1: Tag, tag2: Tag, expected: bool):
    """
    Vérifie les règles de collision métier.
    """
    assert TagSystem.can_collide(tag1, tag2) is expected


@pytest.mark.parametrize(
    "tag1, tag2",
    [
        (Tag.NONE, Tag.PLAYER),
        (Tag.NONE, Tag.ENEMY),
        (Tag.PLAYER, Tag.NONE),
        (Tag.NONE, Tag.NONE),
    ],
)
def test_can_collide_with_none(tag1: Tag, tag2: Tag):
    """
    Aucun tag ne doit interagir avec Tag.NONE.
    """
    assert TagSystem.can_collide(tag1, tag2) is False


@pytest.mark.parametrize(
    "tag1, tag2, expected",
    [
        (Tag.PROJECTILE, Tag.ENEMY, True),
        (Tag.PROJECTILE, Tag.WALL, True),
        (Tag.PROJECTILE, Tag.PLAYER, False),
        (Tag.ENEMY, Tag.PLAYER, True),
        (Tag.ENEMY, Tag.WALL, False),
    ],
)
def test_can_destroy(tag1: Tag, tag2: Tag, expected: bool):
    """
    Vérifie les règles de destruction métier.
    """
    assert TagSystem.can_destroy(tag1, tag2) is expected


@pytest.mark.parametrize(
    "tag1, tag2",
    [
        (Tag.PLAYER, Tag.ENEMY),
        (Tag.PLAYER, Tag.WALL),
        (Tag.WALL, Tag.PLAYER),
        (Tag.NONE, Tag.ENEMY),
    ],
)
def test_can_destroy_invalid_cases(tag1: Tag, tag2: Tag):
    """
    Les interactions non définies doivent retourner False.
    """
    assert TagSystem.can_destroy(tag1, tag2) is False


@pytest.mark.parametrize(
    "tag1, tag2, expected",
    [
        (Tag.PLAYER, Tag.PICKUP, True),
        (Tag.PLAYER, Tag.ENEMY, False),
        (Tag.ENEMY, Tag.PICKUP, False),
        (Tag.PROJECTILE, Tag.PICKUP, False),
    ],
)
def test_can_pickup(tag1: Tag, tag2: Tag, expected: bool):
    """
    Vérifie les règles de ramassage métier.
    """
    assert TagSystem.can_pickup(tag1, tag2) is expected


@pytest.mark.parametrize(
    "tag1, tag2",
    [
        (Tag.NONE, Tag.PICKUP),
        (Tag.PLAYER, Tag.NONE),
        (Tag.NONE, Tag.NONE),
    ],
)
def test_can_pickup_with_none(tag1: Tag, tag2: Tag):
    """
    Tag.NONE ne permet jamais une interaction.
    """
    assert TagSystem.can_pickup(tag1, tag2) is False


@pytest.mark.parametrize(
    "mask",
    [
        CAN_COLLIDE,
        CAN_DESTROY,
        CAN_PICKUP,
    ],
)
def test_check_mask_consistency(mask):
    """
    Vérifie que la logique générique _check_mask applique correctement les masques.
    """
    for source, allowed in mask.items():
        for target in Tag:
            result = TagSystem._check_mask(source, target, mask)
            assert result is bool(allowed & target)
