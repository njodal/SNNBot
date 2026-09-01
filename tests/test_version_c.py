"""Version C of spec 005: the reflex driven by a fully neuromorphic eye."""

import random

from snnbot.body.vehicle1 import Vehicle1
from snnbot.clock import Clock
from snnbot.events import Event, OFF, ON
from snnbot.layers.sensory import CorrelationReflex
from snnbot.params import ORDER_DELAY_MS
from snnbot.world import World, experiment_path


def drive(seconds=9.0, moving=True, object_deg=18.0):
    world = World(object_deg=object_deg, path=experiment_path() if moving else None)
    v = Vehicle1(world, rng=random.Random(0), reflex=CorrelationReflex())
    angles = []
    for t in Clock().times(int(seconds * 1000)):
        world.update(t)
        v.step(t)
        angles.append(v.head_deg)
    return v, angles


def test_there_is_a_cell_for_every_ordered_pair():
    c = CorrelationReflex()
    assert len(c.cells()) == 72                      # 9 successors by 8 predecessors
    assert (3, 3) not in c.cells()


def test_eight_cells_share_each_effector():
    c = CorrelationReflex()
    for j in range(1, 10):
        sharing = [p for p in c.cells() if p[1] == j]
        assert len(sharing) == 8


def test_it_fires_on_a_move_and_only_that_way_round():
    """The eye reports both at once; the delay cell is what makes them a move."""
    c = CorrelationReflex()
    assert c.moved(0, [Event(0, (3,), OFF), Event(0, (2,), ON)]) is None   # not yet
    fired = [c.moved(t, []) for t in range(1, ORDER_DELAY_MS + 1)]
    assert [f for f in fired if f] == [(3, 2)]                # once the wait is up

    c = CorrelationReflex()
    c.moved(0, [Event(0, (2,), OFF), Event(0, (3,), ON)])
    fired = [c.moved(t, []) for t in range(1, ORDER_DELAY_MS + 1)]
    assert [f for f in fired if f] == [(2, 3)]                # the other way round


def test_an_arrival_with_nothing_before_it_fires_nothing():
    """The object turning up in front of the eye is not a move."""
    c = CorrelationReflex()
    c.moved(0, [Event(0, (3,), ON)])
    assert not any(c.moved(t, []) for t in range(1, ORDER_DELAY_MS + 1))


def test_a_predecessor_too_long_ago_does_not_count():
    c = CorrelationReflex()
    c.moved(0, [Event(0, (3,), OFF)])
    c.moved(1000, [Event(1000, (2,), ON)])
    assert not any(c.moved(t, []) for t in range(1001, 1001 + ORDER_DELAY_MS))


def test_it_cannot_see_an_object_that_never_moves():
    """No movement, no events, nothing to react to. This one needs babbling."""
    v, angles = drive(moving=False)
    assert set(angles) == {0.0}
    assert v.retina.busy_cell() != 5


def test_it_tracks_an_object_once_the_object_moves():
    v, _ = drive()
    assert v.retina.busy_cell() == 5


def test_it_does_not_stir_until_the_object_does():
    _, angles = drive()
    assert set(angles[:300]) == {0.0}                # the first three seconds
    assert angles[-1] != 0.0


def test_only_one_effector_ever_emits_at_a_time():
    world = World(object_deg=18.0, path=experiment_path())
    v = Vehicle1(world, rng=random.Random(0), reflex=CorrelationReflex())
    for t in Clock().times(9000):
        world.update(t)
        v.step(t)
        assert sum(e.emitting for layer in v.effectors.values()
                   for e in layer.effectors) <= 1


def test_it_costs_the_eye_less_than_the_reflex_on_the_level_readout():
    from snnbot.layers.sensory import Reflex

    def eye_events(reflex):
        world = World(object_deg=18.0, path=experiment_path())
        v = Vehicle1(world, rng=random.Random(0), reflex=reflex)
        n = 0
        for t in Clock().times(9000):
            world.update(t)
            n += len(v.step(t).get("retina", ()))
        return n

    assert eye_events(CorrelationReflex()) < eye_events(Reflex())
