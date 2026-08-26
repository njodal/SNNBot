"""The contraction sensor of spec 001, example II: N threshold based sensors.

The ranges do not overlap and cover the whole span, so exactly one sensor is
firing at a time and which one it is *is* the reading. Unlike the eye, it keeps
firing while the level stays where it is.
"""

from ..events import Event, ON, OFF
from ..params import CONTRACTION_MAX, PROP_RATE_HZ, PROP_SENSORS


class Sensor:
    def __init__(self, index, lo, hi, period_ms):
        self.index, self.lo, self.hi = index, lo, hi
        self._period = period_ms
        self._next_t = None

    def holds(self, level):
        return self.lo <= level <= self.hi

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
            Sensor(i, 0 if i == 1 else (i - 1) * width + 1, i * width, period)
            for i in range(1, sensors + 1)
        ]

    def update(self, t, level):
        events = (s.update(t, level) for s in self.sensors)
        return [e for e in events if e is not None]

    def firing(self):
        """Which sensor is in range, for the observer."""
        return next((s.index for s in self.sensors if s._next_t is not None), None)
