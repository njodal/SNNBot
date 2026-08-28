# 008 — Vehicle 1, Version C: reflex with a neuromorphic retina

- **Status:** draft
- **Date:** 2026-08-28
- **Supersedes / Superseded by:** —

[Version B](007-vehicle-1-b-reflex.md) again, on the body of [spec 005](005-vehicle-1.md), with the eye it should have had all along.

This is similar to Version B, but this time the retina is full neuromorphic, so it only respondo to changes.

Remember that in this kind of retina there are two sensor per cell, one that fires when cell moves from empty to busy (ON) and other for busy to empty (OFF). So if the busy cell moves from cell 1 to cell 3, two events will be triggered: the first is the OFF sensor of cell 1 and later the ON sensor of cell 3 (order is important).

Note this version is incapable of centering an object that isn't moving. This restriction will be solved in later versions.

The sensory layer is composed of correlation cells which have two inputs, one (the predecessor input) to an OFF sensor, and a successor to a ON one, so the fire cells when there is a move from one cell to the other. This layer is fully connected, so there are 72 cells (9 sucessor input times 8 possible predessors).

Each of this cells is connected to an effector cell.

## The order the cells read
The two events of a move only come in an order if something makes them. With the cells of the eye covering the world edge to edge and the object a point, it leaves one cell in the very instant it reaches the next, and both events carry the same time — a correlation cell waiting for its predecessor to arrive first would wait forever.

So a cell reports **becoming busy one cycle after it happens**, and becoming empty at once. A move is then always an OFF and, a cycle later, an ON, which is what this spec and [spec 001](001-neuromorphic-sensors.md) have described from the start.

That is not the whole of it either. Cells that share their edges leave an object standing on one of them inside both at once, so the cell being reached reports before the cell being left and the lag does no more than cancel that head start out. The cells are half open — each takes its own edge and leaves the next one to its neighbour — so an object is never in two of them.

## The wire out of each cell
Every one of the 72 has its own wire to an effector, and several name the same one: they are moves that end in the same place, having started in different ones. Any one of them is enough to wake it.

A cell that ends in the middle is the exception worth naming. Waking nothing there stops the head dead the moment the object arrives, which is precisely what leaves it drifting straight back out again, so those cells go on the way the object was going, gently. Gently needs an effector the ladder of spec 003 does not have: its slowest runs the head some eight degrees, near enough a whole cell, and a nudge that size overshoots every time. Hence a fifth, at 5 Hz — four degrees in its run, about the speed of the thing it is keeping up with.

![Version C running the experiment](../docs/images/version_c.gif)

The six seconds of nothing at the start are what an object that will not move looks like from in here. Which makes the babbling of [spec 002](002-vehicles.md) the only way this vehicle could ever start on its own.

Watch the eye's row of the raster afterwards: it stays nearly empty. Over the fifteen seconds this vehicle spends a quarter of the eye events Version B does and a tenth of Version A's, and it is still the one that ends up closest to the object.
