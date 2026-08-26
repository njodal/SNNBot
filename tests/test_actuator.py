"""The actuator, spec 003."""

from snnbot.body.actuator import Actuator
from snnbot.params import RELAX_MS, STEP


def test_one_spike_one_step_always_the_same_direction():
    a = Actuator(level=50)
    for i in range(1, 6):
        a.on_spike(i * 10)
        assert a.level == 50 + i * STEP


def test_twice_as_long_contracts_twice_as_much():
    slow, fast = Actuator(level=0), Actuator(level=0)
    for t in range(0, 100, 10):
        slow.on_spike(t)
    for t in range(0, 200, 10):
        fast.on_spike(t)
    assert fast.level == 2 * slow.level


def test_it_stops_at_the_end_of_the_range():
    a = Actuator(level=0)
    for t in range(0, 10_000, 10):
        a.on_spike(t)
    assert a.level == 100


def test_nothing_it_does_itself_moves_it_back():
    a = Actuator(level=50)
    a.on_spike(0)
    contracted = a.level
    for t in range(10, 5000, 10):
        assert a.level >= contracted
    a.stretched_by(STEP)                       # only the antagonist can
    assert a.level < contracted


def test_relaxing_does_not_undo_the_movement():
    a = Actuator(level=50)
    a.on_spike(0)
    level = a.level
    assert not a.relaxed(0)
    assert a.relaxed(RELAX_MS)
    assert a.level == level
