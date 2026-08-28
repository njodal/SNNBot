# 009 — Vehicle 1, Version D: the wiring is learnt

- **Status:** draft
- **Date:** 2026-08-28
- **Supersedes / Superseded by:** —

[Version C](008-vehicle-1-c-neuromorphic.md) with nobody to wire it, on the body of [spec 005](005-vehicle-1.md).

The same body, the same eye and the same 72 correlation cells as Version C. What changes is that nobody says beforehand which effector each of those cells reaches. The vehicle has to find that out.

Which needs something to learn from, and the obvious candidate is not available: there is no measure of how far the object sits from the middle. A neuromorphic eye never says where anything is. It only ever says that something moved.

## The error is not there, but its sign is
It turns out that is enough, because what a learner needs is not the error but whether the last thing it did made the error smaller.

A correlation cell says the object went from cell i to cell j. Whether it got closer to the middle or further from it is then settled by the pair alone — no measurement, no arithmetic at run time, and nothing read off the world. It is a fixed property of each cell, decided once when the layer is built:

| the cells where | meaning | how many |
|-----------------|---------|----------|
| `abs(j - middle) < abs(i - middle)` | it came closer | 32 |
| `abs(j - middle) > abs(i - middle)` | it went further | 32 |
| `abs(j - middle) == abs(i - middle)` | neither, it crossed over | 8 |

So the reinforcement signal is not a quantity to be computed but **a partition of the sensory layer**: some of its cells mean *better* and some mean *worse*, by virtue of which cells of the eye they are wired to. The eye did not take the error signal away. It handed it over already differentiated, which is the form a learner wants it in.

On top of that sits a rarer and blunter one, free of any wiring at all: the ON of the middle cell is *arrived*, and its OFF is *lost it*. Too rare to learn from on its own — a vehicle that knows nothing reaches the middle almost never — but worth having as a bonus over the graded signal that arrives at every move.

## Which wire gets the credit
The signal turns up after the act, so something has to remember what was done. When a correlation cell wakes an effector, the connection between those two is left **eligible**, and the eligibility fades. When a reinforcing spike arrives it strengthens every connection still eligible, by however much of the eligibility is left. Nothing here is global: a connection is changed by what passed through it and by a signal that reaches it, and by nothing else.

## What the connection becomes
The table of Version C, one effector per cell, becomes a weight per pair of cell and effector. What fires is the strongest, or one drawn from among the strong so that the vehicle keeps trying things it has not settled on.

This is what the layer being fully connected was for. Under a fixed wiring, 56 of the 72 cells can never fire at all, since the object never skips a cell, and a table with 56 dead entries looks like waste. Under a learnt one it is not: which pairs matter is precisely what is not known in advance, and the ones that never occur simply never update.

## Babbling, and what it is now for
Two things stand in the way of learning, and they have the same cure.

The vehicle cannot tell its own movement from the world's. An object that moves while the vehicle is learning credits it for transitions it did not cause. So it is taught against **an object that stays still**, where every change on the retina is its own doing and the credit is clean.

But a still object seen by an eye that reports only change produces nothing at all, as Version C shows for six seconds together. The only way to make a still world visible is to move, which is what the babbling of [spec 002](002-vehicles.md) is.

Which puts babbling at odds with the rule that an effector, once wired, never babbles again — because a vehicle that is still learning has to keep exploring. The way out is that a weight is not a wire: **uncontrolled** stops being a state a cell is in and becomes what a cell does while nothing is telling it convincingly what to do. Babbling then fades of its own accord as the weights grow, and the rule in spec 002 turns from something imposed into something observed at the end of learning.

## What it learns

![Version D being taught](../docs/images/learning.gif)

Being taught, in three windows of the same four minutes: the first seconds, the middle, and the end. The object never moves, so the only thing that can make it visible is the vehicle moving itself, and early on that is all there is — flailing, and the object wherever it happens to land. By the end the flailing has largely gone and the object mostly sits in the middle cell.

The counter is how many of the 72 cells have learnt anything at all, and it is the discouraging part: after four minutes it is around ten. Only 16 of the 72 can ever fire, since the object never skips a cell, so it is ten of a possible sixteen — but the vehicle spends much of its schooling somewhere it has already been.

Afterwards, with learning off and nothing left to chance, it runs the experiment like this:

![Version D after four minutes of being taught](../docs/images/version_d.gif)

That is one run of one seed, though, and this vehicle varies a great deal from seed to seed:

| | holds the object in the middle |
|---|---|
| [Version C](008-vehicle-1-c-neuromorphic.md), wired by hand | 7.84 s of 15 |
| Version D, taught four minutes, over eight seeds | 8.70 s on average, from 6.07 to 11.38 |

So it learns — an untaught vehicle manages almost nothing, and a taught one lands in the same range as the wiring put in by hand. But it does not yet beat it. The spread across seeds is wider than the difference between the two, which means a single run of Version D says more about its seed than about learning, and a good one should not be reported as a result.

## Open questions

- How much does a reinforcing spike change a weight, and how fast does eligibility fade? Between them they set whether the vehicle learns at all and whether what it learns survives one bad run.
- How strong must a weight be before a cell stops babbling, and does it ever go back?
- Standing still in the middle earns nothing. The vehicle is paid for *improving*, and improving means having got worse first, so a vehicle that wanders off and comes back is paid for the coming back. It does not do that here, but nothing in the reward says it must not.
- Ten of the sixteen cells that can fire is poor coverage for four minutes of schooling. Teaching it against an object that is not always in the same place would visit more of them.
