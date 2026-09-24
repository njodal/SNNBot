# Neuromorphic Memory

The goal is to have a memory who store info just from sensory info and later can be recalled just using SNN.

It has three levels:

1. Sensory. This is the sensors defined in the Neuromorphic Sensors spec.
2. Spatial. Receive spike from sensors and stablish the concurrent patterns
3. Temporal. Groups the spatial layer spikes in sequences (what spatial pattern comes after another)

The recall function consist on ingesting an spatial pattern (not necessary to be perceived) and takes the next pattern the memory responds (can be more than one) as the answer.

## Level 1: Neuromorphic sensors
This are the sensors that feed the memory. Usually a combination of external sensors like the retina used in Vehicle1 and proprioceptive ones.
Notes:
- the proprioceptive sensor are needed to stablih the causal relations in the Temporal layer 
A neuromorphic sensor like a retina used in Vehicle1.

## Level 2: Spatial recognition (patterns)
Receive input from Level 1 and establish connections among the sensors that fires together.
- Use concurrent neurons
- Neurons randomly connected to all sensors
- Hebbian pruning learning: synapses that coincide in time are strengthened; those that don't coincide disappear
- Example: one neuron recognizes that sensors 1 and 3 turn on together; another recognizes 2 and 3
- This is spatial recognition: everything fires at once, in the same place

## Level 3: Temporal sequence layer
Receive input from level 2 and establish connections among signal who come one after another.
- Use predecessor neurons
- Connects to the already-stabilized spatial recognition outputs (does not start dense).
- Each neuron learns the order: pattern A precedes pattern B within a time window.
- It also receives the direction sensors (left/right) to record the cause of each transition.
- Each edge of the graph has two labels: temporal order and cause of the movement.
- Note: since it also receives information about whether the retina itself moved, it eliminates all sequences that could be caused by the floor moving rather than the retina.

## Level 4: Recall (output)
To be defined. The idea is to have an alternative path to level 2 (instead of 'seeing' a pattern, 'imaging' one) and pick the next patterns in the sequence.

- A final neuron that encodes the full chain: sequence of patterns + cause of each transition.
- Episodic memory: not only what happened, but why it happened.

# Example
## Level 1: Retina

- 3 motion sensors, each fires a pulse when it detects a change at its point.
- 2 additional sensors: one for leftward motion, one for rightward motion.

