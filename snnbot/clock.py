"""The tick, and the only place that knows there is one.

Spec 004: components are handed a time, never a tick index, so that the grid
stays out of every interface and can be made finer here alone.
"""

from .params import TICK_MS


class Clock:
    def __init__(self, tick_ms=TICK_MS):
        self.tick_ms = tick_ms
        self.t = 0

    def times(self, duration_ms):
        """Yield the time at each step, in milliseconds."""
        end = self.t + duration_ms
        while self.t < end:
            yield self.t
            self.t += self.tick_ms
