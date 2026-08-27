"""Vehicle 1 of spec 005: one eye, two actuators that turn it, nothing else.

The body has a single degree of freedom. The two actuators are antagonists
sharing one anchor, so contracting one stretches the other, and the head angle
follows from the imbalance between the two contractions.
"""

from ..events import Event
from ..params import CONTRACTION_REST, DEG_PER_UNIT, EFFECTORS, STEP
from ..layers.effector import EffectorLayer
from .actuator import Actuator
from .proprioception import ProprioceptiveArray
from .retina import Retina

LEFT, RIGHT = "left", "right"


class Vehicle1:
    """The body, and whatever drives it.

    With no controller it is driven by its own effector layers, which babble
    while they are unwired. Given one — Version A of spec 005 — the effectors
    step aside and the controller turns the head directly.
    """

    def __init__(self, world, rng=None, wired=False, controller=None):
        self.world = world
        self.controller = controller
        self._last_t = None
        self.retina = Retina()
        self.actuators = {LEFT: Actuator(), RIGHT: Actuator()}
        self.proprioception = {LEFT: ProprioceptiveArray(), RIGHT: ProprioceptiveArray()}
        self.effectors = {
            side: EffectorLayer(side, EFFECTORS, wired=wired, rng=rng)
            for side in (LEFT, RIGHT)
        }

    def turn(self, degrees):
        """Turn the head, by contracting one actuator and stretching the other."""
        d = degrees / (2 * DEG_PER_UNIT)
        near, far = (LEFT, RIGHT) if d >= 0 else (RIGHT, LEFT)
        self.actuators[near].contract_by(self._last_t, abs(d))
        self.actuators[far].stretched_by(abs(d))

    @property
    def head_deg(self):
        """Positive is turned to the left. Ground truth: the vehicle cannot read it."""
        return DEG_PER_UNIT * (self.actuators[LEFT].level - self.actuators[RIGHT].level)

    def step(self, t):
        """One moment of the vehicle's life. Returns what each part fired."""
        fired = {}
        elapsed, self._last_t = 0 if self._last_t is None else t - self._last_t, t

        if self.controller is not None:
            # Version A: the controller reads the active cell as a number and
            # turns the head itself. No effector fires, no spike is involved.
            rate = self.controller.update(t, self.retina.busy_cell())
            self.turn(rate * elapsed / 1000)
            return self._sense(t, fired)

        # the effector layer drives the actuators
        for side, layer in self.effectors.items():
            spikes = layer.update(t)
            if spikes:
                fired[f"effector.{side}"] = spikes
            other = RIGHT if side == LEFT else LEFT
            for _ in spikes:
                self.actuators[side].on_spike(t)
                self.actuators[other].stretched_by(STEP)

        return self._sense(t, fired)

    def _sense(self, t, fired):
        """What the body and the world are now, as spikes."""
        eye = self.retina.update(t, self.world.object_deg, self.head_deg)
        if eye:
            fired["retina"] = eye
        for side, array in self.proprioception.items():
            spikes = array.update(t, self.actuators[side].level)
            if spikes:
                fired[f"proprioception.{side}"] = spikes
        return fired
