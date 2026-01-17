import pytest

from vect_hunt.engine.core import Tag
from vect_hunt.engine.core import TagSystem
from vect_hunt.engine.core import CAN_COLLIDE, CAN_DESTROY, CAN_PICKUP


def _expected_can_collide(tag1: Tag, tag2: Tag) -> bool:
    return bool(
        (CAN_COLLIDE.get(tag1, Tag.NONE) & tag2)
        or (CAN_COLLIDE.get(tag2, Tag.NONE) & tag1)
    )


def _expected_can_destroy(tag1: Tag, tag2: Tag) -> bool:
    return bool(CAN_DESTROY.get(tag1, Tag.NONE) & tag2)


def _expected_can_pickup(tag1: Tag, tag2: Tag) -> bool:
    return bool(CAN_PICKUP.get(tag1, Tag.NONE) & tag2)


@pytest.mark.parametrize("tag1", list(Tag))
@pytest.mark.parametrize("tag2", list(Tag))
def test_can_collide_matches_config(tag1: Tag, tag2: Tag) -> None:
    """
    Vérifie que can_collide reflète la configuration chargée.
    """
    assert TagSystem.can_collide(tag1, tag2) is _expected_can_collide(tag1, tag2)


@pytest.mark.parametrize("tag1", list(Tag))
@pytest.mark.parametrize("tag2", list(Tag))
def test_can_destroy_matches_config(tag1: Tag, tag2: Tag) -> None:
    """
    Vérifie que can_destroy reflète la configuration chargée.
    """
    assert TagSystem.can_destroy(tag1, tag2) is _expected_can_destroy(tag1, tag2)


@pytest.mark.parametrize("tag1", list(Tag))
@pytest.mark.parametrize("tag2", list(Tag))
def test_can_pickup_matches_config(tag1: Tag, tag2: Tag) -> None:
    """
    Vérifie que can_pickup reflète la configuration chargée.
    """
    assert TagSystem.can_pickup(tag1, tag2) is _expected_can_pickup(tag1, tag2)

