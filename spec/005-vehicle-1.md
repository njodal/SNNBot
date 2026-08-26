# 005 — Vehicle 1 - a moving eye

- **Status:** draft
- **Date:** 2026-08-25
- **Supersedes / Superseded by:** —

The first of the series of [spec 002](002-vehicles.md), and the simplest one. 

This vehicle has:

- sensors
  - one very simple eye: just an array of 9 cells (1x9) that can have some kind of lateral inhibition (not modeled) that only allow to perceived one cell ON maximum. this is to simulate viewing a source of light.
  - two propioceptive sensors (1x10 sensors each) to sense the level of contraction of each actuator
- actuators
  - one attached to the right of eye and the other to the left (agonist and antagonist) that move the eye.

So the vehicle can't move, it just can move the eye to both sides.

Its shape is a T: the eye is the head, the joint is where the head meets the stem, and both actuators run from the middle of each half of the head down to the middle of the base. The black cell is an object standing in front of the eye, seen here by cell 3:

![Vehicle 1 at rest](../docs/images/vehicle1_layout.png)

Contracting one actuator stretches the other and the head turns around the joint, so the eye ends up looking to that side:

![Vehicle 1 with the head turned](../docs/images/vehicle1_tilted.png)

The object has not moved — the head has. If each cell covers 9 degrees of the world (a number still to be fixed), turning 18 degrees to the left slides the object two cells along the eye, from cell 3 to cell 5: the eye has centred what it was looking at off to one side.

Those angles are measured from the joint, not from each cell: the eye takes whatever it is looking at to be far enough away that where along the head a cell happens to sit makes no difference to the direction it sees the object in. Something close by — a couple of head lengths away — would break that, and would need the parallax worked out cell by cell. This vehicle does not do it.

Which is worth keeping in mind when reading [spec 001](001-neuromorphic-sensors.md): between those two pictures the eye fires `3 off` and `5 on`, and yet nothing in the world moved. To the retina, moving the eye and the world moving look exactly the same.
