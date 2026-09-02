"""Vehicle 2 of spec 006: the eye of Vehicle 1, carried on a neck.

Two joints now, each with an antagonist pair of its own, and what the eye ends
up looking at is the sum of the two angles. The retina is handed that sum and
nothing else, which is the whole difficulty of this vehicle: nothing it sees
says which joint moved.
"""

from ..layers.effector import EffectorLayer
from ..params import (HEAD_DEG_PER_UNIT, HEAD_EFFECTORS, NECK_DEG_PER_UNIT,
                      NECK_EFFECTORS, STEP)
from ..events import ON, Event
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


class Gain:
    """One spike in, so many out: an integrator that fires whenever it is full.

    The neck and the head are not worth the same per spike — 1.6 degrees against
    0.9 — so a wire between them cannot be one for one, and a spike cannot be cut
    in half. What can be done is what a cell does anyway: add the weight up and
    fire whenever the total has come to one.
    """

    def __init__(self, gain):
        self.gain = gain
        self._charge = 0.0

    def spikes(self, arriving):
        self._charge += arriving * self.gain
        whole = int(self._charge)
        self._charge -= whole
        return whole


class Vehicle2:
    """The body, and whatever drives it.

    With no controller both joints are driven by their own effector layers,
    which babble while they are unwired. Given one — Version A of spec 006 —
    the effectors step aside and the controller turns each joint directly.
    """

    def __init__(self, world, rng=None, wired=False, controller=None,
                 eye_reflex=None, neck_reflex=None, vor=False):
        self.world = world
        self.controller = controller
        self.eye_reflex, self.neck_reflex = eye_reflex, neck_reflex
        wired = wired or eye_reflex is not None or neck_reflex is not None
        self._last_eye, self._last_sense = [], []
        # The reflex arc of spec 006: the neck's effectors reach the eye's, so
        # that a neck that moves is given way to before anything has to see it.
        self.vor = Gain(NECK_DEG_PER_UNIT / HEAD_DEG_PER_UNIT) if vor else None
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

        driven = list(self.joints)      # the joints their own effectors move
        if self.controller is not None:
            # Version A: the controller reads the active cell as a number and
            # turns the joints itself. No effector fires, no spike is involved.
            # A joint that has a layer of its own is left to it — which is how a
            # spiking neck gets to be tried against an eye known to work.
            head_rate, neck_rate = self.controller.update(
                t, self.retina.busy_cell(), self.head_deg)
            self.head.turn(t, head_rate * elapsed / 1000)
            driven = []
            if self.neck_reflex is None:
                self.neck.turn(t, neck_rate * elapsed / 1000)
            else:
                driven = [self.neck]

        # Version B: a layer of its own on each joint, reading different things.
        # The eye's is wired to the retina, the neck's to the propioceptive array
        # of the head — so what the neck learns about is where the eye is sitting.
        if self.eye_reflex is not None:
            sensed = self.eye_reflex.update(t, self.retina.busy_cell(),
                                            self._last_eye, self.head.effectors)
            if sensed:
                fired["sensory.eye"] = sensed
        if self.neck_reflex is not None:
            sensed = self.neck_reflex.update(t, None, self._last_sense,
                                             self.neck.effectors)
            if sensed:
                fired["sensory.neck"] = sensed

        for joint in driven:
            fired.update(joint.driven_by_spikes(t))

        if self.vor is not None:
            for side in (LEFT, RIGHT):
                arriving = len(fired.get(f"effector.{NECK}.{side}", ()))
                if not arriving:
                    continue
                # give way the other way round: a neck turning left needs an eye
                # turning right by as much, and the gaze does not move at all
                gives, holds = (RIGHT, LEFT) if side == LEFT else (LEFT, RIGHT)
                spikes = self.vor.spikes(arriving)
                for _ in range(spikes):
                    self.head.actuators[gives].on_spike(t)
                    self.head.actuators[holds].stretched_by(STEP)
                if spikes:
                    fired.setdefault("vor", []).extend(
                        Event(t, (gives,), ON) for _ in range(spikes))

        for reflex, name in ((self.eye_reflex, HEAD), (self.neck_reflex, NECK)):
            if reflex is not None:
                reflex.spent(sum(len(s) for k, s in fired.items()
                                 if k.startswith(f"effector.{name}")))
        return self._sense(t, fired)

    def _sense(self, t, fired):
        """What the body and the world are now, as spikes."""
        eye = self.retina.update(t, self.world.object_deg, self.gaze_deg)
        self._last_eye = eye            # what the correlation cells read next moment
        if eye:
            fired["retina"] = eye
        for joint in self.joints:
            fired.update(joint.sense(t))
        # The neck's layer reads one of the head's two arrays. The other is its
        # mirror — the pair being antagonists — so it would say the same thing
        # backwards and double the cells for nothing.
        self._last_sense = fired.get(f"proprioception.{HEAD}.{LEFT}", [])
        return fired
