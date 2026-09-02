# 006 — Vehicle 2 - an eye on a neck

- **Status:** draft
- **Date:** 2026-09-01
- **Supersedes / Superseded by:** —

The second of the series of [spec 002](002-vehicles.md). It is [Vehicle 1](005-vehicle-1.md) with one thing added: a second joint underneath the first, so that the eye is carried on a neck.

This vehicle has:

- sensors
  - the same eye as Vehicle 1: an array of 9 cells covering 9 degrees of the world each, at most one of them busy
  - four propioceptive sensors (1x10 each), one per actuator
- actuators
  - four, in two antagonist pairs: one pair turns the eye on the head joint, the other turns the whole neck on the base.

It still cannot go anywhere. What it has that Vehicle 1 has not is a second way of pointing the same eye.

## The body

Its shape is a T standing on another T. The upper one is Vehicle 1 entire — the eye is the head, the head joint is where it meets the neck, and the two head actuators run from the middle of each half of the eye down to the neck. The lower one is new: the neck is a rigid link from the head joint down to the base, with a cross bar of its own near the bottom, and the two neck actuators run from the ends of that bar down to the base. The black cell is an object standing in front of the eye, seen here by cell 3:

![Vehicle 2 at rest](../docs/images/vehicle2_layout.png)

The neck actuators reach the base on either side of the joint, and not the joint itself. An actuator that ends at the pivot keeps its length whatever the pivot does, so it could never turn it — the head actuators get away with converging on a single point because that point is on the neck, far below the joint they act on. It is the first piece of geometry in this project that had to be got right rather than merely drawn.

## Both joints, one gaze

Turning either joint turns the eye, so what the eye ends up looking at is the sum of the two angles:

```
gaze = neck angle + head angle
```

Here both are turned 9 degrees to the left, which is 18 degrees of gaze:

![Vehicle 2 with both joints turned](../docs/images/vehicle2_tilted.png)

That is the same 18 degrees as the turned picture of Vehicle 1, and it has the same consequence: the object has not moved, and it slides two cells along the eye, from cell 3 to cell 5.

Which is the whole difficulty of this vehicle, and it is worth stating as plainly as the pictures do. **The retina cannot tell the two joints apart.** Cell 3 going empty and cell 5 going busy is what a neck of 18 degrees looks like, and a head of 18 degrees, and any of the infinitely many pairs in between — including the two turned against each other by more than that and cancelling. One percept, many postures. Vehicle 1 had a body with one degree of freedom and one thing to see it with; this one has two degrees of freedom and the same one thing, so for the first time the vehicle's own state is not recoverable from what it sees.

The propioceptive sensors are what is left to tell them apart, four of them now instead of two, and telling them apart is their whole job. This is also the first vehicle where the sensory layer's task — tie a movement to what it did to the world — has two sources of movement to keep separate.

## The two joints are not alike

If both joints were the same, the redundancy would be the only new thing here and the choice between them arbitrary. They are not the same, in the two ways they are not the same in a human: **the eye is quick and short of travel, the neck slow and long**. The numbers below are the human ones, rounded, then what they become in the units of [spec 003](003-neuromorphic-actuators.md) and [spec 004](004-simulator.md).

| | human eye in the orbit | human head on the neck |
|---|---|---|
| range | ±45 to 50° | ±70 to 80° |
| range in customary use | ±15 to 20° | ±45° |
| peak speed | 300 to 500 °/s, saturating near 700 | 100 to 200 °/s in natural gaze shifts |
| how long one movement takes | 30 to 100 ms | 300 to 800 ms |
| latency | about 200 ms | starts 20 to 80 ms *after* the eye |
| rate of the motoneurons | bursts of 400 to 1000 spikes/s | 10 to 30 Hz sustained |

The eye is three to four times the faster and the neck close to twice the travel. Those two ratios are what this vehicle is asked to keep:

| | head joint | neck joint |
|---|---|---|
| range | ±45° (5 cells) | ±80° |
| range in customary use | ±20° | ±45° |
| degrees per spike | 0.9 | 1.6 |
| fastest effector | 500 Hz for 40 ms → **450 °/s**, a jerk of 16° | 100 Hz for 400 ms → **160 °/s** |
| the ladder, Hz × ms | (500, 40) (250, 80) (100, 200) (20, 500) | (100, 400) (50, 600) (20, 1000) (5, 1000) |
| one propioceptive level | 9°, one cell of the eye | 16°, near two |
| one babble of 0.5 s at 20 Hz | 9°, one cell | 16°, near two |

Three things fall out of that table, and each is a decision rather than an implementation detail.

**The eye reaches the ceiling of spec 004.** 450 degrees a second at 0.9 per spike is 500 Hz, which is exactly `MAX_RATE_HZ`, the rate the 2 ms refractory period allows and nothing more. Spec 004 says that nothing built so far comes near it and that the fastest effector runs at 100 Hz; the eye of this vehicle is the first thing to touch it. That is the right place to be, because it is where the biology is: the burst neurons that drive a real saccade fire at 600 to 1000 spikes a second and are the fastest thing in the motor system. The alternative — a bigger step at a lower rate — buys the same speed and loses the tie between one spike and one cell, so it is not taken.

**A saccade is a jerk, not a movement that is held.** The head's fastest effector runs for 40 ms and no longer, which is the whole of its command: 18 spikes, 16 degrees, and over before anything could stop it. That is what the `duration` of spec 003 is for, and this is the first vehicle to use it as biology does.

**The two joints are coherent internally and coarse against each other.** The head's step, its propioceptive level and its babble all come to about one cell of the eye, which is the scale spec 004 asks for. The neck's all come to about two. So the neck is not sloppier in some places and sharp in others — it is uniformly the coarser joint, which is also true of a human, whose sense of where the eye is sitting is barely propioceptive at all. What it costs is that the two modalities no longer have the comparable resolution spec 004 was careful to give them: for the neck, one level of contraction spans nearly two cells of retina.

## What decides which joint moves

Nothing in the vehicle yet. In a human the answer is a threshold rather than a share: gaze shifts under about 20 degrees are made by the eye alone, and past that the head is recruited and the eye rides along. Then the two come apart again — the eye lands first, the head is still arriving, and the eye rolls back towards the middle of its range while the gaze stays where it was put.

That last part is the useful half. A head that has re-centred its eye has spent its neck to buy back the eye's range, and is ready for the next thing to appear anywhere. It is also what makes the two joints worth having: not a bigger range — the neck alone would give that — but a fast joint that is always near the middle of its travel, kept there by a slow one.

Which of those the vehicle should do, and what should decide, is the open question of this spec. Version A is handed the answer, the way Version D of [spec 005](005-vehicle-1.md) was handed the partition it learnt from: it is told the threshold rather than finding it.

## Version A: a PID on each joint

The same thing Version A of [spec 005](005-vehicle-1.md) is — a ground truth, reading the active cell as a plain number and turning the body itself, with no spike anywhere in it — but there are two joints to drive now, so there are two controllers.

**The eye keeps Vehicle 1's, unchanged.** The same proportional law, the same `Kp`, the same error in degrees from the middle of the eye. One thing follows the body rather than the controller: the cap. Vehicle 1's is 80 degrees a second because that is what its fastest effector manages, and by the same rule the head joint's is 450.

**The neck gets the same controller with a dead zone.** Below twenty degrees of error it returns nothing at all; above it, it acts on what is left once the threshold is subtracted rather than on the whole error, so that at the boundary the neck starts from nothing instead of lurching into motion. Its cap is the neck's own 160 degrees a second.

Both are still proportional and nothing more, for the reason spec 005 gives: the plant is a pure integrator either way, and an integral term against a dead zone would be the worst of both — winding up in the silence and carrying the neck past the target when it finally speaks.

Neither controller is told what the other is doing, and neither could be told usefully: what they share is an error of **gaze**, which is nobody's angle in particular. What keeps them from fighting is that both drive the sum the same way, and that the neck gives up first.

The threshold lands on the retina as a staircase, the error being one. With cells of nine degrees, the neck answers to cells 1, 2, 8 and 9 and to nothing else.

| object at | head ends | neck ends | gaze |
|---|---|---|---|
| 9° (cell 4) | 4.5° | 0.0° | 4.5° |
| 18° (cell 3) | 13.5° | 0.0° | 13.5° |
| 27° (cell 2) | 21.6° | 0.9° | 22.5° |
| 36° (cell 1) | 28.3° | 3.3° | 31.5° |

### The neck is recruited, and then hardly used

That last column is the result, and it is worth reading before the next version is designed. The neck moves — the threshold works — but it contributes three degrees out of thirty. The eye is three times the faster, so it removes the error before the neck has gone anywhere, and the neck stops when the error does. Two loops on one error, and the quick one wins.

Nothing here is broken. The gaze is where it should be, and this is the shortest path to it. What is missing is the half of the human pattern that comes after: the head goes on turning once the eye has landed, and the eye rolls back towards the middle of its range while the gaze stays put. The neck spends itself to buy the eye's range back.

That cannot come out of the error these two share. A gaze that does not change produces no events at all on a change-based eye, so there is nothing in the retina to ask for a movement of the neck that is cancelled by a movement of the eye. It would have to be driven by the head joint's own propioceptive sensors — a second loop with a different input, closing on the eye's angle rather than on what the eye sees.

There is a plainer version of the same point. The eye alone reaches ±45 degrees and the retina spans ±40, so anything this vehicle can see at rest, it can centre without its neck. Within the experiment of spec 005 the neck is never *needed* — which is a consequence of the numbers, not of the controller. A human's eye can reach ±45 too and habitually uses ±20, and `HEAD_COMFORT_DEG` is in `params.py` for exactly that reason.

### Giving the range back

So the neck gets a second law, and its input is not the world. It is the head joint's own angle: not where to look, which the first law already settles, but how much of the looking the eye is doing. What it asks for is that the neck take that over.

```
neck rate = Kp × (error beyond the threshold) + Kr × the head's angle
```

The first term closes on the world and the second on the body, and it is the first loop in this project to close on the body at all. `Kr` is 1 per second against the eye's 2, so the eye is given its range back in about a second and caught up with anything in half of one: giving the range back is never allowed to compete with the catching.

### Which needs the eye to give way, and to be told

A neck that turns while the gaze is meant to stay put needs the eye to turn back by exactly as much. The eye cannot work that out from what it sees. Inside a cell there is no error to see — that is what a nine degree cell means — so it would not notice the gaze drifting until the object had crossed into the next one, and would then lunge back a whole cell at once. That is the chatter of Version A of spec 005, this time self-inflicted, and it is what the vehicle does if left to find out for itself:

| over five seconds | out of the middle cell | events the eye fired |
|---|---|---|
| the eye told what the neck is doing | 0 ms | 9 |
| the eye left to see for itself | 1128 ms | 260 |

So the eye is handed the neck's re-centring rate and cancels it. That is a **vestibulo-ocular reflex**, and two things about this one are worth saying out loud. It is subtracted from the re-centring term only: cancelling the recruiting term as well would undo the neck's contribution to every gaze shift and make recruiting it pointless — which is why a real VOR is suppressed during one. And a real VOR reads a canal, a sensor of head velocity, which this vehicle has not got: its propioceptive arrays report a position. What stands in for the canal here is a copy of the command, so this is the first thing in the project that is fed forward rather than sensed.

### What it does

The object stands still at 36 degrees. The vehicle catches it in under a second either way; what differs is what happens after that.

| | at 1 s | at 2 s | at 4 s |
|---|---|---|---|
| the two PIDs alone | eye 28.3°, neck 3.3° | eye 28.3°, neck 3.3° | eye 28.3°, neck 3.3° |
| with the second loop | eye 15.2°, neck 16.4° | eye 5.6°, neck 25.9° | eye 0.8°, neck 30.8° |

The gaze is 31.5 degrees in every one of those cells and the object never leaves the middle of the eye. Nothing about the task is done better. What has changed is that the vehicle ends up **ready**: its quick joint is back in the middle of its travel, with its whole ±45 available for whatever turns up next, and the slow joint is holding the posture. That is what the two joints were for.

It shows as an ability rather than a posture as soon as the object goes somewhere the eye alone cannot follow. Sliding left at 10 degrees a second for nine seconds, from 18 degrees out to 108:

| | where it ends up |
|---|---|
| the two PIDs alone | eye pinned at its 45° stop, neck 40.5°, the object out at cell 2 |
| with the second loop | eye 15.9°, neck at its 80° stop, the object at cell 4 |

Both lose it in the end — 108 degrees is past what this body can reach — but the one that kept giving its range back follows ten degrees further and is still nearly centred when the other has the object three cells off and nothing left to turn.

## Acceptance criteria

- [ ] The body has four actuators in two antagonist pairs, and four propioceptive sensors, one per actuator.
- [ ] The eye is the one of Vehicle 1, unchanged, and it is reached by neither joint directly: what it reports is the sum of the two angles and nothing else.
- [ ] With both joints at 9 degrees, the object of the pictures reads `3 off` then `5 on`, exactly as Vehicle 1 does at 18 degrees.
- [ ] The head joint stops at ±45 degrees, the neck at ±80, and the gaze therefore at ±125.
- [ ] The head's fastest effector turns the eye at 450 °/s and its slowest at 18, the neck's at 160 and 8.
- [ ] No effector exceeds the 500 Hz the refractory period of spec 004 allows.
- [ ] The cortex still cannot read either angle or any contraction, by construction — spec 004 stands unchanged.
- [ ] Version A drives both joints without a spike passing anywhere in it.
- [ ] Its neck stands still for anything the eye can reach on its own, and moves for what it cannot.
- [ ] Its neck stops as soon as the error falls back inside the threshold, and the eye finishes alone.
- [ ] Neither of its joints overshoots, and neither turns faster than its own fastest effector.
- [ ] With the second loop, the neck ends up holding the gaze and the head joint ends within a couple of degrees of its own middle.
- [ ] It does that without the object leaving the middle cell of the eye.
- [ ] The eye is given the re-centring rate and not the recruiting one: a gaze shift is not cancelled.

## Open questions

- **What recruits the neck?** The human threshold of about 20 degrees is the obvious first thing to try, but a threshold is a decision made somewhere, and there is no cortex here to make it. Whether it can fall out of the two ladders instead — the head's effectors simply running out of range while the neck's do not — is the more interesting version of the question.
- **How does the eye re-centre on spikes?** Version A does it by reading the head's angle as a number and handing the eye a copy of the neck's command. Neither is available to a spiking vehicle. The angle would have to come from the head's 1x10 propioceptive array, which resolves 9 degrees a level, so the giving back would happen in steps of a whole cell rather than smoothly. The copy of the command is worse: there is nothing to copy, the command being spikes to an actuator, so either the effectors reach the eye's own effectors directly — a reflex arc, which is what the real one is — or the vehicle needs the velocity sensor it has not got.
- **Can the sensory layer keep the two apart?** Its correlation cells tie a movement to what it did to the eye, and there are now two movements that do the same thing to it. Four propioceptive sensors say which one happened; whether the correlation cells can use that, or need a second input, is not settled.
- **Does babbling still work with four actuators?** Two unwired pairs babble at once, and the eye sees the sum. Some of the credit for what changed then belongs to a joint that happened to move at the same time, which is exactly the confusion Version D of spec 005 was taught against a still object to avoid.
- **Is one step size per joint enough?** The neck's 1.6 degrees was chosen to give it ±80 out of the same contraction range, not because anything wanted a coarser step. Giving it a longer contraction range instead would keep the step, and would say that the neck is a bigger muscle rather than a rougher one.
