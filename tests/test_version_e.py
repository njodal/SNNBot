"""Version E of spec 005: nobody tells it which cells are the good ones."""

import random

from snnbot.body.vehicle1 import Vehicle1
from snnbot.clock import Clock
from snnbot.events import Event, OFF, ON
from snnbot.layers.sensory import Critic, ValueReflex
from snnbot.params import ARRIVING_PAYS, LEAVING_COSTS
from snnbot.world import World, wandering


def critic(cells=((3, 4), (4, 5), (5, 4))):
    return Critic(list(cells), middle=5)


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
    c.sense([Event(0, (5,), ON)])
    c.update(0, [(3, 4)])                       # the first state, nothing to compare
    c.sense([])
    c.update(50, [(4, 5)])
    assert c.value[(3, 4)] != 0                 # the reward reached the state before it


def test_what_a_cell_is_worth_is_a_weight_and_not_something_it_keeps():
    c = critic()
    c.value[(3, 4)] = 0.5
    assert c.worth([(3, 4)]) == 0.5
    assert c.worth([(3, 4), (4, 5)]) == 0.5     # they add, being wires into one cell


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

    c = Critic(list(((3, 4),)), middle=5, acting=0.01)
    c.charge(10)
    assert c._owed == -0.1


def test_a_reflex_that_does_not_pay_is_told_all_the_same():
    """Every reflex hears what its effectors fired; only one of them cares."""
    from snnbot.layers.sensory import CorrelationReflex, Reflex

    for reflex in (Reflex(), CorrelationReflex()):
        reflex.spent(5)                          # and says nothing about it
