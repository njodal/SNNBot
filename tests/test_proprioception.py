"""The contraction sensor, spec 001 example II."""

from snnbot.body.proprioception import ProprioceptiveArray
from snnbot.events import ON


def test_which_sensor_fires_is_the_reading():
    """Sensor 3 covers 20 up to 30, as the example says."""
    a = ProprioceptiveArray()
    a.update(0, 25)
    assert a.firing() == 3


def test_exactly_one_sensor_at_a_time():
    for level in range(0, 101):
        a = ProprioceptiveArray()
        a.update(0, level)
        firing = [s.index for s in a.sensors if s.holds(level)]
        assert len(firing) == 1, f"level {level} is read by {firing}"


def test_no_level_at_all_falls_between_two_sensors():
    """Whole steps land on whole numbers. A controller that does not step does not.

    Version A of spec 006 turns its joints continuously, and an eye brought back
    to the middle of its range comes to rest at 50 and a fraction — which whole
    numbered edges a unit apart left unread by anything.
    """
    a = ProprioceptiveArray()
    for tenth in range(0, 1001):
        level = tenth / 10
        firing = [s.index for s in a.sensors if s.holds(level)]
        assert len(firing) == 1, f"level {level} is read by {firing}"


def test_it_keeps_firing_while_the_level_holds():
    """Unlike the eye: a contraction that does not move is still reported."""
    a = ProprioceptiveArray()
    spikes = [e for t in range(0, 500, 10) for e in a.update(t, 25)]
    assert len(spikes) > 5
    assert all(e.address == (3,) and e.p is ON for e in spikes)


def test_leaving_a_range_is_reported_once():
    a = ProprioceptiveArray()
    a.update(0, 25)
    events = a.update(10, 35)
    assert sorted(str(e) for e in events) == ["3 off", "4 on"]
