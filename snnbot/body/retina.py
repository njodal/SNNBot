"""The eye of spec 005: a 1xN row of change based cells (spec 001).

A cell is busy when the object falls inside the slice of the world it looks at,
and empty otherwise. Going from empty to busy fires ON, the other way OFF.

Every cell works out its own occupancy from the object and the head angle and
looks at nothing else, so no cell needs another cell's state.

A cell reports becoming busy one cycle after it happens, and becoming empty at
once. Without that gap the two events of a move carry the same time — the object
leaves one cell in the very instant it reaches the next — and there is no order
left for anything downstream to read. With it, a move is always an OFF followed
by an ON, which is what specs 001 and 005 have described all along.
"""

from ..events import Event, ON, OFF
from ..params import CELL_ANGLE_DEG, EYE_CELLS, ON_LAG_MS, T_REF_MS


class Cell:
    def __init__(self, index, cells, cell_angle, t_ref_ms, on_lag_ms):
        self.index = index
        self._offset = ((cells + 1) / 2 - index) * cell_angle   # degrees left of the head
        self._half = cell_angle / 2
        self._t_ref = t_ref_ms
        self._on_lag = on_lag_ms
        self.occupied = False       # where the object really is
        self.busy = False           # what the cell has got round to saying
        self._due = None            # when the ON it owes falls due
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
            self._due = None        # it left before the ON was ever due
            return self._spike(t, OFF) if self.busy else None

        if not self.busy and self._due is None:
            self._due = t + self._on_lag
        if self._due is not None and t >= self._due:
            self._due = None
            return self._spike(t, ON)
        return None


class Retina:
    def __init__(self, cells=EYE_CELLS, cell_angle=CELL_ANGLE_DEG, t_ref_ms=T_REF_MS,
                 on_lag_ms=ON_LAG_MS):
        self.cells = [Cell(i, cells, cell_angle, t_ref_ms, on_lag_ms)
                      for i in range(1, cells + 1)]

    def update(self, t, object_deg, head_deg):
        events = (c.update(t, object_deg, head_deg) for c in self.cells)
        return [e for e in events if e is not None]

    def busy_cell(self):
        """Which cell the object is on, read as a number the way Version A does.

        This is the occupancy itself, not what the spiking cells have reported,
        so it does not wait for the lag. Nothing spiking may ask for it.
        """
        for c in self.cells:
            if c.occupied:
                return c.index
        return None
