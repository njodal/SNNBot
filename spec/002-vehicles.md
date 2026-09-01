# 002 — Vehicles

- **Status:** draft
- **Date:** 2026-08-20
- **Supersedes / Superseded by:** —

Following the Braitenberg tradition, we will define a series of Vehicles, from the simplest one to more sophisticated.

## General Architecture
All vehicles have a similar setup for sensors, brain, and actuators.

![The architecture of a vehicle](../docs/images/vehicle_architecture.png)

At the bottom is the *body*: the sensors that face the environment, the propioceptive sensors that face the body itself, and the actuators. On top of it sits the *cortex*, and between them two layers that do the translating — the sensory layer, which takes the spikes the sensors fire, and the effector layer, whose effectors drive the actuators.

Nothing crosses those levels other than spikes, so what changes from one vehicle to the next is what hangs off the bottom level and how the cortex is wired, not the shape of the stack.

The cortex stayed empty for a long while: every vehicle up to [Version D](005-vehicle-1.md) is a reflex, the sensory layer reaching the effector layer directly. Version E is the first to want one, and what it puts there judges rather than acts — which is why it belongs above a body it cannot touch.

The Sensory Layer, Cortex and Effector Layer are composed of [cells](010-cells.md).

### Sensory Layer
It takes spikes from sensors and does some processing to generate perception to be sent to the Cortex. Ex: find some correlations in the spikes between environment sensors and propioceptive ones (in other words, find what effect the movements detected by the propioceptive sensors have on the environment ones).

This layer can have some learning or not, depending on each vehicle.

### Effector Layer
This layer is composed of Effector cells that are attached to the actuators.

If an Effector cell doesn't have yet a start and stop input signal, it is said the cell is uncontrolled and it will fire spontaneously for a brief period of time. This is the cause of 'motor babbling' and is useful to learn correlations in the Sensory Layer.

Uncontrolled means *not wired yet*: nothing is connected to the cell's start and stop inputs. Once the cell is wired, its spontaneous firing is gone for good. So babbling belongs to the stage before the cortex has taken hold of an effector, and is not something an idle effector does while waiting for a command.

The firing of an uncontrolled cell is random: nothing schedules it, the cell simply goes off at unpredictable moments (ex: one time in two seconds) and emits for a brief period each time (ex: 0.5 seconds). That randomness is what makes babbling worth having — the movements it produces bear no relation to each other, so whatever the Sensory Layer does find correlated is the tie between a movement and what it causes the sensors to see.

## The vehicles

- [005 — Vehicle 1](005-vehicle-1.md): one eye and two actuators that turn it, and nothing else.
