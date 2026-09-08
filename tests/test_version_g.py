"""Version G of spec 005: Version F with the gain left to be found."""

import random

from snnbot.body.vehicle1 import LEFT, RIGHT, Vehicle1
from snnbot.clock import Clock
from snnbot.events import Event, ON
from snnbot.layers.sensory import GainReflex, ProportionalReflex
from snnbot.params import KP
from snnbot.world import World, experiment_path, jumping


def teach(seconds=60.0, seed=1):
    reflex = GainReflex(random.Random(seed))
    world = World(object_deg=18.0, path=jumping(random.Random(seed + 7)))
    v = Vehicle1(world, rng=random.Random(seed), reflex=reflex)
    for t in Clock().times(int(seconds * 1000)):
        world.update(t)
        v.step(t)
    reflex.learning, reflex.explore = False, 0.0
    return reflex


def catches(reflex, object_deg=36.0, seconds=3.0):
    """How long it takes to bring an object at the far edge of the eye to the middle."""
    v = Vehicle1(World(object_deg=object_deg), rng=random.Random(0), reflex=reflex)
    for t in Clock().times(int(seconds * 1000)):
        v.step(t)
        if v.retina.busy_cell() == 5:
            return t
    return None


def holds(reflex):
    world = World(object_deg=18.0, path=experiment_path())
    v = Vehicle1(world, rng=random.Random(0), reflex=reflex)
    centred = 0
    for t in Clock().times(15000):
        world.update(t)
        v.step(t)
        centred += v.retina.busy_cell() == 5
    return centred / 1000


def test_it_starts_knowing_nothing():
    r = GainReflex(random.Random(0))
    assert all(w == 0.0 for by_rung in r.weights.values() for w in by_rung.values())
    assert 0 not in r.weights                       # zero error wakes nothing, and learns nothing


def test_the_side_is_not_learnt():
    r = GainReflex(random.Random(0))
    assert r.wire(-3)[0] == LEFT and r.wire(3)[0] == RIGHT


def test_untried_before_tried():
    r = GainReflex(random.Random(0))
    chosen = {r.choose(2) for _ in range(200)}
    assert chosen == set(r.rungs)                   # anything, while nothing has been tried
    r.tried[2] = set(r.rungs) - {5}
    assert r.choose(2) == 5                         # the one left


def test_once_everything_is_tried_it_goes_with_the_best():
    r = GainReflex(random.Random(0), explore=0.0)
    r.tried[2] = set(r.rungs)
    r.weights[2][3] = 0.5
    assert all(r.choose(2) == 3 for _ in range(50))


def test_a_weight_moves_toward_what_its_rung_earned_and_credit_fades():
    r = GainReflex(random.Random(0), lr=0.5, eligibility_ms=1000)
    r._eligible[(2, 3)] = 0
    r.reinforce(500, 1.0)                           # half the eligibility left
    assert r.weights[2][3] == 0.25
    r.reinforce(600, 1.0)
    assert 0.25 < r.weights[2][3] < 0.5             # toward 0.4, not piling up
    r.reinforce(2000, 1.0)                          # too late to count
    assert (2, 3) not in r._eligible


def test_nothing_is_learnt_while_learning_is_off():
    r = GainReflex(random.Random(0))
    r.learning = False
    r._eligible[(2, 3)] = 0
    r.reinforce(10, 1.0)
    assert r.weights[2][3] == 0.0


def test_arriving_leaves_nothing_to_blame():
    """Nothing runs at zero error, so what the object does next is its own doing."""
    r = GainReflex(random.Random(0))
    r._error, r._eligible = -1, {(-1, 2): 0}
    r.fired = lambda t, eye: [(5, 5)]               # the middle diagonal fires
    r.update(20, None, [], {})
    assert r._eligible == {} and r._error == 0


def test_the_credit_is_the_change_in_the_error():
    r = GainReflex(random.Random(0), lr=1.0)
    r._error, r._eligible = -3, {(-3, 4): 0}
    r.fired = lambda t, eye: [(3, 5)]               # from three cells off to two
    r.update(10, None, [], {})
    assert r.weights[-3][4] > 0
    r._eligible = {(-2, 4): 10}
    r.fired = lambda t, eye: [(2, 5)]               # and back out to three
    r.update(20, None, [], {})
    assert r.weights[-2][4] < 0


def test_a_reflex_lives_the_same_life_twice():
    """A body calls forget() at birth: nothing held from the life before."""
    r = ProportionalReflex()
    assert holds(r) == holds(r)
    g = teach()
    assert catches(g) == catches(g)


def test_it_still_brings_the_object_to_the_middle_and_keeps_it_there():
    g = teach()
    assert holds(g) >= holds(ProportionalReflex())


def test_what_it_learns_is_a_bigger_gain_than_it_was_given():
    """On a pure integrator the best gain is the biggest the body has."""
    g = teach()
    assert catches(g) < catches(ProportionalReflex())
    assert all(g.gain(d) >= KP for d in (-2, 2))
