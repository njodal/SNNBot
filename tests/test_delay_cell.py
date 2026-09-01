"""The delay cell of spec 010: the same spike again, later."""

from snnbot.layers.cells import DelayBank, DelayCell


def test_it_says_nothing_until_the_wait_is_up():
    cell = DelayCell(20)
    assert not cell.update(0, fired=True)
    assert not any(cell.update(t) for t in range(1, 20))
    assert cell.update(20)


def test_it_says_nothing_at_all_if_nothing_went_in():
    cell = DelayCell(20)
    assert not any(cell.update(t) for t in range(0, 200))


def test_what_goes_in_comes_out_as_often():
    cell, went_in = DelayCell(20), (0, 5, 40)
    came_out = [t for t in range(0, 200) if cell.update(t, fired=t in went_in)]
    assert came_out == [t + 20 for t in went_in]


def test_a_bank_delays_each_source_on_its_own():
    bank = DelayBank(range(1, 10), 20)
    assert bank.update(0, [3]) == []
    assert bank.update(10, [7]) == []
    assert bank.update(20) == [3]
    assert bank.update(30) == [7]


def test_it_is_what_makes_two_things_at_once_into_an_order():
    """The eye reports both at the same instant; this is what separates them."""
    bank = DelayBank(range(1, 10), 20)
    left, arrived = 3, 4                       # the eye says both at t = 0
    at = next(t for t in range(0, 100) if arrived in bank.update(t, [arrived] if t == 0 else []))
    assert at == 20 and at > 0                 # the leaving was first, by 20 ms
