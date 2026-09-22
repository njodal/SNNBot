# 012 — A joint primitive

- **Status:** draft
- **Date:** 2026-09-19
- **Supersedes / Superseded by:** —

## Context
The controller of [spec 011](011-neuromorphic-p-controller.md) has now been built three times: once for the head of [Vehicle 1](005-vehicle-1.md), in Version F, and twice in [Version C of Vehicle 2](006-vehicle-2.md), for its eye and for its neck. Spec 006 calls the last two *the same circuit*, and then lists three things different between them. `gaze_reflexes` says it more bluntly than the prose does. It builds one class twice and hands it, each time, a fistful of things from outside:

| handed in | the eye's | the neck's | what it is really a fact about |
|---|---|---|---|
| `cells` | 9 | 10 | the array it reads |
| `tonic` | no | yes | the array it reads |
| `mirror` | no | yes | which actuator's array it reads |
| `reference` | the middle cell | level 6 | the task |
| `dead` | 0 | 2 levels | the task |
| the ladder: `k`, degrees per spike, cap, duration, `dead` again | `Kp`, 0.9, 450, 100 ms | `Kr`, 1.6, 160, three periods | the body, the task and a taste for how it should look |

So it is the same circuit the way two houses are the same plan: somebody who knew both sites adjusted each. Every one of those numbers was worked out by whoever wrote the vehicle, from things the vehicle is not allowed to read.

What prompted the question is work published, so far only as demonstrations, by [Artificial Brains](https://artificialbrains.ai): a spiking block of about 120 neurons, copied unchanged onto every joint of an arm, [two opposing copies a joint](https://x.com/alexanderawolf/status/2100975132282085724) — one that flexes and one that extends — with no calibration joint by joint, the copies said to *adapt to the body they are connected to*. Nothing about how is public, and none of it is leaned on here. What is taken is the question, which this project is unusually well placed to ask, having a controller in cells, two joints that are deliberately not alike, and in [Version G](005-vehicle-1.md) a controller that has already found one of its own numbers.

## Goal
One circuit, built with no argument that names a joint, which drives the head of Vehicle 1, the head of Vehicle 2 and the neck of Vehicle 2 as well as the three hand-fitted ones do. Whatever differs between them has to arrive through what the circuit is plugged into, or be found by it.

## Scope
In: what is inside the primitive and what is its socket; where each row of the table above goes; the two stages it is built in; what it is measured against.

Out: a cortex that sets the reference, which stays the observer's job as in Version F. Any new kind of cell. A body with inertia, which is where Version G says its answer would stop being the right one, and which deserves a vehicle of its own. Anything that tells the primitive what a movement costs — the missing price spec 006 keeps running into is noted where it bites and not solved.

## Design

### A primitive is for an actuator, not for a joint
An actuator of [spec 003](003-neuromorphic-actuators.md) only contracts. So the unit that gets copied is the half of the spec 011 controller that answers with *one* actuator: the triangle of the table on which that actuator is the answer, the zero diagonal, and the wires from each diagonal to the rungs of that actuator's ladder. A joint is two copies, facing each other.

```
            r row ─────────────┬──────────────────────────┐
            p row ──────┬──────│───────────────────┐      │
                        │      │                   │      │
                  ┌─────▼──────▼─────┐       ┌─────▼──────▼─────┐
                  │  table, p > r    │       │  table, p > r    │   the same, with
                  │  and p = r       │       │  and p = r       │   both rows plugged
                  │  diagonals→rungs │◄─────►│  diagonals→rungs │   in back to front
                  └────────┬─────────┘ each  └────────┬─────────┘
                           │        silences          │
                   rungs of one       the      rungs of its
                     actuator        other      antagonist
```

**The two copies are one circuit plugged in both ways round.** A copy contracts its actuator when `p` sits at a higher line than `r`, and does nothing when it sits lower. Its antagonist is the identical copy with the lines of both rows plugged in the opposite order, so that *lower* is what it sees as higher. That is the whole of `mirror`: the eye's right-hand copy takes the retina left to right, and the neck's left-hand copy takes the head's array in the order it comes, because a head turned left reads high on its left actuator. The flag goes away and what is left is a plug with two orientations.

**One wire runs between them.** Whatever wakes a rung in one copy reaches, inhibitorily, the stop of every rung in the other. In `ProportionalReflex.drive` that is the loop that stops every effector but the target, on both sides, and nobody had to say whose job it was. Between two copies it is a wire, and it has a name: it is the reciprocal inhibition a spinal cord runs between a flexor and its extensor, through an interneuron kept for the purpose.

**The zero diagonal is in both.** Each copy brakes its own rungs, so a joint has the cells `(i, i)` twice over. For `N` lines a copy is `N(N − 1)/2 + N` coincidence cells: 45 for the eye, 55 for the neck, 90 and 110 a joint against the 81 and 100 of one shared table. That is what cutting the circuit along the line the body is already cut along costs.

### The socket
A copy is plugged into three things and knows nothing else:

- **a `p` row**, `N` lines of which one fires, tonically;
- **an `r` row**, the same `N` lines, set by whoever decides the reference;
- **a ladder**, the start and stop of however many rungs the actuator has.

`N` is read off the row it is plugged into, and is the one thing about a copy that is not identical from joint to joint: the rule that builds the table is the same, the table it builds is as wide as what it reads. Whether that still counts as *the same primitive* is the first open question.

**A row of memory cells is an adapter, not part of the primitive.** The retina reports change and the primitive wants a line that fires while a thing is true, so between them sits the row of memory cells of Version F. The propioceptor needs none. Which is `tonic`, moved from an argument of the circuit to a fact about what stands in front of it — where spec 006 already said it belonged.

### The dead zone is a reference several lines wide
Version C gives the neck its comfortable range twice: as diagonals wired to nothing, and again as `k × (d − dead)` in the ladder, because a diagonal wired to nothing says when to move and not how much. Both are numbers inside the circuit, and the second is arithmetic done by whoever cut the ladder.

Both come out of the circuit if the comfortable range is said where a range can be said, in the reference: **set every line of `r` the joint is content to rest in**, and not one. Then, with `p` outside them, a whole run of diagonals fires at once — one per line of `r` that is set — and the smallest of them is the distance from `p` to the *nearest edge* of the range. Which is `d − dead`, with nobody having subtracted anything. With `p` inside the range the zero diagonal is among those that fire, and the joint brakes.

What it needs is for the nearest diagonal to win when several fire together, and the brake to win over all of them:

- each diagonal reaches, inhibitorily, the stop of every rung above its own;
- an inhibition arriving together with an excitation wins.

Wires, and one rule about a cell that spec 010 has not yet had to state. No cells, and no number: the primitive no longer has a dead zone, and the task has a reference that is as wide as it likes. Lines 4 to 8 of the head's array set, against one ladder cut to plain `k × d`, is Version C's neck exactly; and the lopsidedness spec 006 apologises for — ten levels having no middle — turns into a choice of which lines to set, made by the thing that sets them.

### The ladder belongs to the body, and which rung to the primitive
What is left of the table in Context is the ladder, and it is the real calibration: `k`, the degrees a spike is worth, the cap, and how long a rung runs were each worked out from the body's numbers by somebody holding a calculator.

[Spec 003](003-neuromorphic-actuators.md) has the effectors belong to the actuator. So the rungs are part of the body, as a muscle comes with its motor units, and they are whatever that body has: the four of spec 003, the four a joint of spec 006's table, or the eight Version F cut. **The primitive is handed the rungs and not the wiring**, which is [Version G](005-vehicle-1.md) and nothing new: every diagonal reaches every rung through a weight, the rung with the most behind it runs or one is tried, and credit comes from the table itself — a change of the nearest diagonal towards zero is an improvement, read off the wiring, and it goes to the rung that was running by what is left of its eligibility.

On Vehicle 1 that learner found the cap. What it finds on a neck whose gentlest useful command and whose wildest are a factor of eight apart, and whose fastest burst is four fifths of its range, is what this spec is for.

### Two stages
The same order spec 005 took, for the same reason — so that when the learnt one does something odd, there is a wired one to say whether the primitive or the learning did it.

**Wired.** The weights are set by hand to the ladders of Version F and Version C. Nothing is learnt. This stage tests only the cut: that two copies, a plug, one inhibitory wire and a wide reference are the circuit of spec 011 and have lost nothing. Vehicle 1 from two copies, Vehicle 2 from four.

**Found.** The weights start at nothing and each copy finds its own. The teaching follows what the project has already paid to learn: against an object that jumps, as in Version G, a wandering one teaching nothing past one cell of error; the eye first and frozen before the neck begins, as in Version B; the reflex arc of Version B in place throughout, so that what a neck copy does reaches the array it reads at once and the problem stays local.

### What is likely to go wrong
Written before it is built, as Version E of spec 005 did.

- **The neck learns the cap too.** Nothing in the credit prices a movement, a degree of neck is cheaper in spikes than a degree of eye, and a copy on the neck has the same reason as one on the eye to prefer the rung that closes the error soonest. Spec 006 measured what a thrashing neck costs: travel in the thousands of degrees against Version A's 63. If that is what comes out, it is a finding about the missing price and not a fault in the primitive, and the travel column below is there to catch it.
- **Too few jumps reach the neck.** A neck copy is taught by the head leaving its comfortable range, which takes an object jumping far, and the far diagonals are the ones that matter. Four minutes settled Version G; this may need the jumps biased outward, or longer.
- **Two learners on one joint.** The copies of a pair learn separately and only ever act in turn, but a rung still running when the error changes sign is silenced by the other side, and its eligibility is then credited with what its antagonist did. Version G never met this, having one learner for both sides.
- **Ties inside one tick.** The wide reference leans on inhibition beating excitation when both land together. The simulator steps in whole milliseconds and the rows of `r` are all set by the same spike, so together is the normal case and not the rare one.

## Acceptance criteria
Built as the next version of each vehicle; the numbers go there.

- [ ] The primitive is one class whose constructor takes a `p` row, an `r` row and a ladder, and no argument that is a number about a joint: no `cells`, `k`, `dead`, `mirror`, `tonic`, degrees per spike or cap.
- [ ] Six copies of it — two on Vehicle 1, four on Vehicle 2 — differ in nothing but what they are plugged into and which way round.
- [ ] Wired, two copies on Vehicle 1 keep the head within one step, 0.8 degrees, of Version F's at every moment of the experiment of [spec 005](005-vehicle-1.md).
- [ ] Wired, four copies on Vehicle 2 keep the gaze and both joint angles within one step of each joint of Version C's over the same experiment, with the reference of the neck's pair set to lines 4 to 8 and its ladder cut to `k × d` with nothing taken off.
- [ ] With one line of that reference set instead of five, the same circuit is Version C *with the subtraction left out*, to the same tolerance — the wide reference is what does the subtracting, and nothing else does.
- [ ] A rung running in one copy stops within one tick of a rung waking in its antagonist, and no tick of any run has rungs of both emitting.
- [ ] Found, on Vehicle 1: two copies taught four minutes against the jumping object catch an object at the far edge in under 500 ms, which is where Version G's single learner lands.
- [ ] Found, on Vehicle 2, eye then neck: over six seeds, the object is held in the middle cell for 12.3 s of 15 or better, which is what a neck that never moves scores — so that the neck is at worst no harm.
- [ ] The same six seeds, reported whatever they come to: both joints' travel, against Version C's 61 degrees; mean |eye|; and the rung each diagonal of each copy settled on, against the hand-cut ladder.
- [ ] Nothing in a copy reads a value. Its inputs are spikes and its only state is weights, eligibility, and what a coincidence cell is waiting on.

## Open questions

- **Is a rule that builds a table of any width one primitive, or a family?** A block of fixed size copied everywhere is a stronger claim than this one makes. The honest alternative is to give every array in the project the same number of lines, and the eye's nine against the propioceptor's ten was never argued for.
- **Does inhibition win a tie?** [Spec 010](010-cells.md) says what an inhibitory connection is and not what happens when it meets an excitatory one in the same tick. This circuit needs it settled, and the effector layer's lateral inhibition — still not decided to be wiring or something the layer does — is the same question wearing different clothes.
- **Who sets a wide reference?** One line of `r` was something a cortex might plausibly decide. A run of them is a statement about how much of its range a joint should be happy in, which spec 006 argues should follow from what moving costs. It is at least now in the one place a cortex can reach.
- **Should the two copies of a pair share what they learn?** A body is usually symmetrical and the copies are identical, so what one finds about its ladder is very likely true of the other. Sharing halves the teaching. It also builds in a symmetry that a body with one weak side would not have.
- **What does a copy do with a ladder it has never met?** Rungs whose bursts are wildly different in size — the neck's 64 degrees against 8 — make *trying one out* a different gamble on each joint. Whether exploration should be as eager on a joint where a wrong try throws the object off the eye is not something Version G had to ask.
- **Is the adapter row part of the body or of the sensory layer?** It sits between a sensor and the primitive and belongs cleanly to neither. If every change-reporting sensor wants one, it is a property of the socket and spec 001 should say so.
