"""The simulator itself, spec 004."""

import random

from snnbot.body.vehicle1 import Vehicle1
from snnbot.clock import Clock
from snnbot.recorder import Recorder
from snnbot.run import run
from snnbot.world import World


def test_the_same_seed_gives_exactly_the_same_stream():
    a, b = run(seconds=5, seed=7), run(seconds=5, seed=7)
    assert [s[0::1] for s in a[1].spikes] == [s[0::1] for s in b[1].spikes]
    assert len(a[1]) > 0


def test_a_different_seed_gives_a_different_one():
    a, b = run(seconds=5, seed=7), run(seconds=5, seed=8)
    assert a[1].spikes != b[1].spikes


def test_it_runs_headless():
    vehicle, rec = run(seconds=1, seed=1)
    assert len(rec) > 0
    assert {"retina", "effector.left", "proprioception.left"} <= set(rec.counts())


def test_no_component_is_handed_a_tick_index():
    """Times are times: a run that does not start at zero behaves the same."""
    def stream(start_ms):
        world = World(object_deg=18.0)
        v = Vehicle1(world, rng=random.Random(2))
        rec, clock = Recorder(), Clock()
        clock.t = start_ms
        for t in clock.times(3000):
            for source, events in v.step(t).items():
                rec.record(t, source, events)
        return [(t - start_ms, s, str(e)) for t, s, e in rec.spikes]

    assert stream(0) == stream(1_234_560)


def test_the_babbling_moves_the_head():
    vehicle, _ = run(seconds=10, seed=1)
    assert abs(vehicle.head_deg) > 1.0
