# Neuromorphic Memory

## Level 1: Retina
- 3 motion sensors, each fires a pulse when detecting change at its point.
- 2 additional sensors: one for leftward motion, one for rightward.

## Level 2: AND Layer (patterns)
- Neurons randomly connected to all sensors.
- Hebbian pruning learning: synapses that coincide in time strengthen; those that don't disappear.
- Example: one neuron recognizes that sensors 1 and 3 turn on together; another recognizes 2 and 3.

## Level 3: Temporal sequence layer
- Connects to the already stabilized AND outputs (doesn't start dense).
- Each neuron learns the order: pattern A precedes pattern B within a time window.
- Also receives direction sensors (left/right) to record the cause of each transition.
- Each edge of the graph has two labels: temporal order and cause of movement.

## Level 4: Recall (output)
- A final neuron that encodes the complete chain: sequence of patterns + cause of each transition.
- Episodic memory: not just what happened, but why it happened.
