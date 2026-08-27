"""The actuator of spec 003: it moves one step per spike, one way only.

It has no input other than spikes. Relaxing releases the tension, it does not
undo the movement, so the contraction level is untouched by it.
"""

from ..params import CONTRACTION_MAX, CONTRACTION_MIN, CONTRACTION_REST, RELAX_MS, STEP


class Actuator:
    def __init__(self, level=CONTRACTION_REST, step=STEP, relax_ms=RELAX_MS):
        self.level = level
        self._step = step
        self._relax_ms = relax_ms
        self._last_spike_t = None

    def on_spike(self, t):
        """One spike, one step, always in the same direction."""
        self.contract_by(t, self._step)

    def contract_by(self, t, amount):
        """Contract by an arbitrary amount, for a controller that is not spiking."""
        self.level = min(CONTRACTION_MAX, self.level + amount)
        self._last_spike_t = t

    def stretched_by(self, other_step):
        """Pulled the other way by the antagonist. Nothing it does itself."""
        self.level = max(CONTRACTION_MIN, self.level - other_step)

    def relaxed(self, t):
        return self._last_spike_t is None or t - self._last_spike_t >= self._relax_ms
