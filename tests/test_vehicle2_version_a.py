"""Version A of spec 006: a PID on each joint, the neck's deaf near the middle."""

import random

from snnbot.body.vehicle2 import LEFT, RIGHT, Vehicle2
from snnbot.clock import Clock
from snnbot.control import DeadZoneController, GazeController, ProportionalController
from snnbot.params import (CELL_ANGLE_DEG, CONTRACTION_REST, HEAD_MAX_RATE_DEG_S,
                           HEAD_RANGE_DEG, NECK_MAX_RATE_DEG_S, NECK_RANGE_DEG,
                           RECRUIT_NECK_DEG)
from snnbot.world import World

NEAR = 18.0        # cell 3: inside the threshold, the eye's business alone
FAR = 36.0         # cell 1: far enough out that the neck is recruited


def preset(joint, degrees):
    """Start with the joint already turned, without spending time turning it."""
    units = degrees / (2 * joint.deg_per_unit)
    joint.actuators[LEFT].level = CONTRACTION_REST + units
    joint.actuators[RIGHT].level = CONTRACTION_REST - units


def drive(object_deg=FAR, seconds=3.0, head_deg=None, neck_deg=None, controller=None):
    """Run Version A and return the vehicle and both angles at every tick."""
    v = Vehicle2(World(object_deg=object_deg), rng=random.Random(0),
                 controller=controller or GazeController())
    if head_deg is not None:
        preset(v.head, head_deg)
    if neck_deg is not None:
        preset(v.neck, neck_deg)
    head, neck, fired = [], [], []
    for t in Clock().times(int(seconds * 1000)):
        fired.append(v.step(t))
        head.append(v.head_deg)
        neck.append(v.neck_deg)
    return v, head, neck, fired


def test_it_brings_the_object_to_the_middle_of_the_eye():
    v, _, _, _ = drive()
    assert v.retina.busy_cell() == 5


def test_the_gaze_is_the_sum_of_the_two_angles():
    v, head, neck, _ = drive()
    assert v.gaze_deg == head[-1] + neck[-1]


def test_the_neck_stays_put_for_what_the_eye_can_reach_alone():
    """An object inside the threshold is the eye's business and nobody else's."""
    v, head, neck, _ = drive(object_deg=NEAR)
    assert v.retina.busy_cell() == 5
    assert set(neck) == {0.0}
    assert head[-1] > 0.0


def test_the_neck_is_recruited_for_what_is_further_out():
    _, head, neck, _ = drive(object_deg=FAR)
    assert neck[-1] > 0.0
    assert head[-1] > neck[-1]      # the quick joint still does most of it


def test_the_neck_gives_up_once_the_eye_can_finish_on_its_own():
    """It stops the moment the error falls inside the threshold, and stays stopped."""
    _, _, neck, _ = drive(object_deg=FAR)
    assert neck[-1] == neck[-200]
    assert neck[-1] < RECRUIT_NECK_DEG


def test_neither_joint_overshoots():
    _, head, neck, _ = drive()
    for angles in (head, neck):
        steps = [b - a for a, b in zip(angles, angles[1:]) if b != a]
        assert steps and all(s > 0 for s in steps)


def test_neither_joint_turns_faster_than_its_own_fastest_effector():
    _, head, neck, _ = drive(controller=GazeController(
        eye=ProportionalController(kp=1000, max_rate=HEAD_MAX_RATE_DEG_S),
        neck=DeadZoneController(kp=1000)))
    for angles, cap in ((head, HEAD_MAX_RATE_DEG_S), (neck, NECK_MAX_RATE_DEG_S)):
        per_tick = max(abs(b - a) for a, b in zip(angles, angles[1:]))
        assert per_tick <= cap / 1000 + 1e-9


def test_each_joint_stays_within_its_own_range():
    v, head, neck, _ = drive(object_deg=165.0, head_deg=HEAD_RANGE_DEG,
                             neck_deg=NECK_RANGE_DEG)
    assert v.retina.busy_cell() is not None     # seen, and still not reachable
    assert v.retina.busy_cell() != 5
    assert max(head) <= HEAD_RANGE_DEG + 1e-9
    assert max(neck) <= NECK_RANGE_DEG + 1e-9


def test_it_does_nothing_with_nothing_in_sight():
    v, head, neck, _ = drive(object_deg=60.0)   # past the edge of the eye
    assert v.retina.busy_cell() is None
    assert set(head) == set(neck) == {0.0}


def test_no_spike_drives_it():
    _, _, _, fired = drive()
    assert not any(k.startswith("effector") for f in fired for k in f)


def test_the_eye_reads_the_error_exactly_as_vehicle_1_does():
    assert GazeController().eye.error(3) == ProportionalController().error(3)


def test_the_neck_is_deaf_inside_the_threshold():
    c = DeadZoneController()
    assert c.error(4) == 0.0                    # one cell out: 9 degrees
    assert c.error(3) == 0.0                    # two cells out: 18, still inside
    assert c.error(5) == 0.0


def test_the_neck_acts_on_what_is_left_after_the_threshold():
    """Subtracting it is what keeps the neck from lurching at the boundary."""
    c = DeadZoneController()
    assert c.error(2) == 3 * CELL_ANGLE_DEG - RECRUIT_NECK_DEG
    assert c.error(8) == -(3 * CELL_ANGLE_DEG - RECRUIT_NECK_DEG)
    assert c.error(1) > c.error(2) > 0


def test_the_neck_rate_is_capped():
    c = DeadZoneController(kp=1000)
    assert c.update(0, 1) == NECK_MAX_RATE_DEG_S
    assert c.update(1000, 9) == -NECK_MAX_RATE_DEG_S
