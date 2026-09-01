"""The eye. Criteria from spec 001 and the worked pair of spec 005."""

from snnbot.body.retina import Retina
from snnbot.events import OFF, ON
from snnbot.params import SETTLE_MS, T_REF_MS, TICK_MS

AT_REST, TURNED_LEFT = 0.0, 18.0
OBJECT = 18.0                      # degrees left of ahead, as drawn in spec 005


def stream(retina, steps):
    out = []
    for t, object_deg, head_deg in steps:
        out += [(t, e) for e in retina.update(t, object_deg, head_deg)]
    return out


def test_the_object_at_rest_is_seen_by_cell_3():
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    assert r.busy_cell() == 3


def test_turning_the_head_slides_the_object_to_cell_5():
    """Spec 004: the pair of pictures of spec 005 is reproducible.

    A cell says it has gone empty at once and that it has filled once it is sure,
    and being sure takes the same moment for every cell — so the two events of a
    move still arrive together, and putting them in an order is a delay cell's
    job further along.
    """
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    assert [str(e) for e in r.update(SETTLE_MS, OBJECT, AT_REST)] == ["3 on"]
    r.update(1000, OBJECT, TURNED_LEFT)
    assert [str(e) for e in r.update(1000, OBJECT, TURNED_LEFT)] == []
    assert r.busy_cell() == 5


def test_the_cells_never_share_an_edge():
    """An object exactly on a boundary is in one cell, never in two."""
    r = Retina()
    for boundary in (4.5, 13.5, 22.5, -4.5, -13.5):
        r.update(0, boundary, AT_REST)
        assert sum(c.occupied for c in r.cells) == 1


def test_a_move_leaves_one_cell_and_reaches_the_next_at_the_same_instant():
    """Which is why an order has to be made downstream, by a delay cell.

    Every cell takes the same moment to be sure, so the pair is shifted whole
    and neither event overtakes the other.
    """
    r = Retina()
    for t in range(0, SETTLE_MS + 1):
        r.update(t, OBJECT, AT_REST)
    head, seen = 0.0, []
    for t in range(SETTLE_MS + 1, 4000, TICK_MS):
        head += 0.2 * TICK_MS / 10
        seen += [(t, e.p, e.address[0]) for e in r.update(t, OBJECT, head)]
    moves = [(a, b) for a, b in zip(seen, seen[1:]) if a[1] is OFF]
    assert moves
    for (t_off, _, off_cell), (t_on, p, on_cell) in moves:
        assert p is ON and t_on - t_off == SETTLE_MS and abs(on_cell - off_cell) == 1


def test_it_says_nothing_while_nothing_changes():
    """Spec 001: a sensor emits nothing at all while its input is constant."""
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    for t in range(0, SETTLE_MS + 1):      # the object turning up is a change
        r.update(t, OBJECT, AT_REST)
    assert stream(r, [(t, OBJECT, AT_REST)
                      for t in range(SETTLE_MS + 1, 4000, TICK_MS)]) == []


def test_two_events_from_one_cell_are_never_closer_than_t_ref():
    r = Retina()
    head = 0.0
    events = []
    for t in range(0, 2000, TICK_MS):       # sweep the object across the eye
        head += 0.8 * TICK_MS / 10
        events += [(t, e) for e in r.update(t, OBJECT, head)]
    last = {}
    for t, e in events:
        cell = e.address[0]
        assert t - last.get(cell, -T_REF_MS) >= T_REF_MS
        last[cell] = t
    assert events, "the sweep should have produced something"


def test_every_cell_has_both_an_on_and_an_off_channel():
    """Sweep the object across the whole eye, head still."""
    r = Retina()
    seen = set()
    for t in range(0, 4000, TICK_MS):
        object_deg = 50.0 - (t / 4000) * 100.0
        for e in r.update(t, object_deg, AT_REST):
            seen.add((e.address[0], e.p))
    for cell in range(1, 10):
        assert (cell, ON) in seen and (cell, OFF) in seen


def test_the_stream_is_time_ordered():
    r = Retina()
    head, events = 0.0, []
    for t in range(0, 2000, TICK_MS):
        head += 0.4 * TICK_MS / 10
        events += [(t, e) for e in r.update(t, OBJECT, head)]
    assert [t for t, _ in events] == sorted(t for t, _ in events)
