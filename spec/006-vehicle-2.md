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

In a human the answer is usually given as a threshold on the world: gaze shifts under about 20 degrees are made by the eye alone, and past that the head is recruited. Then the two come apart again — the eye lands first, the head is still arriving, and the eye rolls back towards the middle of its range while the gaze stays where it was put.

That second half is the useful one. A head that has re-centred its eye has spent its neck to buy back the eye's range, and is ready for the next thing to appear anywhere. It is also what makes the two joints worth having: not a longer reach — the neck alone would give that — but a fast joint that is always near the middle of its travel, kept there by a slow one.

And it turns out to be the whole of it. Nothing has to decide which joint moves, because the two are not choosing between the same jobs.

## Version A: a PID on each joint

The same thing Version A of [spec 005](005-vehicle-1.md) is — a ground truth, reading the active cell as a plain number and turning the body itself, with no spike anywhere in it — but there are two joints to drive now, so there are two controllers, and they do not read the same thing.

**The eye keeps Vehicle 1's, unchanged.** The same proportional law, the same `Kp`, the same error in degrees from the middle of the eye. One thing follows the body rather than the controller: the cap. Vehicle 1's is 80 degrees a second because that is what its fastest effector manages, and by the same rule the head joint's is 450.

**The neck's does not read the eye's picture at all.** What it reads is the head joint's own angle — how much of the looking the eye is doing — and what it asks for is that the neck take that over:

```
neck rate = Kr × how far the eye is outside its comfortable range
```

`Kr` is 1 per second against the eye's 2, so the eye is given its range back in about a second and catches up with anything in half of one: giving the range back is never allowed to compete with the catching. Below `HEAD_COMFORT_DEG` the neck asks for nothing — an eye a few degrees off its middle is not worth moving a neck for, and a human's sits there all day — and past it, what is acted on is what is left once that range is subtracted, so the neck starts from nothing at the edge instead of lurching into motion.

So each of the three parts has one job. **The eye decides where to look, and is the only thing that sees. The neck decides how the looking is held, and is the only thing that reads the eye. The VOR, which is not a controller at all but a wire, keeps the second from disturbing the first.**

### What the neck is not told, and why

It was told, at first. The neck had a second law reading the same retina as the eye, deaf until the object was more than 20 degrees out and helping to swing the gaze past that. It worked. It is also what a human does, and the version of the threshold everybody quotes.

It was taken away because it gave the neck two inputs and two jobs, and because the threshold it needed was a fact about the world that nothing inside the vehicle could justify. What that costs is small and worth writing down: an object at the far edge of the eye is caught in 979 ms instead of 925, and on the experiment of spec 005 nothing changes at all, the object never getting far enough out for the second law to have spoken.

What it buys is that the threshold left over is about the eye's own posture. Which is what the human number means underneath: the head is not recruited because the target is far away, it is recruited because the eye has ended up outside the range it is content to work in. The two coincide when the eye starts centred, which is why it is usually quoted as a gaze shift — and the propioceptive version is the one that stays right when it does not.

### The eye has to give way, and has to be told

A neck that turns while the gaze is meant to stay put needs the eye to turn back by exactly as much. The eye cannot work that out from what it sees. Inside a cell there is no error to see — that is what a nine degree cell means — so it would not notice the gaze drifting until the object had crossed into the next one, and would then lunge back a whole cell at once. That is the chatter of Version A of spec 005, this time self-inflicted, and it is what the vehicle does if left to find out for itself:

| over five seconds | out of the middle cell | events the eye fired |
|---|---|---|
| the eye told what the neck is doing | 0 ms | 9 |
| the eye left to see for itself | 1128 ms | 260 |

So the eye is handed the neck's rate and cancels it — the whole of it, the neck having nothing else to say. That is a **vestibulo-ocular reflex**, and one thing about this one has to be admitted: a real VOR reads a canal, a sensor of head velocity, which this vehicle has not got, its propioceptive arrays reporting a position. What stands in for the canal here is a copy of the command, so this is the first thing in the project that is fed forward rather than sensed.

### What it does

The object stands still at 36 degrees, at the far edge of the eye. It is caught in 979 ms whatever the comfortable range is set to, the eye doing that part alone. What the range settles is where the two joints come to rest afterwards:

| `HEAD_COMFORT_DEG` | at 1 s | at 3 s | at 5 s |
|---|---|---|---|
| 0° | eye 17.2, neck 14.3 | eye 2.3, neck 29.2 | eye 0.3, neck 31.2 |
| 10° | eye 23.2, neck 8.3 | eye 11.8, neck 19.7 | eye 10.2, neck 21.3 |
| 20° | eye 28.4, neck 3.1 | eye 21.1, neck 10.4 | eye 20.2, neck 11.3 |

The gaze is 31.5 degrees in every one of those cells and the object never leaves the middle of the eye. Nothing about the task is done better or worse. What the range buys is how much of its travel the eye has left when the vehicle is done: all of it at zero, half of it on one side at twenty. It is a decision about posture and not about performance, which is the sort of number this project should be explicit about having chosen.

It shows as an ability rather than a posture as soon as the object goes somewhere the eye alone cannot follow. Sliding left at 10 degrees a second for nine seconds, from 18 degrees out to 108, the vehicle settles into following it with the neck at 10 degrees a second and the eye parked a fixed few degrees off its middle — which is what a human does with anything that has to be watched for longer than a glance. It keeps the object within a cell of the middle until the neck runs out of range at 80 degrees, and ends with the object in cell 4 and its eye still 15 degrees from its stop.

## Acceptance criteria

- [ ] The body has four actuators in two antagonist pairs, and four propioceptive sensors, one per actuator.
- [ ] The eye is the one of Vehicle 1, unchanged, and it is reached by neither joint directly: what it reports is the sum of the two angles and nothing else.
- [ ] With both joints at 9 degrees, the object of the pictures reads `3 off` then `5 on`, exactly as Vehicle 1 does at 18 degrees.
- [ ] The head joint stops at ±45 degrees, the neck at ±80, and the gaze therefore at ±125.
- [ ] The head's fastest effector turns the eye at 450 °/s and its slowest at 18, the neck's at 160 and 8.
- [ ] No effector exceeds the 500 Hz the refractory period of spec 004 allows.
- [ ] The cortex still cannot read either angle or any contraction, by construction — spec 004 stands unchanged.
- [ ] Version A drives both joints without a spike passing anywhere in it.
- [ ] Neither of its joints turns faster than its own fastest effector, and neither leaves its range.
- [ ] Its neck reads the head joint's angle and nothing else: which cell is busy makes no difference to what it asks for.
- [ ] With no comfortable range set aside, the neck ends up holding the whole gaze and the eye ends within a couple of degrees of its own middle.
- [ ] It does that without the object leaving the middle cell of the eye.
- [ ] Either joint may turn back on itself; the gaze may not.

## Open questions

- **What is the comfortable range, and does anything have to decide it?** Version A no longer needs anything to choose between the joints — the eye moves because it sees, the neck moves because the eye moved — but it is still handed a number saying how far off centre an eye may sit before its neck is worth troubling. What would settle that number honestly is a vehicle that pays for moving, the neck being the expensive joint: with `ACTING_COSTS` of spec 005 charging for spikes, a range that is too small is measurable as waste rather than a matter of taste.
- **How does the eye re-centre on spikes?** Version A does it by reading the head's angle as a number and handing the eye a copy of the neck's command. Neither is available to a spiking vehicle. The angle would have to come from the head's 1x10 propioceptive array, which resolves 9 degrees a level, so the giving back would happen in steps of a whole cell rather than smoothly. The copy of the command is worse: there is nothing to copy, the command being spikes to an actuator, so either the effectors reach the eye's own effectors directly — a reflex arc, which is what the real one is — or the vehicle needs the velocity sensor it has not got.
- **Can the sensory layer keep the two apart?** Its correlation cells tie a movement to what it did to the eye, and there are now two movements that do the same thing to it. Four propioceptive sensors say which one happened; whether the correlation cells can use that, or need a second input, is not settled.
- **Does babbling still work with four actuators?** Two unwired pairs babble at once, and the eye sees the sum. Some of the credit for what changed then belongs to a joint that happened to move at the same time, which is exactly the confusion Version D of spec 005 was taught against a still object to avoid.
- **Is one step size per joint enough?** The neck's 1.6 degrees was chosen to give it ±80 out of the same contraction range, not because anything wanted a coarser step. Giving it a longer contraction range instead would keep the step, and would say that the neck is a bigger muscle rather than a rougher one.
