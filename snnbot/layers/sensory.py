"""The sensory layer of [spec 002].

Version B of [spec 005] uses the plainest one there could be: a cell per cell of
the eye, each wired straight to an effector, with nothing in between. No cortex,
no learning — what the vehicle does is what the wiring makes it do.

The wiring is forced by the task. A cell to the left of the middle means the
object is to the left, so the head has to turn left, and the further from the
middle the cell is the further the head has to go — so the further out the cell,
the faster the effector it wakes. The middle cell wakes nothing: there is
nowhere to go from there.
"""

from ..events import Event, ON, OFF
from ..params import (BABBLE_EVERY_MS, CORRELATION_WINDOW_MS, EFFECTORS,
                      ELIGIBILITY_MS, EXPLORE, EYE_CELLS, LEARNING_RATE,
                      STEERING, TICK_MS, WEIGHT_MAX)

LEFT, RIGHT = "left", "right"


def wiring(cells=EYE_CELLS, effectors=len(STEERING)):
    """Which effector each cell of the eye reaches: {cell: (side, index)}.

    Index 0 is the fastest effector, so the outermost cell gets it.
    """
    middle = (cells + 1) // 2
    return {
        cell: (LEFT if cell < middle else RIGHT, effectors - abs(cell - middle))
        for cell in range(1, cells + 1) if cell != middle
    }


class Reflex:
    """Sensory layer and effector layer, hard wired to each other."""

    def __init__(self, wiring=None):
        self.wiring = wiring if wiring is not None else globals()["wiring"]()
        self.awake = None                   # the one effector left running

    def update(self, t, active_cell, eye, layers):
        """Wake the effector this cell reaches, and let no other one run.

        The effector layer is meant to inhibit its own cells laterally so that
        only the last one woken stays active. Rather than wire that up, the same
        thing is done here by simply not letting the others run.
        """
        target = self.wiring.get(active_cell)
        for side, layer in layers.items():
            for index, effector in enumerate(layer.effectors):
                if (side, index) == target:
                    if not effector.emitting:
                        effector.start(t)
                elif effector.emitting:
                    effector.stop(t)

        if target == self.awake:
            return []
        self.awake = target
        return [] if active_cell is None else [Event(t, (active_cell,), ON)]


def correlation_wiring(cells=EYE_CELLS, effectors=len(STEERING)):
    """One wire per correlation cell: {(predecessor, successor): (side, index)}.

    Seventy two entries, one for every cell of the layer, because it is the
    correlation cells that reach the effectors and nothing else does. Several
    of them name the same effector, which is allowed — any one is enough to
    wake it. What fills the table is a rule for now; there is nothing stopping
    an entry from being set on its own.
    """
    by_cell = wiring(cells, effectors)
    middle, gentlest = (cells + 1) // 2, effectors     # the one past the ladder

    def wire(i, j):
        if j != middle:
            return by_cell[j]
        # Arriving at the middle. Stopping dead here is what leaves the object
        # drifting straight back out of it, so instead go on the way it was
        # going, at the gentlest speed there is: a cell reached from the left
        # was reached by turning left, and the other way round.
        return (LEFT, gentlest) if i < middle else (RIGHT, gentlest)

    return {(i, j): wire(i, j)
            for j in range(1, cells + 1)
            for i in range(1, cells + 1) if i != j}


class CorrelationReflex:
    """Version C's sensory layer: a cell per ordered pair of cells of the eye.

    Each one has a predecessor input, wired to a cell of the eye reporting that
    it has gone empty, and a successor input wired to another cell reporting
    that it has gone busy. It fires only when the predecessor arrives first, so
    it says not where the object is but that it *moved*, and which way.

    There is one for every ordered pair, 72 of them, and several share an
    effector: they all name the same place to go, having arrived from different
    places. Any one of them is enough to wake it.
    """

    def __init__(self, wiring=None, window_ms=CORRELATION_WINDOW_MS):
        self.wiring = correlation_wiring() if wiring is None else wiring
        self.window = window_ms
        self.awake = None
        self._left = {}                 # cell -> when it reported going empty

    def cells(self):
        """The pairs there is a cell for: 9 successors by 8 predecessors."""
        return list(self.wiring)

    def moved(self, t, eye):
        """Which pair, if any, just fired. The successor is what arrives last."""
        for event in eye:
            if event.p is OFF:
                self._left[event.address[0]] = t
        for event in eye:
            if event.p is not ON:
                continue
            j = event.address[0]
            came_from = [(when, i) for i, when in self._left.items()
                         if i != j and 0 < t - when <= self.window]
            if came_from:
                return max(came_from)[1], j     # the most recent one it left
        return None

    def drive(self, t, layers, target):
        """Wake that one and let no other run. Started once, not held on.

        An effector runs its own course and stops by itself, as spec 003 has it.
        Restarting it for as long as nothing else has happened is how a vehicle
        ends up leaning on its own stop for ever, having last been told to turn
        and never told anything since.
        """
        for side, layer in layers.items():
            for index, effector in enumerate(layer.effectors):
                if (side, index) == target:
                    effector.start(t)
                elif effector.emitting:
                    effector.stop(t)

    def update(self, t, active_cell, eye, layers):
        move = self.moved(t, eye)
        if move is not None:
            self.awake = self.wiring[move]      # the wire out of that very cell
            self.drive(t, layers, self.awake)
        return [Event(t, move, ON)] if move is not None else []


def outcome(pair, cells=EYE_CELLS):
    """What a correlation cell means for the vehicle: better, worse or neither.

    A cell is wired to two cells of the eye and that alone settles it — whether
    the object it watched move ended up nearer the middle than it started. No
    measurement, nothing worked out while running: a fixed property of the cell,
    decided when the layer is built. Of the 72, thirty two mean better, thirty
    two mean worse, and eight mean neither, being the ones that cross over.
    """
    i, j, middle = pair[0], pair[1], (cells + 1) // 2
    return (abs(i - middle) > abs(j - middle)) - (abs(i - middle) < abs(j - middle))


class LearningReflex(CorrelationReflex):
    """Version D of [spec 005]: the same cells, with the wiring left to be found.

    Every correlation cell reaches every effector, through a weight rather than
    a wire. What fires is the effector with the most weight behind it, unless
    the vehicle is exploring, and while no weight is worth anything it explores
    all the time — which is the babbling of [spec 002] arriving at the same
    behaviour by a different road.

    The connection last used is left eligible for a while. When a cell fires it
    says, by which cell it is, whether things got better or worse, and whatever
    is still eligible is credited or blamed accordingly.
    """

    def __init__(self, rng, cells=EYE_CELLS, effectors=len(EFFECTORS),
                 lr=LEARNING_RATE, eligibility_ms=ELIGIBILITY_MS, explore=EXPLORE,
                 babble_every_ms=BABBLE_EVERY_MS, window_ms=CORRELATION_WINDOW_MS):
        super().__init__(wiring=correlation_wiring(cells), window_ms=window_ms)
        self.rng, self.lr, self.explore = rng, lr, explore
        self.learning = True        # turned off to see what it has got, not to teach
        self._eligibility_ms, self._babble_every = eligibility_ms, babble_every_ms
        self.actions = [(side, index) for side in (LEFT, RIGHT)
                        for index in range(effectors)]
        self.weights = {pair: {act: 0.0 for act in self.actions} for pair in self.wiring}
        self._eligible = {}         # (pair, action) -> when it was used
        self._last_pair = None

    def choose(self, pair):
        """The effector with the most weight behind it, or one to try out.

        Untried is not the same as known to be bad: once a cell has learnt
        anything at all it goes with the best it has, even when the best it has
        is merely the least harmful.
        """
        weights = self.weights[pair]
        untried = not any(weights.values())
        if untried or self.rng.random() < self.explore:
            return self.rng.choice(self.actions)
        best = max(weights.values())
        return self.rng.choice([a for a, w in weights.items() if w == best])

    def reinforce(self, t, reward):
        """Credit or blame whatever is still eligible, by what is left of it."""
        if not reward or not self.learning:
            return
        for (pair, action), used in list(self._eligible.items()):
            left = 1 - (t - used) / self._eligibility_ms
            if left <= 0:
                del self._eligible[(pair, action)]
            else:
                w = self.weights[pair][action] + self.lr * reward * left
                self.weights[pair][action] = max(-WEIGHT_MAX, min(WEIGHT_MAX, w))

    def update(self, t, active_cell, eye, layers):
        move = self.moved(t, eye)
        if move is not None:
            self.reinforce(t, outcome(move))
            self.awake = self.choose(move)
            self._eligible[(move, self.awake)] = t
            self._last_pair = move
            self.drive(t, layers, self.awake)
        elif not any(e.emitting for layer in layers.values() for e in layer.effectors):
            # nothing to go on and nothing running: try something, which is what
            # an effector with nothing convincing behind it does anyway
            if self.rng.random() < TICK_MS / self._babble_every:
                self.awake = self.rng.choice(self.actions)
                if self._last_pair is not None:
                    self._eligible[(self._last_pair, self.awake)] = t
                self.drive(t, layers, self.awake)

        return [Event(t, move, ON)] if move is not None else []
