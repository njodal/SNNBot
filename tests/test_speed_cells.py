"""Correlation cells with a window each, which is what makes them read speed."""

import statistics

from snnbot.body.retina import Retina
from snnbot.clock import Clock
from snnbot.events import Event, OFF, ON
from snnbot.layers.sensory import SpeedLayer, speed_bands
from snnbot.params import CELL_ANGLE_DEG, DEG_PER_SPIKE, STEERING, TICK_MS


def test_the_bands_tile_the_transit_times():
    bands = speed_bands()
    assert len(bands) == 5                                  # one per effector
    for (lo, hi, tuned) in bands:
        assert lo < tuned < hi                              # each holds its own
    for (_, hi, _), (lo, _, _) in zip(bands, bands[1:]):
        assert hi == lo                                     # and no gap between


def test_each_band_holds_one_speed_of_the_body_and_no_other():
    transits = [CELL_ANGLE_DEG / (hz * DEG_PER_SPIKE) * 1000 for hz, _ in STEERING]
    for transit in transits:
        holding = [b for b in speed_bands() if b[0] <= transit <= b[1]]
        assert len(holding) == 1


def test_a_cell_watches_two_that_are_not_neighbours():
    for cell in SpeedLayer().cells:
        assert abs(cell.succ - cell.pred) > 1
        assert cell.crossed == abs(cell.succ - cell.pred) - 1


def test_what_speed_a_cell_stands_for():
    cell = next(c for c in SpeedLayer().cells if (c.pred, c.succ) == (2, 4))
    assert cell.crossed == 1
    assert cell.speed() == CELL_ANGLE_DEG / (cell.tuned_to / 1000)


def test_it_fires_on_an_interval_inside_its_window_and_not_outside():
    layer = SpeedLayer()
    slowest = max(c.high for c in layer.cells)
    layer.update(0, [Event(0, (2,), OFF)])
    fired = layer.update(200, [Event(200, (4,), ON)])
    assert fired and all(c.low <= 200 <= c.high for c in fired)

    layer = SpeedLayer()
    layer.update(0, [Event(0, (2,), OFF)])
    assert layer.update(int(slowest) + 1000, [Event(0, (4,), ON)]) == []


def test_an_arrival_next_door_fires_none_of_them():
    """That is the other kind of cell's job, and its interval is not a transit."""
    layer = SpeedLayer()
    layer.update(0, [Event(0, (3,), OFF)])
    assert layer.update(200, [Event(200, (4,), ON)]) == []


def test_what_fires_says_how_fast_the_head_went():
    """The point of the whole thing, run against the eye itself."""
    for hz, _ in STEERING:
        speed = hz * DEG_PER_SPIKE
        retina, layer, head, said = Retina(), SpeedLayer(), -40.0, []
        for t in Clock().times(30_000):
            head += speed * TICK_MS / 1000
            if head > 40:
                break
            said += [c.speed() for c in layer.update(t, retina.update(t, 0.0, head))]
        assert said, f"nothing fired at {speed} deg/s"
        assert statistics.median(said) == speed


def test_a_wandering_object_moves_at_more_than_one_speed():
    """What teaching a vehicle about speed needs, and a still object cannot give."""
    import random
    from snnbot.world import wandering

    where = wandering(random.Random(0))
    seen = [where(t) for t in range(0, 60_000, 100)]
    assert min(seen) < -20 and max(seen) > 20            # it gets about
    speeds = {round(abs(b - a) / 0.1) for a, b in zip(seen, seen[1:])}
    assert len(speeds) > 5                               # and not always alike


def test_the_same_seed_wanders_the_same_way():
    import random
    from snnbot.world import wandering

    a, b = wandering(random.Random(4)), wandering(random.Random(4))
    assert [a(t) for t in range(0, 20_000, 250)] == [b(t) for t in range(0, 20_000, 250)]
