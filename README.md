# SNNBot
An experiment on a simple BOT controlled by a Spike Neural Network

# Goal
Have a simple bot (a la Braintenberg Vehicles) using neuromorphic sensors, brain and effectors. In particular the neural network must be an spike type one.

# Definitions
## Neuromorphic sensors
Refers to sensor 'retina style': instead of taking images, it fire events (spikes) any time a change is sensed.

Example: suppose an artificial eye with 3x3 cells, each cell can be empty (white) or busy (black):

![Cell (2,1) occupied](docs/images/grid_3x3.png)

If the eye goes from later status to this new one:

![Cell (2,3) occupied](docs/images/grid_3x3_r2c3.png)

# Vehicle 1
This vehicle has one eye (retina style)
