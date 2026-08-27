"""The eye. Criteria from spec 001 and the worked pair of spec 005."""

from snnbot.body.retina import Retina
from snnbot.events import OFF, ON
from snnbot.params import T_REF_MS

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

    The cell it leaves says so at once and the cell it reaches a cycle later, so
    the two events of the move arrive in that order and never together.
    """
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    assert [str(e) for e in r.update(10, OBJECT, AT_REST)] == ["3 on"]
    assert [str(e) for e in r.update(100, OBJECT, TURNED_LEFT)] == ["3 off"]
    assert [str(e) for e in r.update(110, OBJECT, TURNED_LEFT)] == ["5 on"]
    assert r.busy_cell() == 5


def test_the_cells_never_share_an_edge():
    """An object exactly on a boundary is in one cell, never in two."""
    r = Retina()
    for boundary in (4.5, 13.5, 22.5, -4.5, -13.5):
        r.update(0, boundary, AT_REST)
        assert sum(c.occupied for c in r.cells) == 1


def test_a_move_is_always_an_off_and_then_an_on():
    """What the correlation cells of Version C read: the order, never a tie."""
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    r.update(10, OBJECT, AT_REST)
    head, seen = 0.0, []
    for t in range(10, 4000, 10):
        head += 0.2
        seen += [(t, e.p, e.address[0]) for e in r.update(t, OBJECT, head)]
    moves = [(a, b) for a, b in zip(seen, seen[1:]) if a[1] is OFF]
    assert moves
    for (t_off, _, off_cell), (t_on, p, on_cell) in moves:
        assert p is ON and t_on > t_off and abs(on_cell - off_cell) == 1


def test_it_says_nothing_while_nothing_changes():
    """Spec 001: a sensor emits nothing at all while its input is constant."""
    r = Retina()
    r.update(0, OBJECT, AT_REST)
    r.update(10, OBJECT, AT_REST)          # the object turning up is a change
    assert stream(r, [(t, OBJECT, AT_REST) for t in range(20, 1000, 10)]) == []


def test_two_events_from_one_cell_are_never_closer_than_t_ref():
    r = Retina()
    head = 0.0
    events = []
    for t in range(0, 2000, 10):            # sweep the object across the eye
        head += 0.8
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
    for t in range(0, 4000, 10):
        object_deg = 50.0 - (t / 4000) * 100.0
        for e in r.update(t, object_deg, AT_REST):
            seen.add((e.address[0], e.p))
    for cell in range(1, 10):
        assert (cell, ON) in seen and (cell, OFF) in seen


def test_the_stream_is_time_ordered():
    r = Retina()
    head, events = 0.0, []
    for t in range(0, 2000, 10):
        head += 0.4
        events += [(t, e) for e in r.update(t, OBJECT, head)]
    assert [t for t, _ in events] == sorted(t for t, _ in events)
