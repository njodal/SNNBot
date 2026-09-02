"""Version E of spec 005: nobody tells it which cells are the good ones."""

import random

from snnbot.body.vehicle1 import Vehicle1
from snnbot.clock import Clock
from snnbot.events import Event, OFF, ON
from snnbot.layers.sensory import Critic, ValueReflex
from snnbot.params import ARRIVING_PAYS, LEAVING_COSTS
from snnbot.world import World, wandering


def critic(places=range(1, 10)):
    return Critic(places, middle=5)


def test_the_drive_is_two_wires_from_one_cell_of_the_eye():
    c = critic()
    assert c.drive([Event(0, (5,), ON)]) == ARRIVING_PAYS
    assert c.drive([Event(0, (5,), OFF)]) == -LEAVING_COSTS
    assert c.drive([Event(0, (4,), ON), Event(0, (7,), OFF)]) == 0     # no other cell


def test_it_starts_thinking_nothing_is_worth_anything():
    assert set(critic().value.values()) == {0.0}


def test_a_reward_waits_for_a_state_to_charge_it_to():
    """The eye sees the arrival at once, a correlation cell a delay later."""
    c = critic()
    c.sense(0, [Event(0, (5,), ON)])
    c.update(0, [(3, 4)])                       # the first state, nothing to compare
    c.update(50, [(4, 5)])
    assert c.value[4] != 0                      # charged to where it was, cell 4


def test_what_it_values_is_where_the_object_is_not_how_it_got_there():
    c = critic()
    c.value[4] = 0.5
    assert c.worth([(3, 4)]) == 0.5             # arrived at 4, from wherever
    assert c.worth([(5, 4)]) == 0.5             # the same place, the other way


def test_it_is_told_nothing_about_which_cells_are_good():
    r = ValueReflex(random.Random(0), speed=False)
    assert set(r.critic.value.values()) == {0.0}


def test_it_learns_values_from_the_middle_cell_alone():
    r = ValueReflex(random.Random(2), speed=False)
    world = World(object_deg=18.0, path=wandering(random.Random(9)))
    v = Vehicle1(world, rng=random.Random(102), reflex=r)
    for t in Clock().times(60_000):
        world.update(t)
        v.step(t)
    assert any(r.critic.value.values()), "nothing came to be worth anything"


def test_acting_can_be_charged_for():
    """One more wire into the reward cell, from the effectors that already spike."""
    c = critic()
    c.charge(10)
    assert c._owed == 0                          # nothing is what it costs today

    c = Critic(range(1, 10), middle=5, acting=0.01)
    c.charge(10)
    assert c._owed == -0.1


def test_a_reflex_that_does_not_pay_is_told_all_the_same():
    """Every reflex hears what its effectors fired; only one of them cares."""
    from snnbot.layers.sensory import CorrelationReflex, Reflex

    for reflex in (Reflex(), CorrelationReflex()):
        reflex.spent(5)                          # and says nothing about it


def test_being_centred_pays_while_it_lasts():
    """The one tonic thing here: an eye of changes cannot say *still there*."""
    c = critic()
    c.sense(0, [Event(0, (5,), ON)])
    owed = c._owed
    for t in range(1, 1000):
        c.sense(t, [])
    assert c._owed > owed + 0.5                  # about a second of it, about 1

    stops = critic()
    stops.sense(0, [Event(0, (5,), ON)])
    stops.sense(1, [Event(1, (5,), OFF)])
    owed = stops._owed
    for t in range(2, 1000):
        stops.sense(t, [])
    assert stops._owed == owed                   # and nothing once it is gone


def test_it_finds_that_the_middle_is_the_good_place():
    """Taught by the middle cell alone, without being told what any move means."""
    from snnbot.layers.sensory import outcome

    r = ValueReflex(random.Random(2), speed=False)
    world = World(object_deg=18.0, path=wandering(random.Random(9)))
    v = Vehicle1(world, rng=random.Random(102), reflex=r)
    for t in Clock().times(240_000):
        world.update(t)
        v.step(t)

    learnt = r.partition()
    judged = [(learnt[m] > 0) == (outcome(m) > 0)
              for m in learnt if outcome(m) and any(r.critic.value[c] for c in m)]
    assert sum(judged) / len(judged) > 0.75      # chance being half
