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

### How often each of them decides

Version A of spec 005 runs its controller **every tick**, so that it is never favoured over the spiking vehicle by being asked more often. Here the two loops are not asked equally, and neither is asked as often as its body could act:

| | decides every | its fastest effector emits every |
|---|---|---|
| the eye | 10 ms | 2 ms |
| the neck | 50 ms | 10 ms |

Between turns a joint keeps going at whatever it was last told, so the interval is a real limit and not a detail. Spec 005 gives the rule it has to clear: a rate controller on a pure integrator starts to ring past `gain × interval = 1`. The eye sits at 0.02 and the neck at 0.02, both a long way under it.

The eye cancels the rate the neck is *holding*, so on beats that do not line up it spends part of every neck interval cancelling a rate that has already changed. Making the neck's interval a whole number of the eye's avoids that exactly — and measuring it says the exactness is not worth much: over the handover, where the gaze is meant to stand perfectly still, the slip is 0.18 degrees at worst and zero for most intervals, whether they line up or not. The neck's rate changes so slowly that ten milliseconds of it being stale is nothing. The tidiness is worth keeping; the argument for it is not.

Slowing the eye by ten and the neck by fifty costs nothing measurable — the object at the far edge of the eye is still caught in 980 ms, and the two joints still change places over the same five seconds — and it is slightly *better* at the task: 12.98 seconds in the middle cell against 12.37 over the experiment of spec 005.

The neck can afford the longer interval because of what it is chasing. How far the eye sits off its middle changes slowly by construction, so a loop that reads it five times less often than the eye reads the retina sees very nearly the same thing. With the eye held at 10 ms throughout:

| the neck decides every | catches in | eye / neck after 5 s | events while it stands | events while it follows | the experiment of spec 005 |
|---|---|---|---|---|---|
| 10 ms | 979 ms | 0.3° / 31.3° | 13 | 378 | 12.97 s |
| 20 ms | 979 ms | 0.3° / 31.4° | 13 | 378 | 13.01 s |
| **50 ms** | 980 ms | 0.3° / 31.4° | 9 | 378 | 12.98 s |
| 100 ms | 980 ms | 0.3° / 31.4° | 9 | 378 | 12.90 s |
| 200 ms | 979 ms | 0.2° / 31.3° | 9 | 374 | 12.98 s |

Nothing moves. Which says the interval is not what settles the neck's behaviour — `Kr` is — and that fifty is a comfortable choice rather than a limit.

### What the eye's interval does move

The last two columns are the eye's doing and not the neck's, and one of them changes by a factor of three hundred when the eye's own interval is changed:

| the eye decides every | events while it stands | events while it follows |
|---|---|---|
| 1 ms | 11 | **1** |
| 10 ms | 13 | **378** |

The vehicle behaves the same either way — it ends the run in the same posture with the object on the same cell. What differs is what the eye *says* while it does it, and the reason is a third number, the five milliseconds of [spec 005](005-vehicle-1.md) that a cell must be busy before it counts.

Following something that slides, the error is quantised, so the vehicle can only track by trembling against the edge of a cell: the object drifts out, the error jumps a whole cell, the eye lunges, the object comes back, the error is zero again. What the control interval sets is how long each tremble lasts. At a millisecond the object is out of the middle cell 1168 times and never for longer than **1 ms**, so the settling time swallows every one of them and the eye reports nothing. At ten it is out 118 times, for as long as 13 ms, and 95 of those get through.

So the three numbers — how often the controller decides, how wide a cell is, and how long a cell must be busy to count — are not independent, and this is the first vehicle in which two of them have been on opposite sides of the third. It costs Version A nothing, since it reads the cell as a number. It would not cost nothing in a version driven by the events themselves, which is every other one. Which is the chatter of spec 005 turning up again from the other side. A controller that decides a thousand times a second lunges at every crossing of a cell boundary and again on the way back; one that decides a hundred times a second lets a few of those pass, and the head trembles less for it.

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
| 0° | eye 17.7, neck 14.0 | eye 2.3, neck 29.4 | eye 0.3, neck 31.4 |
| 10° | eye 23.6, neck 8.0 | eye 11.8, neck 19.9 | eye 10.2, neck 21.5 |
| **20°** | eye 28.5, neck 3.0 | eye 21.1, neck 10.6 | **eye 20.1, neck 11.5** |

![Version A: the neck taking over what the eye was holding](../docs/images/vehicle2_a.gif)

Eleven seconds of the last row of that table, which is the vehicle as it runs: twenty degrees left to the eye to hold on its own. It catches the object with its eye alone, in 979 ms; the neck then takes over only what is past the twenty, so the pair settles with the eye holding 20.1 degrees and the neck 11.5; and then the object leaves, sliding away to the right at five degrees a second.

That last stretch is the two loops settling into the regime they settle into whenever something has to be watched rather than glanced at: **the eye does the following and the neck goes along behind it.** With no range set aside the neck ends up doing all of the following, and the eye parks at a fixed few degrees — the object's speed divided by `Kr`, five degrees for five degrees a second, and not a setting at all. With twenty degrees left to it the eye does the work instead and only hands over what runs past its range, which is why in the picture it comes back to within a degree of its middle while the neck holds the gaze.

The three rows underneath are what the vehicle itself has to go on: the eye fires a handful of times in the whole run, and the two propioceptive arrays — one sensor of ten firing at a time, drawn at the height of whichever it is — walk in opposite directions as the neck takes over. The traces at the bottom are the ground truth, which it does not have.

That picture is also what found the one bug this vehicle has turned up so far. The head's row fell silent as the eye came home, and it was not the drawing: the ten sensors of [spec 001](001-neuromorphic-sensors.md) ran from 0 to 10, then 11 to 20, and so on, leaving a unit of gap between each pair — so a contraction between 50 and 51 was read by nobody. A vehicle that moves in whole steps never lands in a gap, and none of them ever had; Version A turns its joints continuously and landed there about a tenth of the time, including at exactly the level an eye that has come back to its middle rests at. The ranges are half open now, which is the convention the cells of the eye were already tiled with.

The gaze is 31.5 degrees in every one of those cells and the object never leaves the middle of the eye. Nothing about the task is done better or worse by any of them. What the range settles is which joint did it.

### The eye should do the moving

Because the two joints are not equally expensive. The eye is a small thing on a light bar; the neck carries the eye, the bar and everything else. So the division of labour this vehicle wants is not an even one: **the eye should move as much as it can, and the neck should be spent only on what the eye cannot hold.** That is what the comfortable range is for, and it is the reason it is not zero.

It shows up as travel. The same experiment of spec 005, fifteen seconds, at four settings of `HEAD_COMFORT_DEG`:

| comfortable range | the eye travels | the neck travels | together | in the middle |
|---|---|---|---|---|
| 0° | 75.8° | 48.2° | 124.0° | 12.98 s |
| 10° | 61.9° | 18.4° | 80.3° | 13.02 s |
| **20°** | **55.4°** | **8.0°** | **63.4°** | 12.96 s |
| 45° | 49.9° | 0.0° | 49.9° | 12.97 s |

The task is the same in every row, to within a twentieth of a second. What changes is how much the body had to move to do it, and the wider the range left to the eye the less of everything is spent. Note that it is not a transfer: the eye's own travel falls too, from 75.8 degrees to 49.9. A neck that keeps hauling the eye home gives the eye something more to chase, so moving the slow joint makes the quick one work harder as well. At a comfortable range of zero this vehicle moves two and a half times as far as it needs to.

Which leaves the range itself as the one real trade in Version A: every degree of neck is spent buying back a degree of the eye's reach, and the vehicle needs that reach only when something goes further out than the eye alone can follow. Twenty degrees is where a human sets it, and this vehicle has no reason of its own to disagree.

There is one number missing before it could have one. The only currency this project has is the spike, and by that measure a degree of neck is *cheaper* than a degree of eye — 1.6 degrees a spike against 0.9 — which is backwards from the thing being argued. `ACTING_COSTS` of [spec 005](005-vehicle-1.md) charges the same for every effector spike wherever it lands. Charging for the joint rather than for the spike is what would let a vehicle work this out instead of being told it.

It shows as an ability rather than a posture as soon as the object goes somewhere the eye alone cannot follow. Sliding left at 10 degrees a second for nine seconds, from 18 degrees out to 108, the vehicle settles into following it with the neck at 10 degrees a second and the eye parked a fixed few degrees off its middle — which is what a human does with anything that has to be watched for longer than a glance. It keeps the object within a cell of the middle until the neck runs out of range at 80 degrees, and ends with the object in cell 4 and its eye still 15 degrees from its stop.

## Version B: the same circuit on each joint

Version A is two controllers reading numbers. This one is two layers of cells reading spikes, and they are the same layer twice.

**The eye's is [Version D of spec 005](005-vehicle-1.md), unchanged.** Seventy two correlation cells over the retina, a weight from every cell to every effector, credit handed out by the partition, and babbling for as long as no weight is worth anything.

**The neck's is that circuit with its inputs moved.** A correlation cell has a predecessor input and a successor input, and in the eye's layer they are wired to a cell of the retina going empty and another going busy. In the neck's they are wired to the head joint's **propioceptive array** — one of its ten sensors going out of range and another coming into it. So a cell of this layer does not say *the object moved from there to here*, it says *the eye did*; and better is not the object nearing the middle of the eye but the eye nearing the middle of its own range.

Nothing in the circuit knows the difference. That is the point of trying it.

Two things had to be settled to point it at a body instead of at the world, and both are properties of the array rather than of the circuit:

- **The array is tonic.** [Spec 001](001-neuromorphic-sensors.md) has it keep firing for as long as the level stays where it is, which says the same thing over and over, while a correlation cell asks when something *arrived*. So only the first ON after an OFF is passed on — a cell per sensor, firing on the edge of its input and deaf while it holds.
- **It has ten sensors and therefore no middle one.** The partition takes the middle to be 5.5: a place to be near rather than a cell to be in. Everything else about `outcome` is untouched, and the eye, with its nine, is judged exactly as before.

### One at a time, and the eye first

The eye's layer is taught alone and **frozen** before the neck's begins. Both halves of that are necessary, and for different reasons.

A neck that babbles while the eye is being taught makes the object appear to move, and Version D is taught against an object that never moves for exactly that reason — so that every change on the retina is the vehicle's own doing and the credit is clean. Taught together, the pair ends up worse than the eye on its own, and by a lot.

And a neck has nothing to learn from until the eye works. Contracting a neck actuator does not move the head joint at all: it swings the gaze, the object lands on another cell of the eye, the eye's own layer turns the eye, and only *then* does the neck's input move. The neck is learning the consequence of a consequence, through another learner, and if that learner does nothing the chain does not exist.

![Version B, one seed of it](../docs/images/vehicle2_b.gif)

Fifteen seconds of one of the better seeds: the eye near the middle of its range, the neck carrying the gaze, both sets of effectors firing. It is the same division of labour Version A settled into, arrived at this time by two layers of cells that were told nothing about each other.

### What the neck's layer learns

To ask what the layer found, rather than what the pair manage, the chain it depends on has to be made reliable — so the head is driven by the ground truth of Version A and only the neck is left to its layer. Taught 120 seconds against a still object, then put through the experiment of spec 005, over six seeds:

| the head on Version A, the neck as marked | in the middle | mean \|eye\| | both joints travel |
|---|---|---|---|
| a neck that never moves | 12.37 s of 15 | 16.6° | 50° |
| Version A's own neck | 12.96 s | 12.0° | 63° |
| the layer it learnt | 8.19 s | 3.5° | 1015° |

**The neck does bring the eye home** — 3.5 degrees against 16.6 — and of the sixteen or so cells that ever fire, 13 to 15 choose the side that does it. From nothing but its own babbling and a partition over its own sensors, the layer works out that the neck must turn the way the eye is turned. That is the same kind of claim Version E of spec 005 makes: not how well it did, but what it understood.

The other two columns are what it costs. It holds the object four seconds less, because every movement of the neck swings the gaze and nothing tells the eye it is coming — the eye finds out by the object turning up on a different cell, and by then it has been dragged most of a cell away. And it moves the body **sixteen times as far** as the controller does for a worse result, most of it in the neck, which is the joint Version A goes out of its way not to spend.

### What Version A lent it

Two things, and neither is a change to the circuit.

**The comfortable range, as wiring.** Version A leaves the eye twenty degrees to hold on its own and troubles the neck only past them, because the eye is the cheap joint. Here that cannot be a threshold anything reads, so it is which sensors the layer is wired to: the successor input of a cell reaches only the outer ones, and an eye wandering about the middle of its range wakes nothing at all. With ten sensors over ninety degrees the cut can only land on a sensor's edge, so twenty degrees comes out as the middle four of the ten — the propioception quantises the parameter the way the retina quantises the error.

**The vestibulo-ocular reflex, as spikes.** Version A hands the eye the rate the neck is taking. Here the neck's effectors reach the eye's actuators, and because a neck spike is worth 1.6 degrees and an eye spike 0.9 the wire cannot be one for one — it goes through a cell that adds up the weight and fires whenever the total has come to one, sixteen out for every nine in. That changes more than the gaze. Without it, contracting a neck actuator does not move the head joint at all, and the layer is learning through the retina and the eye's answer to it; with it, **a neck spike moves the head joint at once**, and the head joint is what this layer reads. The problem stops being the consequence of a consequence and becomes local.

On the same rig, six seeds:

| | in the middle | mean \|eye\| | both joints travel |
|---|---|---|---|
| as it was | 8.19 s | 3.5° | 1015° |
| with the comfortable range | 7.22 s | 14.8° | 475° |
| with the reflex | 12.26 s | 4.1° | 315° |
| **with both** | **12.30 s** | 13.0° | **306°** |

The reflex is what recovers the task: 12.3 seconds is the 12.37 a neck that never moves scores, so the spiking neck reaches Version A's result while doing what Version A's neck does. The comfortable range is what recovers the movement — on its own it cuts the travel by more than half at some cost to the task, and alongside the reflex it costs nothing. Between them the body moves 306 degrees where it moved 1015, which is still five times what the controller needs, and no longer twenty.

### On the eye it actually has

That was with a ground truth eye underneath. On the eye Version D produces, over six seeds taught 120 seconds a stage:

| | in the middle | best seed | both joints travel |
|---|---|---|---|
| the eye's layer alone | 4.60 s of 15 | 10.22 s | 927° |
| the neck as it was | 2.59 s | 6.36 s | 2014° |
| with the comfortable range | 1.05 s | 2.94 s | 714° |
| with the reflex | 4.78 s | 9.71 s | 2952° |
| **with both** | **5.14 s** | **11.72 s** | 1793° |

Which is the first time in this vehicle that a neck has been worth having: with the two of them the pair beats the eye on its own, on the average and by a wider margin at its best.

The middle two rows are worth reading before the last one. **Each change on its own buys one thing and spends the other.** The reflex buys the task — 2.59 seconds to 4.78 — and lets the neck thrash for free, since a neck movement no longer costs any gaze: 2952 degrees of travel, the most of any row here. The comfortable range buys the movement, cutting the travel to 714, and on its own it is the worst row in the table, because a neck that is woken only when the eye is already far out then swings it with a whole burst and there is nothing to cancel what that does to the gaze. Only together do they come out ahead of both.

The per-seed numbers say the rest: with both it scores 11.72, 9.73, 7.72, 0.96, 0.73 and 0.00. Three seeds learn it and three do not, which is not a spread so much as two outcomes. Every learnt version in this project has been like that, and none of them as plainly.

What is still wrong is the travel. Even at its best the pair moves 1524 degrees where Version A needs 63, and where it goes is into the neck. A vehicle that paid for moving would not do this, and it has no way to pay: `ACTING_COSTS` charges the same for every spike wherever it lands, and by that reckoning a degree of neck is cheaper than a degree of eye.

### What one command is worth

There is a second reason, and it is not about learning at all. An effector runs its own duration, so what a single command comes to is `frequency × duration × degrees per spike`:

| the neck's ladder | one burst | | the eye's ladder | one burst |
|---|---|---|---|---|
| 100 Hz for 400 ms | **64°** | | 500 Hz for 40 ms | 18° |
| 50 Hz for 600 ms | 48° | | 250 Hz for 80 ms | 18° |
| 20 Hz for 1000 ms | 32° | | 100 Hz for 200 ms | 18° |
| 5 Hz for 1000 ms | 8° | | 20 Hz for 500 ms | 9° |

The neck's fastest command moves it sixty four degrees — four fifths of its whole range — in one go, which is enough to throw the object clear off an eye that only spans eighty one. Version A never did that, because a controller sets a rate and decides again a millisecond later; a spiking layer picks a burst and lets it run to the end. The teeth on the gaze trace in the picture above are that, at the gentler end of the ladder.

Those durations were chosen to match how long a human head turn takes, and the frequencies to match how fast one goes. What nobody checked is what the two come to multiplied together, which is the only number that matters to something that decides once per movement. Keeping the speeds and shortening the bursts — 100 Hz for 100 ms, and so on down — gives 16, 16, 8 and 3 degrees, and on the ground truth rig it changes the vehicle's character entirely:

| | in the middle | mean \|eye\| |
|---|---|---|
| the ladder as specified | 6.96, 1.62, 9.45 s | 7.1, 6.7, 2.3° |
| the same speeds in shorter bursts | 11.99, 9.94, 10.66 s | 5.9, 24.8, 14.6° |

Twelve seconds is what a neck that never moves scores, so the task comes back almost entirely — and the eye is left further out. It is the same exchange as the VOR one seen from the other end: with nothing cancelling the gaze a neck movement causes, every degree the neck buys back for the eye is paid for in gaze, and **how far one command moves the neck is the exchange rate**. Neither end of it is free, and this vehicle has no way of pricing either.

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
- [ ] Version B's two layers are the same class of cell, told apart only by what they are wired to.
- [ ] The neck's layer never reads the retina, and the eye's never reads a propioceptive array.
- [ ] A sensor that goes on reporting the same level produces one arrival, not one per spike.
- [ ] Taught against a ground truth eye, most of the cells the neck's layer learns choose the side that brings the eye back towards the middle of its range.
- [ ] The eye's layer is frozen before the neck's is taught, and nothing teaches both at once.

## Open questions

- **What is the comfortable range, and does anything have to decide it?** Version A no longer needs anything to choose between the joints — the eye moves because it sees, the neck moves because the eye moved — but it is still handed a number saying how far off centre an eye may sit before its neck is worth troubling. What would settle that number honestly is a vehicle that pays for moving, the neck being the expensive joint: with `ACTING_COSTS` of spec 005 charging for spikes, a range that is too small is measurable as waste rather than a matter of taste.
- **How does the eye re-centre on spikes?** Version A does it by reading the head's angle as a number and handing the eye a copy of the neck's command. Neither is available to a spiking vehicle. The angle would have to come from the head's 1x10 propioceptive array, which resolves 9 degrees a level, so the giving back would happen in steps of a whole cell rather than smoothly. The copy of the command is worse: there is nothing to copy, the command being spikes to an actuator, so either the effectors reach the eye's own effectors directly — a reflex arc, which is what the real one is — or the vehicle needs the velocity sensor it has not got.
- **What would a VOR made of spikes be?** Version B measures what its absence costs — half the time on target. The arc it is missing goes from the neck's effectors to the eye's, and it is a reflex rather than anything learnt, so it could be wired. Whether it can instead be *learnt*, by a layer whose inputs are the neck's own effectors, is the more interesting question and the one this project would rather ask.
- **What should one command be worth?** [Spec 003](003-neuromorphic-actuators.md) gives an effector a frequency and a duration and says what each is for, and nothing anywhere says what their product should be. For a joint driven by a controller it does not matter; for one driven by a layer that picks a burst and lets it run, it is the whole of what a decision costs. The eye's ladder lands on one or two cells by luck rather than by design.
- **In what order should the two be taught?** Nothing in the vehicle says the eye must be schooled first, and everything in the measurements says it must. A rule imposed from outside is not a rule the vehicle has, so either something in it has to want the order, or the two have to be made teachable at once.
- **Can the sensory layer keep the two apart?** Its correlation cells tie a movement to what it did to the eye, and there are now two movements that do the same thing to it. Four propioceptive sensors say which one happened; whether the correlation cells can use that, or need a second input, is not settled.
- **Does babbling still work with four actuators?** Two unwired pairs babble at once, and the eye sees the sum. Some of the credit for what changed then belongs to a joint that happened to move at the same time, which is exactly the confusion Version D of spec 005 was taught against a still object to avoid.
- **Is one step size per joint enough?** The neck's 1.6 degrees was chosen to give it ±80 out of the same contraction range, not because anything wanted a coarser step. Giving it a longer contraction range instead would keep the step, and would say that the neck is a bigger muscle rather than a rougher one.
