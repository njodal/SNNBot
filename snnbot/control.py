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
"""

from .params import CELL_ANGLE_DEG, CONTROL_TICK_MS, EYE_CELLS, KP, MAX_TURN_RATE


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
