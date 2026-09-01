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

import math

from ..events import Event, ON, OFF
from ..params import (BABBLE_EVERY_MS, CELL_ANGLE_DEG, CORRELATION_MAX_MS,
                      CORRELATION_MIN_MS, DEG_PER_SPIKE, EFFECTORS,
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

    def __init__(self, wiring=None, window=(CORRELATION_MIN_MS, CORRELATION_MAX_MS)):
        self.wiring = correlation_wiring() if wiring is None else wiring
        self.window = window
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
            low, high = self.window
            came_from = [(when, i) for i, when in self._left.items()
                         if i != j and low <= t - when <= high]
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
                 babble_every_ms=BABBLE_EVERY_MS, speed=False,
                 window=(CORRELATION_MIN_MS, CORRELATION_MAX_MS)):
        super().__init__(wiring=correlation_wiring(cells), window=window)
        self.rng, self.lr, self.explore = rng, lr, explore
        self.learning = True        # turned off to see what it has got, not to teach
        self._eligibility_ms, self._babble_every = eligibility_ms, babble_every_ms
        self.actions = [(side, index) for side in (LEFT, RIGHT)
                        for index in range(effectors)]
        # Off by default: over twelve seeds the vehicle does worse with them
        # than without, which is written up in spec 005. They read a speed
        # correctly; there is nothing in this task that wants one.
        self.speed = SpeedLayer(cells) if speed else None
        keys = list(self.wiring) + [(c.pred, c.succ, c.tuned_to)
                                    for c in (self.speed.cells if self.speed else ())]
        self.weights = {key: {act: 0.0 for act in self.actions} for key in keys}
        self._eligible = {}         # (cell, action) -> when it was used
        self._last_pair = None

    def choose(self, *cells):
        """The effector with the most weight behind it, or one to try out.

        Several cells can fire at once — the one that says which way the object
        went, and any that say how fast — so they vote, each adding what it has
        learnt to every effector it has an opinion about.

        Untried is not the same as known to be bad: once anything has been learnt
        it goes with the best there is, even when the best is merely the least
        harmful.
        """
        score = {a: sum(self.weights[c][a] for c in cells) for a in self.actions}
        if not any(score.values()) or self.rng.random() < self.explore:
            return self.rng.choice(self.actions)
        best = max(score.values())
        return self.rng.choice([a for a, w in score.items() if w == best])

    def reinforce(self, t, reward):
        """Credit or blame whatever is still eligible, by what is left of it."""
        if not reward or not self.learning:
            return
        for (cell, action), used in list(self._eligible.items()):
            left = 1 - (t - used) / self._eligibility_ms
            if left <= 0:
                del self._eligible[(cell, action)]
            else:
                w = self.weights[cell][action] + self.lr * reward * left
                self.weights[cell][action] = max(-WEIGHT_MAX, min(WEIGHT_MAX, w))

    def update(self, t, active_cell, eye, layers):
        move = self.moved(t, eye)
        firing = [move] if move is not None else []
        if self.speed is not None:
            firing += [(c.pred, c.succ, c.tuned_to) for c in self.speed.update(t, eye)]

        if firing:
            if move is not None:
                self.reinforce(t, outcome(move))
            self.awake = self.choose(*firing)
            for cell in firing:
                self._eligible[(cell, self.awake)] = t
            self._last_pair = move if move is not None else self._last_pair
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


def speed_bands(cell_angle=CELL_ANGLE_DEG, effectors=EFFECTORS, per_spike=DEG_PER_SPIKE):
    """One band of transit times per speed the body can move the head at.

    A cell of the eye takes `cell_angle / speed` to cross, so each effector of
    spec 003 puts one transit time on the clock. The bands are cut at the
    geometric mean between neighbours, so they tile without overlapping and each
    holds exactly one of those times — the one it is tuned to.
    """
    transits = sorted(cell_angle / (hz * per_spike) * 1000 for hz, _ in effectors)
    cuts = [math.sqrt(a * b) for a, b in zip(transits, transits[1:])]
    edges = [transits[0] / 2] + cuts + [transits[-1] * 2]
    return [(lo, hi, tuned) for (lo, hi), tuned in zip(zip(edges, edges[1:]), transits)]


class SpeedCell:
    """A correlation cell watching two cells of the eye that are not neighbours.

    Its predecessor and successor are a gap apart, so the interval between them
    is not the instant a boundary is crossed but the time taken to cross what
    lies between — which is a speed. Its window says which one.
    """

    def __init__(self, pred, succ, low, high, tuned_to):
        self.pred, self.succ = pred, succ
        self.low, self.high = low, high
        self.tuned_to = tuned_to            # the transit time it is centred on

    @property
    def crossed(self):
        """How many cells of the eye lie between the two it watches."""
        return abs(self.succ - self.pred) - 1

    def speed(self, cell_angle=CELL_ANGLE_DEG):
        """The speed it is tuned to, in degrees a second."""
        return self.crossed * cell_angle / (self.tuned_to / 1000)

    def __repr__(self):
        return f"({self.pred}->{self.succ} @ {self.tuned_to:.0f} ms)"


class SpeedLayer:
    """The cells of the layer that report how fast, rather than where to.

    One per ordered pair with a gap in it, per band. They fire on the same
    events as the cells that report direction and are told apart from them only
    by what they are wired to and how long they are willing to wait.
    """

    def __init__(self, cells=EYE_CELLS, bands=None):
        bands = speed_bands() if bands is None else bands
        self.cells = [SpeedCell(i, j, lo, hi, tuned)
                      for j in range(1, cells + 1)
                      for i in range(1, cells + 1) if abs(i - j) > 1
                      for lo, hi, tuned in bands]
        self._left = {}

    def update(self, t, eye):
        """Which of them just fired, if any."""
        for event in eye:
            if event.p is OFF:
                self._left[event.address[0]] = t
        fired = []
        for event in eye:
            if event.p is not ON:
                continue
            for cell in self.cells:
                if cell.succ != event.address[0]:
                    continue
                when = self._left.get(cell.pred)
                if when is not None and cell.low <= t - when <= cell.high:
                    fired.append(cell)
        return fired
