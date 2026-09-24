"""Cells that belong to no layer in particular.

The delay cell of [spec 010]: one input, one output, the same spike again later.
It works nothing out. What it is for depends entirely on where it is put — on the
successor of a pair it makes an order out of two things that happened at once, on
the predecessor it makes a coincidence out of two things that did not.

The memory cell, which holds that something happened until it is undone, and
the coincidence cell, which fires when enough of its inputs arrive together.

The sequence cell, which fires when its inputs arrive in the order it names,
each within a window of the one before — a chain of correlation cells folded
into one.
"""

from ..params import REFRACTORY_MS


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


class CoincidenceCell:
    """Fires when enough of its inputs arrive together.

    Together has to mean *within a window*: two tonic sources at the same rate
    fire out of step with each other, and a cell asking for the very same tick
    would wait for ever. Each spike is spent once — the ones that made a
    coincidence are cleared, so two sources at 50 Hz make the cell fire at 50 Hz
    and not at every pairing of an old spike with a new one.

    With two inputs `needed` is both of them, which is the only case built so
    far. With more it is the majority, as spec 010 has it.
    """

    def __init__(self, inputs, window_ms, needed=None, refractory_ms=REFRACTORY_MS):
        self.window_ms = window_ms
        self.needed = inputs // 2 + 1 if needed is None else needed
        self._refractory = refractory_ms
        self._pending = [None] * inputs     # when each input last fired, unspent
        self._last_fired = None

    def reset(self):
        """Nothing pending and nothing just fired: as it was before any time passed."""
        self._pending = [None] * len(self._pending)
        self._last_fired = None

    def update(self, t, arrived=()):
        """Whether it fires now, having been given which inputs just did."""
        for k in arrived:
            self._pending[k] = t
        for k, when in enumerate(self._pending):
            if when is not None and t - when > self.window_ms:
                self._pending[k] = None            # too old to go with anything
        if self._last_fired is not None and t - self._last_fired < self._refractory:
            return False
        if sum(when is not None for when in self._pending) < self.needed:
            return False
        self._pending = [None] * len(self._pending)
        self._last_fired = t
        return True


class SequenceCell:
    """Fires when its inputs arrive in order, each within a window of the last.

    Inputs `0 .. n-1` have to come in that order, and each has to arrive
    between `low` and `high` ms after the one before: closer than `low` is the
    same moment, not an order, and further than `high` is two things that have
    nothing to do with each other. Anything out of order breaks the sequence,
    and input `0` starts it again from the beginning whenever it comes.

    With two inputs this is the correlation cell of spec 010, and with more it
    is a chain of those folded into one: the cell for `(a, b, c)` fires exactly
    when the pair `(a, b)` fed into the pair `(·, c)` would have.

    `primed` is true while every input but the last has arrived in order and
    the window for the last is still open — the cell is waiting for one thing.
    Spec 014 reads that to recall what came next.
    """

    def __init__(self, inputs, low_ms, high_ms):
        self.n = inputs
        self.low, self.high = low_ms, high_ms
        self._at = 0                    # which input it is waiting for
        self._last = None               # when the one before that arrived

    def reset(self):
        """Waiting for the first input, as before anything arrived."""
        self._at, self._last = 0, None

    def _open(self, t):
        return self._last is not None and t - self._last <= self.high

    @property
    def primed(self):
        return self._at == self.n - 1

    def update(self, t, arrived=()):
        """Whether it fires now, having been given which inputs just did."""
        if self._at > 0 and not self._open(t):
            self.reset()                # waited too long for the next one
        for k in sorted(arrived):
            if k == 0:
                self._at, self._last = 1, t
            elif k != self._at:
                self.reset()            # out of order: the sequence is broken
            elif t - self._last < self.low:
                continue                # the same moment, not an order
            elif k == self.n - 1:
                self.reset()
                return True
            else:
                self._at, self._last = k + 1, t
        if self._at > 0 and not self._open(t):
            self.reset()
        return False
