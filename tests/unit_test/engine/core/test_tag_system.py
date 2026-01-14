import pytest

from vect_hunt.engine.core import Tag
from vect_hunt.engine.core import TagSystem
from vect_hunt.engine.core import (
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
    "method, tag1, tag2",
    [
        # Tag.NONE ne collide jamais
        ("can_collide", Tag.NONE, Tag.PLAYER),
        ("can_collide", Tag.NONE, Tag.ENEMY),
        ("can_collide", Tag.PLAYER, Tag.NONE),
        ("can_collide", Tag.NONE, Tag.NONE),
        # Tag.NONE ne peut jamais détruire
        ("can_destroy", Tag.NONE, Tag.ENEMY),
        ("can_destroy", Tag.PLAYER, Tag.NONE),
        # Tag.NONE ne permet jamais un pickup
        ("can_pickup", Tag.NONE, Tag.PICKUP),
        ("can_pickup", Tag.PLAYER, Tag.NONE),
        ("can_pickup", Tag.NONE, Tag.NONE),
        # Interactions invalides retournent False
        ("can_destroy", Tag.PLAYER, Tag.ENEMY),
        ("can_destroy", Tag.PLAYER, Tag.WALL),
        ("can_destroy", Tag.WALL, Tag.PLAYER),
    ],
)
def test_tag_none_and_invalid_interactions(method: str, tag1: Tag, tag2: Tag):
    """
    Tag.NONE ne doit jamais interagir avec aucun tag.
    Les interactions non définies doivent également retourner False.
    """
    method_func = getattr(TagSystem, method)
    assert method_func(tag1, tag2) is False


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
