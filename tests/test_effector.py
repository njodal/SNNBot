"""The effector cells, spec 003 and the babbling of spec 002."""

import random

import pytest

from snnbot.layers.effector import Effector
from snnbot.params import TICK_MS



def emissions(cell, from_t, to_t, before=None):
    out = []
    for t in range(from_t, to_t, TICK_MS):
        if before:
            before(cell, t)
        if cell.update(t) is not None:
            out.append(t)
    return out


def test_once_wired_it_emits_nothing_until_a_start_spike():
    cell = Effector("e", 50, 300, wired=True)
    assert emissions(cell, 0, 1000) == []


def test_it_emits_for_its_duration_and_then_stops_on_its_own():
    cell = Effector("e", 50, 300, wired=True)
    cell.start(0)
    fired = emissions(cell, 0, 1000)
    assert fired == list(range(0, 300, 20))     # 50 Hz is one spike every 20 ms
    assert not cell.emitting


def test_a_stop_spike_ends_it_earlier():
    cell = Effector("e", 50, 300, wired=True)
    cell.start(0)
    fired = emissions(cell, 0, 1000, before=lambda c, t: c.stop(t) if t == 100 else None)
    assert max(fired) < 100


def test_a_faster_effector_contracts_it_faster():
    slow = Effector("slow", 10, 500, wired=True)
    fast = Effector("fast", 50, 500, wired=True)
    slow.start(0)
    fast.start(0)
    assert len(emissions(fast, 0, 500)) == 5 * len(emissions(slow, 0, 500))


def test_an_unwired_cell_babbles():
    cell = Effector("e", 50, 300, rng=random.Random(3))
    fired = emissions(cell, 0, 60_000)
    assert fired, "an uncontrolled cell should go off on its own"
    bursts = [t for i, t in enumerate(fired)
              if i == 0 or t - fired[i - 1] > cell.duration_ms]
    assert 20 < len(bursts) < 40, f"about one burst every two seconds, got {len(bursts)}"


def test_an_unwired_cell_has_no_inputs_to_spike():
    cell = Effector("e", 50, 300, rng=random.Random(0))
    with pytest.raises(RuntimeError):
        cell.start(0)


def test_a_wired_cell_never_babbles():
    cell = Effector("e", 50, 300, wired=True, rng=random.Random(0))
    assert emissions(cell, 0, 60_000) == []


def test_a_frequency_that_is_not_a_whole_number_of_ticks_is_refused():
    with pytest.raises(ValueError):
        Effector("e", 30, 300, wired=True)
