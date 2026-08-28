# 007 — Vehicle 1, Version B: reflex based

- **Status:** draft
- **Date:** 2026-08-28
- **Supersedes / Superseded by:** —

The body of [spec 005](005-vehicle-1.md), driven by spikes for the first time, and put through the same experiment as [Version A](006-vehicle-1-a-pid.md).

The goal of this version is to evaluate how good can be a controller where the sensory layer and the effector layer are directly connected (without a cortex), so it's reflex based.

Also the connection comes hard wired, no learning is done.

For each cell in the retina there are a cell in the sensory layer that fires when the retina cell fires. This sensory cell is connected with an effector cell, it's is assumed a lateral inhibition mechanisms in the effector layer, so only one effector cell is active (the last activated one).



For this version the Version A retina will be used (it's fires in the busy cell). The spiking eye comes in version C.

## The wiring
Which effector a cell reaches is settled by the task rather than chosen. A cell left of the middle means the object is to the left, so the head has to turn left; and the further out the cell, the further the head has to go, so the further out the cell the faster the effector it wakes. The middle cell reaches nothing — there is nowhere to go from there.

| cell | turns | effector |
|------|-------|----------|
| 1 | left  | the fastest |
| 2 | left  | ↓ |
| 3 | left  | ↓ |
| 4 | left  | the slowest |
| **5** | **nothing** | **none** |
| 6 to 9 | right | the same, mirrored |

Which is four effectors on each actuator, exactly the set spec 003 already gives them, and it is what settles their frequencies: they are the speeds this vehicle picks between.

![Version B running the experiment](../docs/images/version_b.gif)

Watch the two effector rows of the raster: this vehicle moves because something spikes, which is the whole difference from Version A.
