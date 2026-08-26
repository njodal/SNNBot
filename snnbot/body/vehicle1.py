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
    def __init__(self, world, rng=None, wired=False):
        self.world = world
        self.retina = Retina()
        self.actuators = {LEFT: Actuator(), RIGHT: Actuator()}
        self.proprioception = {LEFT: ProprioceptiveArray(), RIGHT: ProprioceptiveArray()}
        self.effectors = {
            side: EffectorLayer(side, EFFECTORS, wired=wired, rng=rng)
            for side in (LEFT, RIGHT)
        }

    @property
    def head_deg(self):
        """Positive is turned to the left. Ground truth: the vehicle cannot read it."""
        return DEG_PER_UNIT * (self.actuators[LEFT].level - self.actuators[RIGHT].level)

    def step(self, t):
        """One moment of the vehicle's life. Returns what each part fired."""
        fired = {}

        # the effector layer drives the actuators
        for side, layer in self.effectors.items():
            spikes = layer.update(t)
            if spikes:
                fired[f"effector.{side}"] = spikes
            other = RIGHT if side == LEFT else LEFT
            for _ in spikes:
                self.actuators[side].on_spike(t)
                self.actuators[other].stretched_by(STEP)

        # the sensors report what the body and the world are now
        eye = self.retina.update(t, self.world.object_deg, self.head_deg)
        if eye:
            fired["retina"] = eye
        for side, array in self.proprioception.items():
            spikes = array.update(t, self.actuators[side].level)
            if spikes:
                fired[f"proprioception.{side}"] = spikes
        return fired
