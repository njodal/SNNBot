"""The sequence cell of spec 010: a chain of correlation cells folded into one."""

from snnbot.layers.cells import SequenceCell


def fires(cell, spikes, until):
    """`spikes` is {t: [inputs]}; the times the cell fires up to `until`."""
    return [t for t in range(until) if cell.update(t, spikes.get(t, ()))]


def test_three_in_order_make_it_fire_once_on_the_last():
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [1], 40: [2]}, 100) == [40]


def test_the_wrong_order_keeps_it_quiet():
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [2], 40: [1]}, 100) == []
    assert fires(SequenceCell(3, 10, 50), {0: [1], 20: [0], 40: [2]}, 100) == []


def test_two_inputs_is_the_correlation_cell():
    """It is the order that decides, not that both arrived."""
    assert fires(SequenceCell(2, 10, 50), {0: [0], 20: [1]}, 60) == [20]
    assert fires(SequenceCell(2, 10, 50), {0: [1], 20: [0]}, 60) == []


def test_the_same_moment_is_not_an_order():
    assert fires(SequenceCell(2, 10, 50), {0: [0], 5: [1]}, 60) == []
    assert fires(SequenceCell(2, 10, 50), {0: [0, 1]}, 60) == []


def test_too_far_apart_breaks_it():
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [1], 90: [2]}, 120) == []
    assert fires(SequenceCell(3, 10, 50), {0: [0], 70: [1], 90: [2]}, 120) == []


def test_a_broken_sequence_does_not_finish_on_the_next_input():
    """After a wrong input, the rest of the order counts for nothing."""
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [2], 40: [1], 60: [2]}, 100) == []


def test_the_first_input_starts_it_again():
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [0], 40: [1], 60: [2]}, 100) == [60]
    assert fires(SequenceCell(3, 10, 50), {0: [0], 20: [1], 40: [0], 60: [2]}, 100) == []


def test_primed_while_waiting_for_the_last_one_only():
    cell = SequenceCell(3, 10, 50)
    assert not cell.primed
    cell.update(0, [0])
    assert not cell.primed
    cell.update(20, [1])
    assert cell.primed
    cell.update(30)
    assert cell.primed                  # still within the window
    cell.update(80)
    assert not cell.primed              # the window closed
    cell.update(100, [0]); cell.update(120, [1]); cell.update(140, [2])
    assert not cell.primed              # fired, and back to the start
