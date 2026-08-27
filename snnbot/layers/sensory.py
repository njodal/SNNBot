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

from ..events import Event, ON
from ..params import EFFECTORS, EYE_CELLS

LEFT, RIGHT = "left", "right"


def wiring(cells=EYE_CELLS, effectors=len(EFFECTORS)):
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

    def update(self, t, active_cell, layers):
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
