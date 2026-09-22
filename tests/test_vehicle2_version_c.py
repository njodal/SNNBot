"""Version C of spec 006: Version A of it, built of the cells of spec 011."""

import random

from snnbot.body.vehicle2 import HEAD, LEFT, NECK, RIGHT, Vehicle2
from snnbot.clock import Clock
from snnbot.control import GazeController
from snnbot.layers.sensory import gaze_reflexes, proportional_ladder
from snnbot.params import (CELL_ANGLE_DEG, CONTRACTION_REST, EYE_CELLS,
                           HEAD_COMFORT_DEG, HEAD_DEG_PER_SPIKE, HEAD_RANGE_DEG,
                           KP, NECK_DEG_PER_SPIKE, PROP_SENSORS, RECENTRE_KP)
from snnbot.world import World, experiment_path

LEVEL_DEG = 2 * HEAD_RANGE_DEG / PROP_SENSORS       # 9, as one cell of the eye
AT_REST = 6                                         # the level a centred head sits in


def drive(object_deg=36.0, seconds=5.0, moving=False, version="C"):
    world = World(object_deg=object_deg,
                  path=experiment_path(object_deg) if moving else None)
    if version == "A":
        v = Vehicle2(world, rng=random.Random(0), controller=GazeController())
    else:
        eye, neck = gaze_reflexes()
        v = Vehicle2(world, rng=random.Random(0), eye_reflex=eye, neck_reflex=neck,
                     vor=True)
    gaze, fired = [], []
    for t in Clock().times(int(seconds * 1000)):
        world.update(t)
        fired.append(v.step(t))
        gaze.append(v.gaze_deg)
    return v, gaze, fired


def emitting(joint):
    return [(side, i) for side, layer in joint.effectors.items()
            for i, e in enumerate(layer.effectors) if e.emitting]


# --- it does what Version A does ---------------------------------------------

def test_it_brings_the_object_to_the_middle_of_the_eye():
    v, _, _ = drive()
    assert v.retina.busy_cell() == 5


def test_it_follows_version_a_to_within_a_cell_of_the_eye():
    """The criterion spec 011 sets for Version F, asked of both joints at once."""
    _, mine, _ = drive(object_deg=18.0, seconds=15.0, moving=True)
    _, truth, _ = drive(object_deg=18.0, seconds=15.0, moving=True, version="A")
    assert max(abs(a - b) for a, b in zip(mine, truth)) < CELL_ANGLE_DEG


def test_the_neck_ends_up_holding_what_the_eye_was():
    """The same division of labour: the eye near its middle, the neck bearing it."""
    v, _, _ = drive(seconds=8.0)
    assert 0.0 < v.neck_deg < v.head_deg            # some of it, not all of it
    assert v.head_deg < 36.0                        # and less than it started with


def test_no_controller_reads_anything():
    v, _, fired = drive()
    assert v.controller is None
    assert any(k.startswith("effector") for f in fired for k in f)


# --- the two circuits, and what differs between them -------------------------

def test_the_eye_holds_where_the_object_is_and_the_neck_does_not_have_to():
    """A retina reports only change; a propioceptor keeps saying where it is."""
    eye, neck = gaze_reflexes()
    assert len(eye.holds) == EYE_CELLS               # a memory cell per level
    assert neck.tonic and neck.holds == {}           # a row of cells fewer


def test_the_eye_refers_to_its_middle_cell_and_the_neck_to_where_it_rests():
    eye, neck = gaze_reflexes()
    assert eye._refer_to == (EYE_CELLS + 1) // 2
    assert neck._refer_to == AT_REST
    assert neck.cells == PROP_SENSORS


def test_the_comfortable_range_is_diagonals_wired_to_nothing():
    eye, neck = gaze_reflexes()
    assert eye.dead == 0
    assert neck.dead == int(HEAD_COMFORT_DEG / LEVEL_DEG) == 2
    assert neck.wire(2) == neck.wire(-1) == "hold"   # inside: no wire at all
    assert neck.wire(0) is None                      # the brake, as ever
    assert neck.wire(3) is not None


def test_the_neck_turns_the_way_the_eye_is_turned():
    """Its rows are the head's left array, where a higher level is a head to the
    left — so its diagonals run the other way round from the eye's."""
    eye, neck = gaze_reflexes()
    assert eye.wire(3)[0] == RIGHT and eye.wire(-3)[0] == LEFT
    assert neck.wire(3)[0] == LEFT and neck.wire(-3)[0] == RIGHT


def test_each_ladder_is_cut_to_its_own_joint():
    """The eye answers cells of retina in eye spikes; the neck answers levels of
    the head's array in neck spikes, less the range it does not answer at all."""
    eye, neck = gaze_reflexes()
    # Each rung is its exact frequency rounded to a whole millisecond of period,
    # which is all spec 004 lets a period be.
    for d, (hz, _) in enumerate(eye.ladder, start=1):
        wanted = KP * d * CELL_ANGLE_DEG / HEAD_DEG_PER_SPIKE
        assert round(1000 / hz, 6) == round(1000 / wanted)
    for d, (hz, _) in enumerate(neck.ladder[neck.dead:], start=neck.dead + 1):
        wanted = RECENTRE_KP * (d - neck.dead) * LEVEL_DEG / NECK_DEG_PER_SPIKE
        assert round(1000 / hz, 6) == round(1000 / wanted)


def test_a_rung_runs_for_longer_than_its_own_period():
    """Or the slow end of the ladder would emit once and wait, at the wrong rate."""
    _, neck = gaze_reflexes()
    for hz, duration_ms in neck.ladder:
        assert duration_ms > 1000 / hz


def test_the_body_takes_each_joint_s_ladder_from_its_layer():
    eye, neck = gaze_reflexes()
    v = Vehicle2(World(object_deg=18.0), eye_reflex=eye, neck_reflex=neck)
    assert len(v.head.effectors[LEFT].effectors) == len(eye.ladder)
    assert len(v.neck.effectors[LEFT].effectors) == len(neck.ladder)


# --- what the circuit does at the two ends of the error -----------------------

def test_an_object_in_the_middle_stops_every_effector():
    v, _, _ = drive(object_deg=0.0, seconds=1.0)
    assert v.retina.busy_cell() == 5
    assert emitting(v.head) == [] and emitting(v.neck) == []


def test_the_neck_is_woken_only_once_the_eye_is_past_its_comfort():
    """Under the comfortable range the neck's table fires and reaches nothing."""
    v, _, fired = drive(object_deg=9.0, seconds=2.0)      # one cell out: the eye's own
    assert v.retina.busy_cell() == 5
    assert not any(k.startswith(f"effector.{NECK}") for f in fired for k in f)
    assert any(k.startswith("sensory.neck") for f in fired for k in f)


def test_the_reflex_arc_gives_way_when_the_neck_moves():
    _, _, fired = drive(seconds=8.0)
    assert sum(len(s) for f in fired for k, s in f.items() if k == "vor") > 0
