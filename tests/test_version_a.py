"""Version A of spec 005: the ground truth vehicle, driven by a P controller."""

import random

from snnbot.body.vehicle1 import LEFT, RIGHT, Vehicle1
from snnbot.clock import Clock
from snnbot.control import ProportionalController
from snnbot.params import CELL_ANGLE_DEG, DEG_PER_SPIKE, MAX_TURN_RATE
from snnbot.world import World

OBJECT = 18.0


def drive(object_deg=OBJECT, seconds=3.0, head_deg=None, **kw):
    """Run Version A and return the vehicle and the head angle at every tick."""
    v = Vehicle1(World(object_deg=object_deg), rng=random.Random(0),
                 controller=ProportionalController(**kw))
    if head_deg is not None:                    # start with the head already turned
        v.actuators[LEFT].level = 50 + head_deg / (2 * 0.4)
        v.actuators[RIGHT].level = 50 - head_deg / (2 * 0.4)
    angles, fired = [], []
    for t in Clock().times(int(seconds * 1000)):
        fired.append(v.step(t))
        angles.append(v.head_deg)
    return v, angles, fired


def test_it_brings_the_object_to_the_middle_of_the_eye():
    v, _, _ = drive()
    assert v.retina.busy_cell() == 5


def test_it_stops_once_the_object_is_in_the_middle():
    _, angles, _ = drive()
    assert angles[-1] == angles[-200]           # the last two seconds, unmoved


def test_it_stops_at_the_edge_of_the_middle_cell_not_at_its_centre():
    """The error is zero anywhere inside cell 5, so it stops on the way in."""
    v, _, _ = drive()
    off_centre = abs(OBJECT - v.head_deg)
    assert off_centre <= CELL_ANGLE_DEG / 2      # inside the cell
    assert off_centre > CELL_ANGLE_DEG / 4       # but nowhere near its middle


def test_it_never_overshoots():
    _, angles, _ = drive()
    steps = [b - a for a, b in zip(angles, angles[1:]) if b != a]
    assert steps and all(s > 0 for s in steps)   # it only ever turned one way


def test_it_never_turns_faster_than_the_spiking_vehicle():
    _, angles, _ = drive(object_deg=36.0)
    assert max(abs(b - a) for a, b in zip(angles, angles[1:])) <= DEG_PER_SPIKE + 1e-9


def test_it_does_nothing_with_nothing_in_sight():
    v, angles, _ = drive(object_deg=60.0)        # past the edge of the eye
    assert v.retina.busy_cell() is None
    assert set(angles) == {0.0}


def test_no_spike_drives_it():
    _, _, fired = drive()
    assert not any(k.startswith("effector") for f in fired for k in f)


def test_the_head_stays_within_its_range():
    _, angles, _ = drive(object_deg=44.0, head_deg=40.0)
    assert max(angles) <= 40.0 + 1e-9


def test_an_object_out_of_reach_is_seen_but_never_centred():
    """Beyond about 44 degrees the eye can see it and still not centre it."""
    v, angles, _ = drive(object_deg=55.0, head_deg=40.0)
    assert v.retina.busy_cell() is not None
    assert v.retina.busy_cell() != 5
    assert angles[-1] == 40.0                    # pinned against the stop


def test_the_rate_is_held_between_the_controller_ticks():
    c = ProportionalController(tick_ms=100)
    first = c.update(0, 3)
    assert c.update(50, 9) == first              # a new cell, but not its turn yet
    assert c.update(100, 9) != first             # now it gets to look again


def test_the_error_is_measured_in_degrees_from_the_middle():
    c = ProportionalController()
    assert c.error(3) == 2 * CELL_ANGLE_DEG      # two cells to the left
    assert c.error(5) == 0
    assert c.error(9) == -4 * CELL_ANGLE_DEG


def test_the_rate_is_capped():
    c = ProportionalController(kp=1000)
    assert c.update(0, 1) == MAX_TURN_RATE
    assert c.update(1000, 9) == -MAX_TURN_RATE
