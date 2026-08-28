# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
The term *neuromorphic* sensors in this contexts refers to sensors that senses some value from the environment and fires *spikes* (events) to be send to upper level of the Spike Neural Network.

See [spec 001](spec/001-neuromorphic-sensors.md).

## Neuromorphic actuators
An actuator that can only move one way — it contracts — driven by spikes alone: it is connected to several neurons called *effectors*, and each spike contracts it one step, so the frequency the effectors fire at is what sets how fast it moves.

See [spec 003](spec/003-neuromorphic-actuators.md).

# Vehicles
Following the Braintenberg tradition, we will define a series of Vehicles, from the simplest one to more sophisticated.

See [spec 002](spec/002-vehicles.md).

# Specs
Design specifications live in [`spec/`](spec/).

- [001 — Neuromorphic sensors](spec/001-neuromorphic-sensors.md): what counts as a
  neuromorphic sensor in this project, and the event format all sensors emit.
- [002 — Vehicles](spec/002-vehicles.md): the architecture every vehicle shares,
  and the list of the vehicles themselves.
- [003 — Neuromorphic actuators](spec/003-neuromorphic-actuators.md): what drives an
  actuator, and how the effectors set the speed it moves at.
- [004 — Simulator](spec/004-simulator.md): how the vehicles are run on a laptop —
  the time base, the stack, and what the vehicle is not allowed to see.
- [005 — Vehicle 1](spec/005-vehicle-1.md): the first vehicle — one eye, two
  actuators that turn it, and nothing else — and the experiment every version of
  it is put through.
- [006 — Version A](spec/006-vehicle-1-a-pid.md): a plain controller reading
  numbers, as a ground truth to measure the others against.
- [007 — Version B](spec/007-vehicle-1-b-reflex.md): the sensory layer wired
  straight to the effectors, no cortex and no learning.
- [008 — Version C](spec/008-vehicle-1-c-neuromorphic.md): the same reflex, on an
  eye that reports only change.
- [009 — Version D](spec/009-vehicle-1-d-learnt.md): the same again, with the
  wiring left for the vehicle to find for itself.

