import pytest

from vect_hunt.engine.physics.collision_tracker import CollisionTracker


def test_update_sets_active_collision_and_duration():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions={(1, 2)},
        current_triggers=set(),
        collision_info={},
        delta_time=0.1,
    )

    assert tracker.is_collision_active(1, 2) is True
    assert tracker.get_collision_duration(1, 2) == pytest.approx(0.1)


def test_update_accumulates_duration():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions={(2, 3)},
        current_triggers=set(),
        collision_info={},
        delta_time=0.1,
    )
    tracker.update(
        current_collisions={(2, 3)},
        current_triggers=set(),
        collision_info={},
        delta_time=0.2,
    )

    assert tracker.get_collision_duration(2, 3) == pytest.approx(0.3)


def test_enter_and_exit_tracking():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions={(1, 2)},
        current_triggers=set(),
        collision_info={},
        delta_time=0.1,
    )

    assert tracker.did_enter(1, 2) is True
    assert tracker.did_exit(1, 2) is False

    tracker.update(
        current_collisions=set(),
        current_triggers=set(),
        collision_info={},
        delta_time=0.1,
    )

    assert tracker.is_collision_active(1, 2) is False
    assert tracker.did_exit(1, 2) is True


def test_triggers_are_tracked_separately():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions=set(),
        current_triggers={(3, 4)},
        collision_info={},
        delta_time=0.1,
    )

    assert tracker.is_trigger_active(3, 4) is True
    assert tracker.is_collision_active(3, 4) is False


def test_collision_info_is_normalized():
    tracker = CollisionTracker()
    info = {(5, 4): {"normal": (1, 0)}}
    tracker.update(
        current_collisions={(4, 5)},
        current_triggers=set(),
        collision_info=info,
        delta_time=0.1,
    )

    assert tracker.get_collision_info(4, 5) == {"normal": (1, 0)}
    assert tracker.get_collision_info(5, 4) == {"normal": (1, 0)}


def test_get_objects_helpers():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions={(1, 2), (1, 3)},
        current_triggers={(2, 4)},
        collision_info={},
        delta_time=0.1,
    )

    assert set(tracker.get_colliding_objects(1)) == {2, 3}
    assert tracker.get_triggering_objects(2) == [4]


def test_clear_resets_state():
    tracker = CollisionTracker()
    tracker.update(
        current_collisions={(1, 2)},
        current_triggers={(3, 4)},
        collision_info={},
        delta_time=0.1,
    )

    tracker.clear()

    assert tracker.get_all_collisions() == []
    assert tracker.get_all_triggers() == []
    assert tracker.get_all_entered() == []
    assert tracker.get_all_exited() == []
