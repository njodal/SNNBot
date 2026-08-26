"""The effector cells of spec 002 and spec 003.

A wired cell emits at its own frequency from a start spike until its duration
runs out, or until a stop spike cuts it short. A cell that is not wired yet is
uncontrolled: it goes off at random and emits for a brief period, which is what
makes the vehicle babble before its cortex has taken hold of it.
"""

from ..events import Event, ON
from ..params import BABBLE_EVERY_MS, TICK_MS


class Effector:
    def __init__(self, name, frequency_hz, duration_ms, wired=False, rng=None,
                 babble_every_ms=BABBLE_EVERY_MS):
        period = 1000 / frequency_hz
        if abs(period - round(period)) > 1e-9 or round(period) % TICK_MS:
            raise ValueError(f"{frequency_hz} Hz is not a whole number of ticks")
        self.name = name
        self.frequency_hz = frequency_hz
        self.duration_ms = duration_ms
        self.wired = wired
        self._period = int(round(period))
        self._rng = rng
        self._babble_every = babble_every_ms
        self._since = None          # when the current emission began
        self._until = None          # when it will end on its own

    @property
    def emitting(self):
        return self._since is not None

    def start(self, t):
        if not self.wired:
            raise RuntimeError("an unwired effector has no start input to spike")
        if not self.emitting:
            self._begin(t, self.duration_ms)

    def stop(self, t):
        if not self.wired:
            raise RuntimeError("an unwired effector has no stop input to spike")
        self._since = self._until = None

    def _begin(self, t, for_ms):
        self._since, self._until = t, t + for_ms

    def update(self, t):
        if not self.emitting and not self.wired:
            if self._rng.random() < TICK_MS / self._babble_every:
                self._begin(t, self.duration_ms)   # a babble lasts what the cell lasts
        if not self.emitting:
            return None
        if t >= self._until:
            self._since = self._until = None
            return None
        if (t - self._since) % self._period:
            return None
        return Event(t, (self.name,), ON)


class EffectorLayer:
    """The effectors attached to one actuator."""

    def __init__(self, actuator_name, specs, wired=False, rng=None):
        self.effectors = [
            Effector(f"{actuator_name}.e{i}", hz, ms, wired=wired, rng=rng)
            for i, (hz, ms) in enumerate(specs, start=1)
        ]

    def update(self, t):
        events = (e.update(t) for e in self.effectors)
        return [e for e in events if e is not None]
