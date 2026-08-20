# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
The term *neuromorphic* sensors in this contexts refers to sensors that senses some value from the environment and fires *spikes* (events) to be send to upper level of the Spike Neural Network.

See [spec 001](spec/001-neuromorphic-sensors.md).

# Vehicles
Following the Braintenberg tradition, we will define a series of Vehicles, from the simplest one to more sophisticated.

See [spec 002](spec/002-vehicles.md) for what each vehicle is made of.

# Specs
Design specifications live in [`spec/`](spec/).

- [001 — Neuromorphic sensors](spec/001-neuromorphic-sensors.md): what counts as a
  neuromorphic sensor in this project, and the event format all sensors emit.
- [002 — Vehicles](spec/002-vehicles.md): the series of vehicles, what sensors and
  actuators each one carries, and how it is put together.

