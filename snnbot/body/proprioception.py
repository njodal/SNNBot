"""The contraction sensor of spec 001, example II: N threshold based sensors.

The ranges do not overlap and cover the whole span, so exactly one sensor is
firing at a time and which one it is *is* the reading. Unlike the eye, it keeps
firing while the level stays where it is.

They are half open, each taking its lower edge and leaving the upper one to the
next, which is the same convention the cells of the eye are tiled with and for
the same reason: a level has to belong to exactly one of them. Whole numbered
edges with a unit between them left a tenth of the span read by nobody, which
nothing noticed while every actuator moved in whole steps.
"""

from ..events import Event, ON, OFF
from ..params import CONTRACTION_MAX, PROP_RATE_HZ, PROP_SENSORS


class Sensor:
    def __init__(self, index, lo, hi, period_ms, top=False):
        self.index, self.lo, self.hi = index, lo, hi
        self._period = period_ms
        self._top = top             # the last one keeps its upper edge: nothing is above it
        self._next_t = None

    def holds(self, level):
        if self._top:
            return self.lo <= level <= self.hi
        return self.lo <= level < self.hi

    def update(self, t, level):
        if not self.holds(level):
            was_firing, self._next_t = self._next_t is not None, None
            return Event(t, (self.index,), OFF) if was_firing else None
        if self._next_t is None:                    # just came into range
            self._next_t = t + self._period
            return Event(t, (self.index,), ON)
        if t >= self._next_t:
            self._next_t = t + self._period
            return Event(t, (self.index,), ON)
        return None


class ProprioceptiveArray:
    def __init__(self, sensors=PROP_SENSORS, span=CONTRACTION_MAX, rate_hz=PROP_RATE_HZ):
        period = 1000 // rate_hz
        width = span // sensors
        self.sensors = [
            Sensor(i, (i - 1) * width, i * width, period, top=i == sensors)
            for i in range(1, sensors + 1)
        ]

    def update(self, t, level):
        events = (s.update(t, level) for s in self.sensors)
        return [e for e in events if e is not None]

    def firing(self):
        """Which sensor is in range, for the observer."""
        return next((s.index for s in self.sensors if s._next_t is not None), None)
