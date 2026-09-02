"""The coincidence cell of spec 010, with the window spec 011 gives it."""

from snnbot.layers.cells import CoincidenceCell


def tonic(period, phase, until):
    return {t for t in range(phase, until, period)}


def fires(cell, a, b, until):
    return [t for t in range(until)
            if cell.update(t, [k for k, src in ((0, a), (1, b)) if t in src])]


def test_two_things_at_once_make_it_fire():
    assert fires(CoincidenceCell(2, 20), {0}, {0}, 5) == [0]


def test_one_thing_alone_never_does():
    assert fires(CoincidenceCell(2, 20), tonic(20, 0, 200), set(), 200) == []


def test_two_things_out_of_step_make_it_fire_at_their_rate():
    """Which is what the window is for: without it, tonic sources never coincide."""
    a, b = tonic(20, 0, 200), tonic(20, 7, 200)
    assert len(fires(CoincidenceCell(2, 20), a, b, 200)) == 10
    assert fires(CoincidenceCell(2, 0), a, b, 200) == []


def test_each_spike_is_spent_once():
    """Two sources at 50 Hz make it fire at 50 Hz, not at every pairing."""
    a, b = tonic(20, 0, 400), tonic(20, 13, 400)
    assert len(fires(CoincidenceCell(2, 20), a, b, 400)) == 20


def test_too_far_apart_is_not_together():
    assert fires(CoincidenceCell(2, 20), {0}, {30}, 40) == []
    assert fires(CoincidenceCell(2, 20), {0}, {20}, 40) == [20]


def test_with_many_inputs_a_majority_is_enough():
    cell = CoincidenceCell(5, 10)
    assert not cell.update(0, [0, 1])
    assert cell.update(3, [2])                # three of five
    cell = CoincidenceCell(5, 10)
    assert not cell.update(0, [0, 1])
    assert not cell.update(30, [2])           # the first two have gone stale
