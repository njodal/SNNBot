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
from ..params import CORRELATION_WINDOW_MS, EYE_CELLS, STEERING

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

    def update(self, t, active_cell, eye, layers):
        move = self.moved(t, eye)
        if move is not None:
            self.awake = self.wiring[move]      # the wire out of that very cell
        target = self.awake

        for side, layer in layers.items():
            for index, effector in enumerate(layer.effectors):
                if (side, index) == target:
                    if not effector.emitting:
                        effector.start(t)
                elif effector.emitting:
                    effector.stop(t)

        return [Event(t, move, ON)] if move is not None else []
