"""Version F of spec 005: the ground truth's controller, built of cells (spec 011)."""

import random

from snnbot.body.vehicle1 import LEFT, RIGHT, Vehicle1
from snnbot.clock import Clock
from snnbot.control import ProportionalController
from snnbot.events import Event, OFF, ON
from snnbot.layers.sensory import ProportionalReflex, proportional_ladder
from snnbot.params import CELL_ANGLE_DEG, DEG_PER_SPIKE, KP, MAX_TURN_RATE
from snnbot.world import World, experiment_path


def drive(object_deg=18.0, seconds=4.0, moving=False, **kw):
    world = World(object_deg=object_deg, path=experiment_path() if moving else None)
    kw = kw or {"reflex": ProportionalReflex()}
    v = Vehicle1(world, rng=random.Random(0), **kw)
    angles, fired = [], []
    for t in Clock().times(int(seconds * 1000)):
        world.update(t)
        fired.append(v.step(t))
        angles.append(v.head_deg)
    return v, angles, fired


def emitting(vehicle):
    return [(side, i) for side, layer in vehicle.effectors.items()
            for i, e in enumerate(layer.effectors) if e.emitting]


def test_the_ladder_is_cut_to_the_gain():
    """One rung per whole cell of error, rounded to a whole millisecond."""
    for d, (hz, _) in enumerate(proportional_ladder(), start=1):
        wanted = min(KP * d * CELL_ANGLE_DEG / DEG_PER_SPIKE, MAX_TURN_RATE / DEG_PER_SPIKE)
        assert round(1000 / hz, 6) == round(1000 / wanted)
    assert proportional_ladder()[3][0] * DEG_PER_SPIKE <= MAX_TURN_RATE
    assert proportional_ladder()[-1][0] * DEG_PER_SPIKE == MAX_TURN_RATE   # capped


def test_the_table_has_a_cell_for_every_pair():
    r = ProportionalReflex()
    assert len(r.table) == 81
    assert (5, 5) in r.table                  # unlike the correlation cells


def test_a_diagonal_reaches_one_rung_and_the_middle_one_reaches_none():
    r = ProportionalReflex()
    assert r.wire(-4) == (LEFT, 3) and r.wire(-1) == (LEFT, 0)
    assert r.wire(4) == (RIGHT, 3) and r.wire(1) == (RIGHT, 0)
    assert r.wire(0) is None


def test_an_object_in_cell_i_wakes_the_rung_for_its_error_and_no_other():
    for cell, deg in ((3, 18.0), (1, 36.0), (7, -18.0), (9, -36.0)):
        v = Vehicle1(World(object_deg=deg), rng=random.Random(0),
                     reflex=ProportionalReflex())
        for t in Clock().times(60):
            v.step(t)
        side = LEFT if cell < 5 else RIGHT
        assert emitting(v) == [(side, abs(cell - 5) - 1)]


def test_it_brings_the_object_to_the_middle_of_the_eye():
    v, _, _ = drive()
    assert v.retina.busy_cell() == 5


def test_zero_error_stops_every_effector_and_nothing_starts_again():
    v, angles, _ = drive()
    assert emitting(v) == []
    assert angles[-1] == angles[-2000]


def test_an_object_to_the_right_turns_the_head_right():
    v, _, _ = drive(object_deg=-18.0)
    assert v.head_deg < 0 and v.retina.busy_cell() == 5


def test_it_is_spikes_that_move_it():
    _, _, fired = drive()
    assert any("effector.left" in f for f in fired)
    assert any("sensory" in f for f in fired)


def test_the_table_fires_at_the_rate_its_sources_hold():
    _, _, fired = drive(seconds=1.0)
    table = [e for f in fired for e in f.get("sensory", ())]
    assert 40 <= len(table) <= 55                    # about 50 Hz, for a second


def test_only_one_effector_ever_emits_at_a_time():
    v = Vehicle1(World(object_deg=36.0), rng=random.Random(0), reflex=ProportionalReflex())
    for t in Clock().times(4000):
        v.step(t)
        assert len(emitting(v)) <= 1


def test_it_does_nothing_with_nothing_in_sight():
    v, angles, fired = drive(object_deg=60.0)
    assert v.retina.busy_cell() is None
    assert set(angles) == {0.0}
    assert not any("effector.left" in f or "effector.right" in f for f in fired)


def test_moving_the_reference_moves_the_head_with_the_eye_reporting_nothing():
    """The one thing Version B has not got: `r` as an input."""
    v = Vehicle1(World(object_deg=0.0), rng=random.Random(0), reflex=ProportionalReflex())
    for t in Clock().times(500):
        v.step(t)
    assert v.retina.busy_cell() == 5 and v.head_deg == 0.0
    v.reflex.refer(500, 3)                        # a spike into the reference row
    for t in Clock().times(3000):
        v.step(500 + t)
    assert v.retina.busy_cell() == 3               # two cells off, on the right side
    assert v.head_deg < 0


def test_it_reads_the_eye_as_spikes_and_never_as_a_number():
    r = ProportionalReflex()
    fired = []
    for t in range(60):
        eye = [Event(0, (3,), ON)] if t == 1 else []
        fired += r.fired(t, eye)
    assert fired and set(fired) == {(3, 5)}
    r.fired(60, [Event(60, (3,), OFF)])
    assert not any(r.fired(t, []) for t in range(61, 120))


def test_it_matches_the_ground_truth_to_within_a_cell():
    """The same law, quantised to the ladder: never a cell apart from Version A."""
    _, a, _ = drive(seconds=15.0, moving=True, controller=ProportionalController())
    _, f, _ = drive(seconds=15.0, moving=True, reflex=ProportionalReflex())
    assert max(abs(x - y) for x, y in zip(a, f)) < CELL_ANGLE_DEG


def test_nothing_in_it_reads_a_value():
    """The reflex is handed the active cell as a number, as every reflex is, and
    turns the head the same with it or without it."""
    world = World(object_deg=18.0)
    v = Vehicle1(world, rng=random.Random(0), reflex=ProportionalReflex())
    told, untold = [], []
    for t in Clock().times(2000):
        told.append(v.step(t))
    w = Vehicle1(World(object_deg=18.0), rng=random.Random(0), reflex=ProportionalReflex())
    w.retina.busy_cell = lambda: None            # the number taken away
    for t in Clock().times(2000):
        untold.append(w.step(t))
    assert v.head_deg == w.head_deg and told == untold
