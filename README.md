# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
There are two types of sensors:
- change based: fires when some change in the environment. Ex: retina style eye.
- threshold based: fires when same value is above same value. Ex: sensor to measure the level of contraction of a muslcle.


Refers to sensor 'retina style': instead of taking images, it fire events (spikes) any time a change is sensed.

See [spec 001](spec/001-neuromorphic-sensors.md) for the full definition, the worked example and the event format.

## Neuromorphic actuators
Refers to actuator 'muscle style': it is fixed to two both sides of and articulation and can only contract.

# Vehicles
Following the Braintenberg tradition, we will define a series of Vehicles, from the simplest one to more sophisticated.

## Vehicle 1
This vehicle has:
- sensors
  - one very simple eye: just an array of 9 cells (1x9)
  - 20 proprioceptive sensors:
    - 10 for the right actuator and 10 for the left one, each set of 10 sense the level of contraction of the actuator (only one sensor is active)
- actuators
  - one attached to the right of eye and the other to the left
 
So the vehicle can't move, it just can move the eye to both sides. 

# Specs
Design specifications live in [`spec/`](spec/).

- [001 — Neuromorphic sensors](spec/001-neuromorphic-sensors.md): what counts as a
  neuromorphic sensor in this project, and the event format all sensors emit.

