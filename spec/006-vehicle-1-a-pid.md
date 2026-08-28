# 006 — Vehicle 1, Version A: PID controlled

- **Status:** draft
- **Date:** 2026-08-28
- **Supersedes / Superseded by:** —

The first way of driving the body of [spec 005](005-vehicle-1.md), and the only one that is not a brain.

This version acts as a 'ground truth' testing vehicle, instead of being controlled by neurons, its just controlled by a plain PID controller.

It runs the **same body** as the spiking version: the same T, the same joint, the same head range of ±40 degrees, the same two antagonist actuators. A ground truth that changed the body as well would leave any difference in behaviour unattributable to the brain, which is the one thing it exists to measure. What changes is the controller, and that the controller reads numbers where the other reads spikes.

Its sensors are analog:

- **Eye**: a number from 1 to 9, which cell is active — nothing at all when no cell is.
- **Eye angle**: a number from −40 to +40 degrees, positive when the eye is turned to the left, the same sense as everywhere else in this spec.

Its actuator is the same pair, so what the controller puts out is not a force but a **rate of turn**: degrees per second, positive turning the eye to the left. It is capped at the 80 degrees per second the spiking vehicle manages at its fastest — 100 Hz of spikes into a step of 0.8 degrees. A reference that can outrun the vehicle it is a reference for is not much of a reference.

The task is to bring whatever the eye sees to the middle of the eye, so the error is how far the active cell is from cell 5, in degrees:

```
error = (5 − active cell) × the degrees one cell covers
```

which is positive when the object sits left of centre and the eye has to turn left — positive — to catch it. Counting the error in degrees rather than in cells is what keeps `Kp` meaningful: the width of a cell is still a provisional number, and an error in cells would carry that number into the gain, so changing the width later would silently change how the vehicle behaves.

**When no cell is active the vehicle does nothing.** There is no error to speak of, and it stays where it is until something turns up in front of it.

## It is really a P controller
A PID has three terms and on this body two of them are zero, so it is worth saying which and why.

The plant is a pure integrator: what the controller sets is the rate the eye turns, so the angle is the running total of everything it has ever asked for. On such a plant proportional feedback alone converges exponentially and never overshoots — the eye slows as it closes in, and stops when the error does.

- The **integral** term has no steady-state error to remove, because the proportional term leaves none. All it can do is pile up on the way in and carry the eye past the target, and wind up against the ±40 degree stop whenever the object is out of reach.
- The **derivative** term would be differentiating a nine-step staircase: zero almost everywhere and an impulse at every cell crossing. It would add kicks, not damping, and there is nothing here to damp.

So `Ki = Kd = 0`, and what is left is

```
rate of turn = Kp × error
```

in degrees per second, capped at ±80. With the error in degrees, `Kp` is in units of one over seconds: it is a rate constant, and `1 / Kp` is roughly how long the eye takes to close the gap. **`Kp = 2`**, so the eye takes about half a second to catch what it is looking at.

The output is a plain continuous number — unlike the spiking vehicle, which moves the head in steps of 0.8 degrees, this one turns it smoothly.

The controller runs once every **10 ms**, the same tick as the simulator of [spec 004](004-simulator.md), so that it gets to act exactly as often as the spiking vehicle does and neither is favoured by being asked more often. The interval is a parameter and can be changed — a controller that runs more slowly than the body moves is a different thing to compare against, and a fair one to want.

Changing it is not free, though. The eye slows down as the error shrinks, but only at each tick: between ticks it keeps turning at whatever rate it was last told. So the eye closes `Kp × tick` of the gap on every step, and the pair has a limit — past `Kp × tick = 1` it starts overshooting, and past 2 it never settles. At 10 ms there is room to spare, since that would need a `Kp` above 100. At a tick of a second it would not: `Kp = 2` would be enough to break it.

## Running the experiment
![Version A running the experiment](../docs/images/version_a.gif)

Two things worth watching in it, both of them consequences of an error that can only take the values a whole number of cells allows.

The eye comes to rest with the object at the **edge** of the middle cell rather than at its centre: the error is zero anywhere inside cell 5, so the eye stops the moment the object crosses in.

And while the object is creeping left the eye **chatters at the cell boundary** — look at how the eye's row of the raster fills up. Inside cell 5 the error is zero and the eye stands still while the object drifts out of it; the moment it crosses into cell 4 the error jumps a whole cell at once, the eye lunges at three times the speed the object is moving, and puts it back where it was. The head ends up trembling against the edge of a cell, and the eye fires about a hundred times a second over an object that is barely moving.

Which is worth knowing before the number that judges a run is settled: this vehicle is at its noisiest exactly where it is doing best. A faster object is easier on it — it simply settles a cell behind and stays there. Curing the chatter would mean hysteresis, or a dead zone around zero error, and neither is decided yet.

## Open questions

- What counts as success? Time taken to bring the object to cell 5, the fraction of a run spent there, something else. Until that is settled Version A is a vehicle that works, but not yet a measurement anything can be compared against.
