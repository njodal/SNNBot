"""Version A of spec 006: a PID on each joint.

The eye's reads what it sees and says where to look. The neck's reads where the
eye is sitting and says nothing about where to look at all.
"""

import random

from snnbot.body.vehicle2 import LEFT, RIGHT, Vehicle2
from snnbot.clock import Clock
from snnbot.control import GazeController, ProportionalController, RecentringController
from snnbot.params import (CONTRACTION_REST, HEAD_COMFORT_DEG, HEAD_MAX_RATE_DEG_S,
                           HEAD_RANGE_DEG, NECK_MAX_RATE_DEG_S, NECK_RANGE_DEG,
                           RECENTRE_KP)
from snnbot.world import World

FAR = 36.0         # cell 1, the far edge of the eye


def controller(comfort=HEAD_COMFORT_DEG, vor=True, **kw):
    return GazeController(neck=RecentringController(comfort=comfort, **kw), vor=vor)


def preset(joint, degrees):
    """Start with the joint already turned, without spending time turning it."""
    units = degrees / (2 * joint.deg_per_unit)
    joint.actuators[LEFT].level = CONTRACTION_REST + units
    joint.actuators[RIGHT].level = CONTRACTION_REST - units


def drive(object_deg=FAR, seconds=5.0, head_deg=None, neck_deg=None, controller=None):
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


def test_the_gaze_never_overshoots():
    """Either joint may go back on itself. What the two add up to may not."""
    _, head, neck, _ = drive()
    gaze = [h + n for h, n in zip(head, neck)]
    steps = [b - a for a, b in zip(gaze, gaze[1:]) if abs(b - a) > 1e-9]
    assert steps and all(s > 0 for s in steps)


def test_neither_joint_turns_faster_than_its_own_fastest_effector():
    _, head, neck, _ = drive(controller=GazeController(
        eye=ProportionalController(kp=1000, max_rate=HEAD_MAX_RATE_DEG_S),
        neck=RecentringController(kr=1000)))
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


# --- the neck: one input, one job -------------------------------------------

def test_the_neck_reads_the_eye_and_not_the_world():
    """Which cell is busy is nothing to it. That is the eye's business."""
    c = RecentringController(comfort=0.0)
    assert c.rate(1, 10.0) == c.rate(5, 10.0) == c.rate(9, 10.0)
    assert c.rate(5, 10.0) == RECENTRE_KP * 10.0


def test_the_neck_asks_for_nothing_with_nothing_in_sight():
    """No gaze worth holding, and moving the neck alone would only sweep it."""
    assert RecentringController(comfort=0.0).rate(None, 20.0) == 0.0


def test_the_neck_is_deaf_while_the_eye_is_comfortable():
    c = RecentringController(comfort=20.0)
    assert c.off_centre(15.0) == 0.0
    assert c.off_centre(-15.0) == 0.0
    assert c.off_centre(25.0) == 5.0            # what is left once it is subtracted
    assert c.off_centre(-25.0) == -5.0


def test_the_neck_takes_over_what_the_eye_was_holding():
    v, head, neck, _ = drive(controller=controller(comfort=0.0))
    assert abs(head[-1]) < 2.0                  # the eye is back near its middle
    assert abs(neck[-1] - v.gaze_deg) < 2.0     # and the neck is holding the gaze


def test_a_comfortable_range_is_left_for_the_eye_to_hold():
    _, head, _, _ = drive(controller=controller(comfort=20.0))
    assert abs(head[-1] - 20.0) < 1.0           # it stops giving back at the edge


def test_the_gaze_does_not_move_while_the_neck_takes_over():
    """The whole point: the object must not notice its keeper changing."""
    v, _, _, _ = drive(controller=controller(comfort=0.0))
    assert v.retina.busy_cell() == 5


def test_the_eye_is_told_what_the_neck_is_doing():
    """Without the VOR the eye only finds out once the object has left the cell."""
    kept = drive(controller=controller(comfort=0.0))[3]
    adrift = drive(controller=controller(comfort=0.0, vor=False))[3]
    fired = [sum(len(f.get("retina", ())) for f in run) for run in (kept, adrift)]
    assert fired[0] < fired[1] / 10             # a handful against a few hundred


def test_the_vor_gives_way_by_exactly_what_the_neck_took():
    """Nothing is left over: the neck's whole rate is cancelled, the gaze stands."""
    eye_rate, neck_rate = controller().update(0, 5, HEAD_COMFORT_DEG + 10.0)
    assert neck_rate == RECENTRE_KP * 10.0
    assert eye_rate == -neck_rate               # cell 5: the eye asks for nothing else


def test_the_neck_rate_is_capped():
    c = RecentringController(kr=1000, comfort=0.0)
    assert c.update(0, 5, 10.0) == NECK_MAX_RATE_DEG_S
    assert c.update(1000, 5, -10.0) == -NECK_MAX_RATE_DEG_S


def test_the_eye_reaches_the_far_cell_with_no_help_from_the_neck():
    """The neck no longer pushes towards the object, and none of it is missed."""
    v, head, _, _ = drive(object_deg=FAR, seconds=2.0,
                          controller=controller(comfort=HEAD_RANGE_DEG))
    assert v.retina.busy_cell() == 5
    assert head[-1] > 25.0                      # the eye did the whole of it itself
