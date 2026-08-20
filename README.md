# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
The term *neuromorphic* sensors in this contexts refers to sensors that senses some value from the environment and fires *spikes* (events) to be send to upper level of the Spike Neural Network.

See [spec 001](spec/001-neuromorphic-sensors.md) for the full definition, the worked example and the event format.

# Vehicles
Following the Braintenberg tradition, we will define a series of Vehicles, from the simplest one to more sophisticated.

## Vehicle 1
This vehicle has:
- sensors
  - one very simple eye: just an array of 9 cells (1x9)
  - two propioceptive sensors (1x10 sensors each) to sense the level of contraction of each actuator
- actuators
  - one attached to the right of eye and the other to the left
 
So the vehicle can't move, it just can move the eye to both sides. 

# Specs
Design specifications live in [`spec/`](spec/).

- [001 — Neuromorphic sensors](spec/001-neuromorphic-sensors.md): what counts as a
  neuromorphic sensor in this project, and the event format all sensors emit.

