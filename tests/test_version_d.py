"""Version D of spec 005: the vehicle finds the wiring for itself."""

import random

from snnbot.body.vehicle1 import LEFT, RIGHT, Vehicle1
from snnbot.clock import Clock
from snnbot.layers.sensory import CorrelationReflex, LearningReflex, outcome
from snnbot.params import WEIGHT_MAX
from snnbot.world import World, experiment_path


def train(reflex, seconds, seed=2):
    v = Vehicle1(World(object_deg=18.0), rng=random.Random(seed), reflex=reflex)
    for t in Clock().times(int(seconds * 1000)):
        v.step(t)
    return reflex


def score(reflex, seed=3):
    """How long it keeps the object in the middle cell, with nothing left to chance."""
    if hasattr(reflex, "learning"):
        reflex.learning, reflex.explore = False, 0.0
    world = World(object_deg=18.0, path=experiment_path())
    v = Vehicle1(world, rng=random.Random(seed), reflex=reflex)
    return sum(v.retina.busy_cell() == 5
               for t in Clock().times(15000) if (world.update(t), v.step(t))) / 100


def test_the_cells_are_split_into_better_worse_and_neither():
    cells = [(i, j) for j in range(1, 10) for i in range(1, 10) if i != j]
    assert sum(outcome(p) == 1 for p in cells) == 32
    assert sum(outcome(p) == -1 for p in cells) == 32
    assert sum(outcome(p) == 0 for p in cells) == 8


def test_what_the_partition_means():
    assert outcome((3, 4)) == 1        # nearer the middle
    assert outcome((4, 3)) == -1       # further from it
    assert outcome((4, 6)) == 0        # straight across, no nearer


def test_it_starts_knowing_nothing():
    r = LearningReflex(random.Random(0))
    assert set(w for weights in r.weights.values() for w in weights.values()) == {0.0}


def test_an_untried_cell_tries_something_and_a_taught_one_does_not():
    r = LearningReflex(random.Random(0), explore=0.0)
    r.weights[(3, 4)][(LEFT, 2)] = 0.5
    assert r.choose((3, 4)) == (LEFT, 2)
    assert len({r.choose((5, 6)) for _ in range(20)}) > 1     # nothing learnt yet


def test_least_harmful_is_still_a_choice():
    """Untried is not the same as known to be bad."""
    r = LearningReflex(random.Random(0), explore=0.0)
    for action in r.actions:
        r.weights[(3, 4)][action] = -1.0
    r.weights[(3, 4)][(RIGHT, 1)] = -0.2
    assert r.choose((3, 4)) == (RIGHT, 1)


def test_credit_goes_to_what_was_used_and_fades():
    r = LearningReflex(random.Random(0))
    r._eligible[((3, 4), (LEFT, 0))] = 0
    r.reinforce(100, 1)
    assert r.weights[(3, 4)][(LEFT, 0)] > 0

    r = LearningReflex(random.Random(0))
    r._eligible[((3, 4), (LEFT, 0))] = 0
    r.reinforce(100_000, 1)                                  # long past eligible
    assert r.weights[(3, 4)][(LEFT, 0)] == 0


def test_a_connection_has_a_strongest_it_can_get():
    r = LearningReflex(random.Random(0))
    for _ in range(100):
        r._eligible[((3, 4), (LEFT, 0))] = 0
        r.reinforce(0, 1)
    assert r.weights[(3, 4)][(LEFT, 0)] == WEIGHT_MAX


def test_nothing_is_learnt_while_learning_is_off():
    r = LearningReflex(random.Random(0))
    r.learning = False
    r._eligible[((3, 4), (LEFT, 0))] = 0
    r.reinforce(100, 1)
    assert r.weights[(3, 4)][(LEFT, 0)] == 0


def test_it_learns_something():
    untaught = score(LearningReflex(random.Random(1)))
    taught = score(train(LearningReflex(random.Random(1)), 120))
    assert taught > untaught + 5


def test_what_it_learns_beats_the_wiring_it_was_given():
    """The point of the whole thing: it has to beat Version C to have learnt."""
    taught = score(train(LearningReflex(random.Random(1)), 240))
    assert taught > score(CorrelationReflex())
