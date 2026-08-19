# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
Refers to sensor 'retina style': instead of taking images, it fire events (spikes) any time a change is sensed.

See [spec 001](spec/001-neuromorphic-sensors.md) for the full definition, the worked example and the event format.

# Vehicle 1
This vehicle has one eye (retina style)

# Specs
Design specifications live in [`spec/`](spec/).

- [001 — Neuromorphic sensors](spec/001-neuromorphic-sensors.md): what counts as a
  neuromorphic sensor in this project, the event format all sensors emit, and the
  3x3 retina of Vehicle 1.
