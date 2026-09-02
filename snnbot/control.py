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
                     KP, MAX_TURN_RATE, NECK_MAX_RATE_DEG_S, RECRUIT_NECK_DEG)


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

    def error(self, active_cell):
        """How far off the middle of the eye the object is, in degrees.

        Positive when it sits to the left and the eye has to turn left to catch
        it, which is the sense every other angle in this project uses. In
        degrees rather than in cells, so that the width of a cell — still a
        provisional number — stays out of the gain.
        """
        return (self._centre - active_cell) * self._cell_angle

    def update(self, t, active_cell):
        """The rate to turn at, in degrees per second. Held between ticks."""
        if self._next_t is not None and t < self._next_t:
            return self._rate
        self._next_t = t + self.tick_ms
        if active_cell is None:         # nothing in sight, nothing to do
            self._rate = 0.0
        else:
            rate = self.kp * self.error(active_cell)
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

    def error(self, active_cell):
        """The part of the error the eye is not expected to cover by itself."""
        e = super().error(active_cell)
        if abs(e) <= self.threshold:
            return 0.0
        return e - math.copysign(self.threshold, e)


class GazeController:
    """Version A of spec 006: one controller per joint, both reading the same eye.

    Neither is told what the other is doing, and neither can be: the error they
    share is the only thing either of them reads, and it is an error of gaze —
    the sum of the two angles — not of any one joint. What keeps them from
    fighting is that both drive the sum the same way, and that the neck gives up
    first: inside its dead zone it stops dead and leaves the rest to the eye.
    """

    def __init__(self, eye=None, neck=None):
        self.eye = eye if eye is not None else ProportionalController(
            max_rate=HEAD_MAX_RATE_DEG_S)
        self.neck = neck if neck is not None else DeadZoneController()

    def update(self, t, active_cell):
        """The rate to turn each joint at, in degrees per second: head, then neck."""
        return self.eye.update(t, active_cell), self.neck.update(t, active_cell)
