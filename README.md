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
- [002 — Vehicles](spec/002-vehicles.md): the series of vehicles, what sensors and
  actuators each one carries, and how it is put together.
- [003 — Neuromorphic actuators](spec/003-neuromorphic-actuators.md): what drives an
  actuator, and how the effectors set the speed it moves at.

