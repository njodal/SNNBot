"""Vehicle 2 of spec 006: the eye of Vehicle 1, carried on a neck.

Two joints now, each with an antagonist pair of its own, and what the eye ends
up looking at is the sum of the two angles. The retina is handed that sum and
nothing else, which is the whole difficulty of this vehicle: nothing it sees
says which joint moved.
"""

from ..layers.effector import EffectorLayer
from ..params import (HEAD_DEG_PER_UNIT, HEAD_EFFECTORS, NECK_DEG_PER_UNIT,
                      NECK_EFFECTORS, STEP)
from .actuator import Actuator
from .proprioception import ProprioceptiveArray
from .retina import Retina

LEFT, RIGHT = "left", "right"
HEAD, NECK = "head", "neck"


class Joint:
    """A pair of antagonists, and the angle their imbalance comes to.

    The pair is Vehicle 1's, twice over. What differs between the two joints is
    what one unit of imbalance is worth in degrees: out of the same contraction
    range of spec 003, the head gets ±45 degrees and the neck ±80.
    """

    def __init__(self, name, deg_per_unit, effectors, wired=False, rng=None):
        self.name = name
        self.deg_per_unit = deg_per_unit
        self.actuators = {LEFT: Actuator(), RIGHT: Actuator()}
        self.proprioception = {LEFT: ProprioceptiveArray(),
                               RIGHT: ProprioceptiveArray()}
        self.effectors = {
            side: EffectorLayer(f"{name}.{side}", effectors, wired=wired, rng=rng)
            for side in (LEFT, RIGHT)
        }

    @property
    def deg(self):
        """Positive is turned to the left. Ground truth: the vehicle cannot read it."""
        return self.deg_per_unit * (self.actuators[LEFT].level
                                    - self.actuators[RIGHT].level)

    def turn(self, t, degrees):
        """Turn it, by contracting one actuator and stretching the other."""
        d = degrees / (2 * self.deg_per_unit)
        near, far = (LEFT, RIGHT) if d >= 0 else (RIGHT, LEFT)
        self.actuators[near].contract_by(t, abs(d))
        self.actuators[far].stretched_by(abs(d))

    def driven_by_spikes(self, t):
        """One moment of its effector layers, and of the actuators they drive."""
        fired = {}
        for side, layer in self.effectors.items():
            spikes = layer.update(t)
            if spikes:
                fired[f"effector.{self.name}.{side}"] = spikes
            other = RIGHT if side == LEFT else LEFT
            for _ in spikes:
                self.actuators[side].on_spike(t)
                self.actuators[other].stretched_by(STEP)
        return fired

    def sense(self, t):
        """What its two contraction levels are, as spikes."""
        fired = {}
        for side, array in self.proprioception.items():
            spikes = array.update(t, self.actuators[side].level)
            if spikes:
                fired[f"proprioception.{self.name}.{side}"] = spikes
        return fired


class Vehicle2:
    """The body, and whatever drives it.

    With no controller both joints are driven by their own effector layers,
    which babble while they are unwired. Given one — Version A of spec 006 —
    the effectors step aside and the controller turns each joint directly.
    """

    def __init__(self, world, rng=None, wired=False, controller=None):
        self.world = world
        self.controller = controller
        self._last_t = None
        self.retina = Retina()
        self.head = Joint(HEAD, HEAD_DEG_PER_UNIT, HEAD_EFFECTORS, wired=wired, rng=rng)
        self.neck = Joint(NECK, NECK_DEG_PER_UNIT, NECK_EFFECTORS, wired=wired, rng=rng)
        self.joints = (self.head, self.neck)

    @property
    def head_deg(self):
        return self.head.deg

    @property
    def neck_deg(self):
        return self.neck.deg

    @property
    def gaze_deg(self):
        """Where the eye is looking. The two angles add, and only the sum is seen."""
        return self.head.deg + self.neck.deg

    def step(self, t):
        """One moment of the vehicle's life. Returns what each part fired."""
        fired = {}
        elapsed, self._last_t = 0 if self._last_t is None else t - self._last_t, t

        if self.controller is not None:
            # Version A: the controller reads the active cell as a number and
            # turns both joints itself. No effector fires, no spike is involved.
            head_rate, neck_rate = self.controller.update(
                t, self.retina.busy_cell(), self.head_deg)
            self.head.turn(t, head_rate * elapsed / 1000)
            self.neck.turn(t, neck_rate * elapsed / 1000)
            return self._sense(t, fired)

        for joint in self.joints:
            fired.update(joint.driven_by_spikes(t))
        return self._sense(t, fired)

    def _sense(self, t, fired):
        """What the body and the world are now, as spikes."""
        eye = self.retina.update(t, self.world.object_deg, self.gaze_deg)
        if eye:
            fired["retina"] = eye
        for joint in self.joints:
            fired.update(joint.sense(t))
        return fired
