# 004 — Simulator

- **Status:** draft
- **Date:** 2026-08-25
- **Supersedes / Superseded by:** —

## Goal
A program that runs a vehicle in a world, on a laptop, with no hardware. It exists so the other specs can be executed instead of only read: the sensors of [spec 001](001-neuromorphic-sensors.md), the bodies of [spec 002](002-vehicles.md) and [spec 005](005-vehicle-1.md) and the actuators of [spec 003](003-neuromorphic-actuators.md) all become code that either satisfies its acceptance criteria or does not.

## Time
A spike takes **10 ms** to happen. Nothing in the vehicle can go faster than that, which fixes two numbers that were open until now: no element can emit above **100 Hz**, and the refractory period `t_ref` of spec 001 cannot be shorter than 10 ms.

The simulator therefore advances in **ticks of 10 ms**, one loop, everything stepping together. A finer step would buy nothing: if the head turns in 10 ms jumps, the instant an object crosses from one cell to the next is quantised, but the retina cannot report that instant with any better resolution either, so the error is never more than the one tick that is already the limit of what the vehicle can perceive.

This is the one place where the simulator gets to differ from spec 001, which asks for no frame rate and no global clock, so it has to be kept honest:

- The tick appears in **no interface**. No component is handed a tick index; components are handed a time.
- Every sensing element still decides on its own state alone, and no stage waits for all elements before emitting.
- What crosses between components is still `(t, address, p)` events, exactly as in spec 001.

Kept that way, nothing downstream can tell the grid from real asynchrony, and the tick can be made finer later without touching anything but the clock. It is an implementation detail, not a design one — which is worth saying out loud, because it is exactly the kind of detail that gets optimised into an interface later.

## What crosses, and what must not
The levels of the architecture in spec 002 exchange spikes and nothing else. In particular:

- The cortex has **no access to the body state**. It cannot read the head angle or the contraction of an actuator. If it could, the propioceptive sensors would be pointless.
- The body has no access to the cortex either. An actuator sees spikes arriving and nothing more.
- The world state — where the object is — is set by whoever runs the experiment, never by the vehicle.

The simulator, as the observer, does see everything. That is the difference between the observer and the vehicle, and it is the whole reason a simulation is useful: the ground truth is available for checking what the vehicle worked out, and unavailable to the vehicle.

## Stack
- **Python 3.11+**, standard library. The event bookkeeping is a list and a `heapq` at most.
- **numpy** where arrays help — the retina, the correlations. Not needed to start.
- **pygame** for the live view: the vehicle drawn as in spec 002, moving, with the object draggable by mouse.
- **matplotlib** for spike rasters and offline analysis.
- **pytest** for the acceptance criteria.

No SNN framework — not Brian2, NEST, Nengo or snnTorch. They are built for thousands of neurons of standard types, and buy performance this project does not need; meanwhile the effector of spec 003, with its start and stop inputs, its own duration and its spontaneous firing while unwired, is not a standard neuron and would have to be fought into one. The neuron model is kept behind a small interface so that Brian2 can be brought in later for the cortex alone, if plasticity there turns out to want it.

No torch, no gym, and no physics engine: the body of [Vehicle 1](005-vehicle-1.md) is one angle.

## Structure
Modules mirror the levels of spec 002, so that a reader who knows the architecture can guess the file:

```
snnbot/
  params.py         every number from the specs, in one place
  clock.py          the tick, and the only thing that knows about it
  events.py         (t, address, p)
  world.py          where the object is
  body/
    retina.py       spec 001, change based
    proprioception.py   spec 001, threshold based
    actuator.py     spec 003
    vehicle1.py     the geometry: head angle from the two contractions
  layers/
    sensory.py
    effector.py     the effector cells, wired and unwired
  cortex/
  viz/
    live.py         pygame
    raster.py       matplotlib
  run.py
tests/
```

`params.py` matters more than it looks: every number in the other specs — `θ`, `t_ref`, step, range, relax time, effector frequencies and durations, the babbling rate, the degrees a retina cell covers — lives there and nowhere else, so the specs and the code can be checked against each other by reading one file.

## Recording
Every spike is recorded as it happens, with its source, so a run can be studied after it ends: rasters, correlations, and the exact stream that a test asserts on. A run is reproducible from its seed — the babbling of an unwired effector is random, so without a seed no two runs could be compared.

## Acceptance criteria

- [ ] Runs headless, with no display, and produces the same spike stream as a run with the live view.
- [ ] The same seed produces exactly the same spike stream, every time.
- [ ] No component receives a tick index; the tick can be changed in `clock.py` alone.
- [ ] The cortex cannot reach the head angle or any contraction level, by construction.
- [ ] Every acceptance criterion of specs 001 and 003 exists as a test, and passes.
- [ ] The pair of pictures in [spec 005](005-vehicle-1.md) is reproducible: with the object where it is drawn, turning the head 18 degrees yields `3 off` then `5 on`, and nothing else.

## Open questions

- How is the object moved during a run — a scripted path, the mouse, or both?
- What is the head's range of rotation, and what step size does an actuator take per spike? The suggestion is to pick the step so that one babble moves the head about one retina cell, which is the scale at which a movement and its sensory consequence can be tied together.
- Do the 10 propioceptive levels span a range comparable to the 81 degrees the eye covers? If they do, the two modalities have similar resolution, which is what the Sensory Layer needs.
- How is learning going to be judged? Something has to say whether the Sensory Layer found the correlation, and it cannot be the vehicle.
