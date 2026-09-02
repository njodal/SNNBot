"""Cells that belong to no layer in particular.

The delay cell of [spec 010]: one input, one output, the same spike again later.
It works nothing out. What it is for depends entirely on where it is put — on the
successor of a pair it makes an order out of two things that happened at once, on
the predecessor it makes a coincidence out of two things that did not.
"""


class DelayCell:
    """The same spike again, later."""

    def __init__(self, delay_ms):
        self.delay_ms = delay_ms
        self._owed = []                 # when the spikes it owes fall due

    def update(self, t, fired=False):
        """Whether it fires now, having been given whether its input just did."""
        if fired:
            self._owed.append(t + self.delay_ms)
        if self._owed and self._owed[0] <= t:
            self._owed.pop(0)
            return True
        return False


class DelayBank:
    """One delay cell per source.

    A delay belongs to the cell that fires rather than to the one that listens,
    so a handful of these serve every cell downstream that wants the same wait.
    """

    def __init__(self, sources, delay_ms):
        self.cells = {source: DelayCell(delay_ms) for source in sources}

    def update(self, t, firing=()):
        """Which sources come out now, having been given which went in."""
        firing = set(firing)
        return [source for source, cell in self.cells.items()
                if cell.update(t, source in firing)]


class MemoryCell:
    """Set by one input, cleared by another, and firing all the while between.

    The counterpart of the delay cell: that one remembers *when* something
    happened, this one remembers *that* it did and has not been undone. Its
    output is the only tonic thing in a project made of changes — which is what
    lets anything downstream be told that a state of affairs is still the case,
    rather than only that it began.
    """

    def __init__(self, rate_hz):
        self._period = 1000 / rate_hz
        self.held = False
        self._next = None

    def update(self, t, set_it=False, clear_it=False):
        """Whether it fires now, having been given what arrived at its inputs."""
        if set_it and not self.held:
            self.held, self._next = True, t
        elif clear_it:
            self.held, self._next = False, None
        if self.held and (self._next is None or t >= self._next):
            self._next = t + self._period
            return True
        return False
