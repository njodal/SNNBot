"""Version B of spec 006: Version D's circuit on each joint, on different inputs."""

import random

from snnbot.body.vehicle2 import HEAD, LEFT, NECK, RIGHT, Vehicle2
from snnbot.clock import Clock
from snnbot.control import GazeController
from snnbot.events import Event, ON, OFF
from snnbot.layers.effector import EffectorLayer
from snnbot.layers.sensory import Arrivals, LearningReflex, PostureReflex, outcome
from snnbot.params import (EYE_CELLS, HEAD_EFFECTORS, NECK_EFFECTORS, ORDER_DELAY_MS,
                           PROP_SENSORS)
from snnbot.world import World


def neck_layers():
    return {side: EffectorLayer(f"{NECK}.{side}", NECK_EFFECTORS, wired=True)
            for side in (LEFT, RIGHT)}


def drive(seconds=3.0, seed=1, object_deg=18.0, controller=None, eye=True, neck=True):
    eye_reflex = (LearningReflex(random.Random(seed), effectors=len(HEAD_EFFECTORS))
                  if eye else None)
    neck_reflex = PostureReflex(random.Random(seed + 3)) if neck else None
    v = Vehicle2(World(object_deg=object_deg), rng=random.Random(seed + 1),
                 controller=controller, eye_reflex=eye_reflex, neck_reflex=neck_reflex)
    fired = [v.step(t) for t in Clock().times(int(seconds * 1000))]
    return v, fired


def counts(fired, prefix):
    return sum(len(s) for f in fired for k, s in f.items() if k.startswith(prefix))


# --- the tonic array read as changes ----------------------------------------

def test_only_the_first_on_after_an_off_is_an_arrival():
    """A sensor that keeps saying the level is still there says nothing new."""
    a = Arrivals()
    assert len(a.update([Event(0, (3,), ON)])) == 1
    assert a.update([Event(20, (3,), ON)]) == []        # the same thing again
    assert a.update([Event(40, (3,), ON)]) == []
    assert len(a.update([Event(60, (3,), OFF)])) == 1   # it left
    assert len(a.update([Event(80, (3,), ON)])) == 1    # and came back


# --- what counts as better, on an array with no middle cell ------------------

def test_the_middle_of_an_even_array_falls_between_two_cells():
    assert outcome((4, 6), PROP_SENSORS) == 1          # 1.5 away, then 0.5
    assert outcome((6, 4), PROP_SENSORS) == -1
    assert outcome((5, 6), PROP_SENSORS) == 0          # both half a cell out
    assert outcome((1, 10), PROP_SENSORS) == 0         # and both four and a half


def test_the_eye_is_judged_exactly_as_it_was():
    assert outcome((3, 5), EYE_CELLS) == 1
    assert outcome((5, 3), EYE_CELLS) == -1
    assert outcome((4, 6), EYE_CELLS) == 0


# --- the neck's layer --------------------------------------------------------

def test_it_is_the_same_circuit_over_the_sensors_of_a_joint():
    neck = PostureReflex(random.Random(0))
    assert len(neck.weights) == PROP_SENSORS * (PROP_SENSORS - 1)
    assert len(neck.actions) == 2 * len(NECK_EFFECTORS)


def test_it_fires_on_the_eye_moving_from_one_sensor_to_the_next():
    """Which is what its cells are about: not where the object is, where the eye is."""
    neck, layers, seen = PostureReflex(random.Random(0)), neck_layers(), []
    for t in range(0, 80):
        events = ([Event(t, (6,), OFF)] if t == 0 else
                  [Event(t, (5,), ON)] if t in (0, 20, 40) else [])
        seen += neck.update(t, None, events, layers)
    assert [e.address for e in seen] == [(6, 5)]        # once, not once per spike


def test_it_learns_from_the_eye_nearing_the_middle_of_its_range():
    neck = PostureReflex(random.Random(0))
    assert neck.told(0, (2, 5), [(2, 5)], []) == 1      # the eye came back
    assert neck.told(0, (5, 2), [(5, 2)], []) == -1     # and went out again


# --- the body with a layer on each joint -------------------------------------

def test_both_joints_are_driven_by_their_own_effectors():
    _, fired = drive()
    assert counts(fired, f"effector.{HEAD}") > 0
    assert counts(fired, f"effector.{NECK}") > 0


def test_each_layer_reads_its_own_sense():
    """The eye's cells fire on the retina, the neck's on the head's array."""
    v, fired = drive()
    assert counts(fired, "sensory.eye") > 0
    assert v.neck_reflex.arrivals._holding                  # it has read the array


def test_no_controller_is_involved():
    v, _ = drive()
    assert v.controller is None


def test_a_ground_truth_eye_can_be_put_under_a_spiking_neck():
    """The rig that tells the neck's learning apart from the eye's: the head on
    Version A, the neck on its own layer."""
    v, fired = drive(controller=GazeController(), eye=False)
    assert counts(fired, f"effector.{HEAD}") == 0          # the controller has it
    assert counts(fired, f"effector.{NECK}") > 0           # its layer has this one
    assert v.head_deg != 0.0


def test_the_eye_is_taught_first_and_frozen_before_the_neck_begins():
    """One learner at a time: a neck that babbles ruins the eye's schooling."""
    from snnbot.run import taught_pair

    eye, neck = taught_pair(1.0, seed=1, object_deg=18.0)
    for layer in (eye, neck):
        assert not layer.learning and layer.explore == 0.0
    assert isinstance(eye, LearningReflex) and isinstance(neck, PostureReflex)
