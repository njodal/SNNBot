# Neuromorphic Memory

## Level 1: Retina
- 3 motion sensors, each fires a pulse when it detects a change at its point.
- 2 additional sensors: one for leftward motion, one for rightward motion.

## Level 2: Spatial recognition (patterns)
- Neurons randomly connected to all sensors.
- Hebbian pruning learning: synapses that coincide in time are strengthened; those that don't coincide disappear.
- Example: one neuron recognizes that sensors 1 and 3 turn on together; another recognizes 2 and 3.
- This is spatial recognition: everything fires at once, in the same place.

## Level 3: Temporal sequence layer
- Connects to the already-stabilized spatial recognition outputs (does not start dense).
- Each neuron learns the order: pattern A precedes pattern B within a time window.
- It also receives the direction sensors (left/right) to record the cause of each transition.
- Each edge of the graph has two labels: temporal order and cause of the movement.
- Note: since it also receives information about whether the retina itself moved, it eliminates all sequences that could be caused by the floor moving rather than the retina.

## Level 4: Recall (output)
- A final neuron that encodes the full chain: sequence of patterns + cause of each transition.
- Episodic memory: not only what happened, but why it happened.
