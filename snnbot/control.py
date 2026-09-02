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

Version A of [spec 006] is two of these, one per joint, and they do not read the
same thing. The eye keeps this controller unchanged, closing on what it sees.
The neck closes on the eye.
"""

import math

from .params import (CELL_ANGLE_DEG, CONTROL_TICK_MS, EYE_CELLS, EYE_CONTROL_MS,
                     HEAD_MAX_RATE_DEG_S, HEAD_COMFORT_DEG, KP, MAX_TURN_RATE,
                     NECK_CONTROL_MS, NECK_MAX_RATE_DEG_S, RECENTRE_KP)


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


class RecentringController(ProportionalController):
    """The neck's controller. One input, one job: where the eye is sitting.

    It is told nothing about the object and could do nothing with it. What it
    reads is the head joint's own angle — how much of the looking the eye is
    doing — and what it asks for is that the neck take that over, so that the
    eye comes back to the middle of its range and is ready for the next thing to
    turn up anywhere. Which is what the two joints are for: not a longer reach,
    since the neck alone would give that, but a quick joint kept near the middle
    of its travel by a slow one.

    It is the first loop in this project to close on the body rather than on the
    world, and the only reading a spiking vehicle could get of it is the 1x10
    propioceptive array of the head's actuators.

    Below the eye's comfortable range it asks for nothing: an eye a few degrees
    off its middle is not worth moving a neck for, and a human's sits there all
    day. What is left after that range is subtracted, and not the whole angle,
    is what it acts on — so at the edge the neck starts from nothing instead of
    lurching into motion.

    With nothing in sight it asks for nothing either. There is no gaze worth
    holding, and moving the neck alone would only sweep it — a search, which
    this is not.
    """

    def __init__(self, kr=RECENTRE_KP, comfort=HEAD_COMFORT_DEG,
                 max_rate=NECK_MAX_RATE_DEG_S, tick_ms=NECK_CONTROL_MS, **kw):
        super().__init__(max_rate=max_rate, tick_ms=tick_ms, **kw)
        self.kr = kr
        self.comfort = comfort

    def off_centre(self, head_deg):
        """How far the eye is outside the range it is content to work in."""
        if abs(head_deg) <= self.comfort:
            return 0.0
        return head_deg - math.copysign(self.comfort, head_deg)

    def rate(self, active_cell, head_deg=0.0):
        if active_cell is None:
            return 0.0
        return self.kr * self.off_centre(head_deg)


class GazeController:
    """Version A of spec 006: one controller per joint, both reading the same eye.

    They do not read the same thing and they do not decide as often. The eye
    reads the retina every 10 ms, the neck reads the head joint's angle every
    20, and both are slower than the body they drive can act — the head's
    fastest effector emits every 2 ms. The neck's interval is a whole number of
    the eye's on purpose: the two decide together, so the reflex below never has
    a stale rate to cancel.

    Each of the three parts has one job. The eye decides where to look and is
    the only thing that sees. The neck decides how the looking is held and is
    the only thing that reads the eye. And the VOR, which is not a controller at
    all but a wire, keeps the second from disturbing the first: a neck that
    moves while the gaze is meant to stay put needs the eye to give way by
    exactly as much, and the eye cannot work that out from what it sees, since
    inside a cell there is no error to see at all. So the eye is handed the
    neck's rate and cancels it — the whole of it, the neck having nothing else
    to say. A real VOR reads a canal, a velocity sensor this vehicle has not
    got; what stands in for it here is a copy of the command.
    """

    def __init__(self, eye=None, neck=None, vor=True):
        self.eye = eye if eye is not None else ProportionalController(
            max_rate=HEAD_MAX_RATE_DEG_S, tick_ms=EYE_CONTROL_MS)
        self.neck = neck if neck is not None else RecentringController()
        self.vor = vor

    def update(self, t, active_cell, head_deg=0.0):
        """The rate to turn each joint at, in degrees per second: head, then neck."""
        neck_rate = self.neck.update(t, active_cell, head_deg)
        eye_rate = self.eye.update(t, active_cell)
        if self.vor:
            eye_rate -= neck_rate
        cap = self.eye.max_rate
        return max(-cap, min(cap, eye_rate)), neck_rate
