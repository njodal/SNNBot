"""Version A of [spec 005]: the ground truth controller.

Not a brain. It reads the body the way no vehicle of this project is allowed to
— the active cell as a plain number — and drives the same body the spiking
vehicle has. It exists to say how well the task can be done at all, so that the
spiking vehicle has something to be compared against.

A PID in name; on this body two of its three terms are zero. The plant is a pure
integrator, the controller setting the rate the eye turns, so proportional
feedback alone converges without overshoot: an integral term could only carry
the eye past the target and wind up against the stop, and a derivative term
would be differentiating a nine step staircase.

Version A of [spec 006] is two of these, one per joint. The eye keeps this
controller unchanged; the neck gets the same one with a dead zone around the
middle, so that it moves only for what the eye cannot reach on its own.
"""

import math

from .params import (CELL_ANGLE_DEG, CONTROL_TICK_MS, EYE_CELLS, HEAD_MAX_RATE_DEG_S,
                     KP, MAX_TURN_RATE, NECK_MAX_RATE_DEG_S, RECENTRE_KP,
                     RECRUIT_NECK_DEG)


class ProportionalController:
    def __init__(self, kp=KP, tick_ms=CONTROL_TICK_MS, max_rate=MAX_TURN_RATE,
                 cell_angle=CELL_ANGLE_DEG, cells=EYE_CELLS):
        self.kp = kp
        self.tick_ms = tick_ms
        self.max_rate = max_rate
        self._cell_angle = cell_angle
        self._centre = (cells + 1) / 2
        self._rate = 0.0
        self._next_t = None
        self.recentring = 0.0       # what of the last rate was giving range back

    def error(self, active_cell):
        """How far off the middle of the eye the object is, in degrees.

        Positive when it sits to the left and the eye has to turn left to catch
        it, which is the sense every other angle in this project uses. In
        degrees rather than in cells, so that the width of a cell — still a
        provisional number — stays out of the gain.
        """
        return (self._centre - active_cell) * self._cell_angle

    def rate(self, active_cell):
        """What the law asks for, before the cap. The place a second law is added."""
        if active_cell is None:         # nothing in sight, nothing to do
            return 0.0
        return self.kp * self.error(active_cell)

    def update(self, t, active_cell, *body):
        """The rate to turn at, in degrees per second. Held between ticks."""
        if self._next_t is not None and t < self._next_t:
            return self._rate
        self._next_t = t + self.tick_ms
        rate = self.rate(active_cell, *body)
        self._rate = max(-self.max_rate, min(self.max_rate, rate))
        return self._rate


class DeadZoneController(ProportionalController):
    """The neck's half of Version A of spec 006: the same P, deaf near the middle.

    A human makes gaze shifts of less than about twenty degrees with the eye
    alone and recruits the head past that, so what tells the two joints apart
    here is a threshold rather than a share. What is left after the threshold is
    subtracted, and not the whole error, is what it acts on: at the boundary the
    neck starts from nothing instead of lurching into motion.
    """

    def __init__(self, threshold=RECRUIT_NECK_DEG, max_rate=NECK_MAX_RATE_DEG_S, **kw):
        super().__init__(max_rate=max_rate, **kw)
        self.threshold = threshold

    def rate(self, active_cell, head_deg=0.0):
        """Where the eye is sitting is not this law's business. The next one reads it."""
        return super().rate(active_cell)

    def error(self, active_cell):
        """The part of the error the eye is not expected to cover by itself."""
        e = super().error(active_cell)
        if abs(e) <= self.threshold:
            return 0.0
        return e - math.copysign(self.threshold, e)


class RecentringController(DeadZoneController):
    """The neck's controller with a second input: where the eye is sitting.

    The first law reads the eye and says where to look. This one reads the head
    joint's own angle and says nothing about where to look at all — it asks for
    the neck to take over whatever the eye is holding, so that the eye comes
    back to the middle of its range and is ready for the next thing to turn up
    anywhere. Which is what the two joints are for: not a longer reach, since
    the neck alone would give that, but a quick joint kept near the middle of
    its travel by a slow one.

    It is the first loop in this project that closes on the body rather than on
    the world, and the only reading a spiking vehicle could get of it is the
    1x10 propioceptive array of the head's actuators.

    With nothing in sight it asks for nothing. There is no gaze worth holding,
    and moving the neck alone would only sweep it — a search, which this is not.
    """

    def __init__(self, kr=RECENTRE_KP, **kw):
        super().__init__(**kw)
        self.kr = kr

    def rate(self, active_cell, head_deg=0.0):
        if active_cell is None:
            self.recentring = 0.0
            return 0.0
        self.recentring = self.kr * head_deg
        return super().rate(active_cell) + self.recentring


class GazeController:
    """Version A of spec 006: one controller per joint, both reading the same eye.

    Neither is told what the other is doing, and neither could be told usefully:
    what they share is an error of gaze — the sum of the two angles — which is
    nobody's angle in particular. What keeps them from fighting is that both
    drive the sum the same way, and that the neck gives up first: inside its
    dead zone it stops dead and leaves the rest to the eye.

    The one thing that is coordinated is the re-centring, and it has to be. A
    neck that moves while the gaze is meant to stay put needs the eye to give
    way by exactly as much, and the eye cannot work that out from what it sees:
    inside a cell there is no error to see at all, so it would not notice until
    the object had crossed into the next one. So the eye is handed the neck's
    re-centring rate directly and cancels it — which is what a vestibulo-ocular
    reflex is, and it is subtracted from the *re-centring only*: during a gaze
    shift the neck's other term goes uncancelled, or recruiting it would achieve
    nothing. A real VOR reads a canal, a velocity sensor this vehicle has not
    got; what stands in for it here is a copy of the command.
    """

    def __init__(self, eye=None, neck=None, vor=True):
        self.eye = eye if eye is not None else ProportionalController(
            max_rate=HEAD_MAX_RATE_DEG_S)
        self.neck = neck if neck is not None else DeadZoneController()
        self.vor = vor

    def update(self, t, active_cell, head_deg=0.0):
        """The rate to turn each joint at, in degrees per second: head, then neck."""
        neck_rate = self.neck.update(t, active_cell, head_deg)
        eye_rate = self.eye.update(t, active_cell)
        if self.vor:
            eye_rate -= self.neck.recentring
        cap = self.eye.max_rate
        return max(-cap, min(cap, eye_rate)), neck_rate
