"""The eye of spec 005: a 1xN row of change based cells (spec 001).

A cell is busy when the object falls inside the slice of the world it looks at,
and empty otherwise. Going from empty to busy fires ON, the other way OFF.

Every cell works out its own occupancy from the object and the head angle and
looks at nothing else, so no cell needs another cell's state.

Both are reported the instant they happen. The two events of a move therefore
carry the same time, the object leaving one cell exactly as it reaches the next,
and putting them in an order is the job of a delay cell downstream — of whatever
wants the order, rather than of the eye, which should not be shading when it saw
something to suit what comes after.
"""

from ..events import Event, ON, OFF
from ..params import CELL_ANGLE_DEG, EYE_CELLS, SETTLE_MS, T_REF_MS


class Cell:
    def __init__(self, index, cells, cell_angle, t_ref_ms, settle_ms=0):
        self.index = index
        self._offset = ((cells + 1) / 2 - index) * cell_angle   # degrees left of the head
        self._half = cell_angle / 2
        self._t_ref = t_ref_ms
        self._settle = settle_ms    # how long a thing must stay before it counts
        self._since = None          # when it arrived, if it has
        self.occupied = False       # where the object really is
        self.busy = False           # what it has said about that
        self._last_t = None

    def looks_at(self, head_deg):
        """The direction of the world this cell is pointing at right now."""
        return head_deg + self._offset

    def _spike(self, t, polarity):
        if self._last_t is not None and t - self._last_t < self._t_ref:
            return None             # still busy with the previous spike
        self._last_t = t
        self.busy = polarity is ON
        return Event(t, (self.index,), polarity)

    def update(self, t, object_deg, head_deg):
        # Half open, so that the cells tile the world without sharing their
        # edges. Were the edge to belong to both, an object crossing it would be
        # in two cells for an instant, the cell it is reaching would report
        # before the cell it is leaving, and the lag below would do no more than
        # cancel that head start out.
        away = object_deg - self.looks_at(head_deg)
        self.occupied = -self._half <= away < self._half
        if not self.occupied:
            self._since = None
            return self._spike(t, OFF) if self.busy else None
        if self.busy:
            return None
        if self._since is None:
            self._since = t
        # A cell that needs a moment to be sure is not a cell lying about when it
        # saw something. What it will not report is anything gone before it settled.
        return self._spike(t, ON) if t - self._since >= self._settle else None


class Retina:
    def __init__(self, cells=EYE_CELLS, cell_angle=CELL_ANGLE_DEG, t_ref_ms=T_REF_MS,
                 settle_ms=SETTLE_MS):
        self.cells = [Cell(i, cells, cell_angle, t_ref_ms, settle_ms)
                      for i in range(1, cells + 1)]

    def update(self, t, object_deg, head_deg):
        events = (c.update(t, object_deg, head_deg) for c in self.cells)
        return [e for e in events if e is not None]

    def busy_cell(self):
        """Which cell the object is on, read as a number the way Version A does.

        This is the occupancy itself, not what the spiking cells have reported.
        Nothing spiking may ask for it.
        """
        for c in self.cells:
            if c.occupied:
                return c.index
        return None
