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
  actuators that turn it, and nothing else — with the four ways it has been
  driven, from a plain controller to a wiring it finds for itself.
- [006 — Vehicle 2](spec/006-vehicle-2.md): the same eye carried on a neck — a
  quick joint of short travel and a slow one of long travel, both pointing it.
- [010 — Cells](spec/010-cells.md): what the layers are made of — what a cell
  reads, what it emits, and the three kinds built so far.
- [011 — A P controller out of cells](spec/011-p-controller.md): the ground
  truth's `o = k × (p − r)` built from the cells there are — the subtraction a
  table of coincidence cells, the gain a ladder of effectors.

