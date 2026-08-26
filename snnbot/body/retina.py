"""The eye of spec 005: a 1xN row of change based cells (spec 001).

A cell is busy when the object falls inside the slice of the world it looks at,
and empty otherwise. Going from empty to busy fires ON, the other way OFF.

Every cell works out its own occupancy from the object and the head angle and
looks at nothing else, so no cell needs another cell's state.
"""

from ..events import Event, ON, OFF
from ..params import CELL_ANGLE_DEG, EYE_CELLS, T_REF_MS


class Cell:
    def __init__(self, index, cells, cell_angle, t_ref_ms):
        self.index = index
        self._offset = ((cells + 1) / 2 - index) * cell_angle   # degrees left of the head
        self._half = cell_angle / 2
        self._t_ref = t_ref_ms
        self.busy = False
        self._last_t = None

    def looks_at(self, head_deg):
        """The direction of the world this cell is pointing at right now."""
        return head_deg + self._offset

    def update(self, t, object_deg, head_deg):
        busy = abs(object_deg - self.looks_at(head_deg)) <= self._half
        if busy == self.busy:
            return None
        if self._last_t is not None and t - self._last_t < self._t_ref:
            return None                      # still busy with the previous spike
        self.busy = busy
        self._last_t = t
        return Event(t, (self.index,), ON if busy else OFF)


class Retina:
    def __init__(self, cells=EYE_CELLS, cell_angle=CELL_ANGLE_DEG, t_ref_ms=T_REF_MS):
        self.cells = [Cell(i, cells, cell_angle, t_ref_ms) for i in range(1, cells + 1)]

    def update(self, t, object_deg, head_deg):
        events = (c.update(t, object_deg, head_deg) for c in self.cells)
        return [e for e in events if e is not None]

    def busy_cell(self):
        """Which cell is occupied, for the observer. The vehicle cannot ask this."""
        for c in self.cells:
            if c.busy:
                return c.index
        return None
