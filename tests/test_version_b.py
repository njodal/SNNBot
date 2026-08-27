"""Version B of spec 005: the reflex vehicle, no cortex and no learning."""

import random

from snnbot.body.vehicle1 import LEFT, RIGHT, Vehicle1
from snnbot.clock import Clock
from snnbot.layers.sensory import Reflex, wiring
from snnbot.world import World


def drive(object_deg=18.0, seconds=4.0):
    v = Vehicle1(World(object_deg=object_deg), rng=random.Random(0), reflex=Reflex())
    angles, fired = [], []
    for t in Clock().times(int(seconds * 1000)):
        fired.append(v.step(t))
        angles.append(v.head_deg)
    return v, angles, fired


def emitting(vehicle):
    return [e for layer in vehicle.effectors.values()
            for e in layer.effectors if e.emitting]


def test_the_further_out_the_cell_the_faster_the_effector():
    w = wiring()
    assert w[1] == (LEFT, 0) and w[4] == (LEFT, 3)      # 0 is the fastest one
    assert w[9] == (RIGHT, 0) and w[6] == (RIGHT, 3)


def test_the_middle_cell_reaches_nothing():
    assert 5 not in wiring()


def test_it_brings_the_object_to_the_middle_of_the_eye():
    v, _, _ = drive()
    assert v.retina.busy_cell() == 5


def test_it_stops_once_the_object_is_in_the_middle():
    v, angles, _ = drive()
    assert angles[-1] == angles[-100]
    assert emitting(v) == []


def test_it_is_spikes_that_move_it():
    _, _, fired = drive()
    assert any("effector.left" in f for f in fired)
    assert any("sensory" in f for f in fired)


def test_only_one_effector_ever_emits_at_a_time():
    v = Vehicle1(World(object_deg=18.0), rng=random.Random(0), reflex=Reflex())
    for t in Clock().times(4000):
        v.step(t)
        assert len(emitting(v)) <= 1


def test_an_object_to_the_right_turns_the_head_right():
    v, angles, _ = drive(object_deg=-18.0)
    assert v.head_deg < 0
    assert v.retina.busy_cell() == 5


def test_it_does_nothing_with_nothing_in_sight():
    v, angles, fired = drive(object_deg=60.0)
    assert v.retina.busy_cell() is None
    assert set(angles) == {0.0}
    assert not any("effector.left" in f or "effector.right" in f for f in fired)


def test_it_is_slower_than_the_ground_truth():
    """Version B has a handful of speeds to pick from; Version A has all of them."""
    from snnbot.control import ProportionalController

    def time_to_centre(**kw):
        v = Vehicle1(World(object_deg=18.0), rng=random.Random(0), **kw)
        for t in Clock().times(6000):
            v.step(t)
            if v.retina.busy_cell() == 5:
                return t
        return None

    assert time_to_centre(reflex=Reflex()) > time_to_centre(controller=ProportionalController())
