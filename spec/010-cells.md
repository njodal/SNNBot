# 010 — Cells

- **Status:** draft
- **Date:** 2026-08-28
- **Supersedes / Superseded by:** —

The three layers of [spec 002](002-vehicles.md) are made of cells. This is what a cell is, what any of them have in common, and what the ones built so far actually do.

## What a cell is
A cell can have any number of inputs and exactly one output, and each input is connected either excitatorily or inhibitorily.

![A cell, its two kinds of input and its one output](../docs/images/cell.png)

An excitatory connection is drawn as a filled circle against the cell and an inhibitory one as a bar.

What travels on any of those lines is a spike, and only a spike, a signal that has happened rather than a value that can be read. 

Nothing emits faster than one spike per 10 ms, the time a spike takes in [spec 004](004-simulator.md). A cell is bound by that like everything else, so 100 Hz is the most any of them can do.

The input connections have a 'weight' value, to indicate if the connection is mature or not. If the connection is not mature the spike will not go to the cell. Weight values is in the (0, 1) interval with values above 0.7 are considered mature.

## Type of Cells
### Effector Cell
It is a cell commonly used to control actuators, as [spec 003](003-neuromorphic-actuators.md) describes.

It main function is to emit a train of spikes at a fixed frequency and time. If the cell has mature input connections it will start the emit process when an excitatory spike arrives, and finish when an inhibitory one arrives or the process run out of its time. If the cell has not mature connections it can start the emit process spontanouely at random. 

![An effector cell, started and stopped](../docs/images/effector_cell.png)


### Correlation Cell
This cell has two input connections and fires if the second connection arrives *after* the first one.

![A correlation cell, one order and the other](../docs/images/correlation_cell.png)

Both inputs arrive in either case. What settles it is the order, which is what makes a pair of these — one wired each way round — able to tell a movement from the same movement backwards.

The time window has a minimum and maximum value, so to discard spikes arriving at almost the same time or too far away. Ex: (10, 50) (in ms).

### Coincidence Cell
This cell have many inputs connections and fires if the mayority of the inputs arrives at the same time.

![A coincidence cell, together and spread out](../docs/images/coincidence_cell.png)

The same spikes arrive in both cases and the same number of them. Only their falling together makes any difference.

## The cells there are so far
Three kinds, with less in common than one might expect.

| | inputs | what it does |
|---|--------|--------------|
| **Effector** ([spec 003](003-neuromorphic-actuators.md)) | start, stop | emits at its own frequency for its own duration, and drives an actuator. Unwired, it fires by itself — the babbling of spec 002 |
| **Relay** ([Version B](005-vehicle-1.md)) | one | fires when its input fires. The plainest cell there could be |
| **Correlation** ([Version C](005-vehicle-1.md)) | predecessor, successor | fires only if the predecessor arrived first, and within a window. The pair `(i→j)` and the pair `(j→i)` are different cells, which is what makes it tell one direction from the other |

## What they have not got
No membrane, no threshold, nothing accumulating. Not one of the cells built so far integrates anything: each is a small rule over the spikes at its inputs, and it either fires or does not.

That is a deliberate simplification and it may well not last. It holds while a cell has one or two inputs and reacts to a pattern between them. The moment a cell has to weigh many inputs against one another — which is what a cortex is for — something like a membrane filling up to a threshold is the usual answer, and none of this has one.

## Connections
A connection carries a spike from one cell's output to another's input.

Through Versions A to C a connection is simply there or not there. In [Version D](005-vehicle-1.md) it is a **weight**, and what a cell does is settled by which of its connections is the strongest. That change is what lets *not connected* soften into *connected weakly*, so that babbling fades as a vehicle learns rather than stopping the moment somebody wires it.

Inhibition sits awkwardly. The effector layer is supposed to inhibit its own cells laterally, so that only the last one woken stays active, but whether that is wiring between the cells or a property of the layer above them is not decided. The simulator does it above them, which is a choice made for convenience and not from the design.

## Open questions

- Is there one cell here, or three unrelated rules that happen to speak in spikes? A common model would make a new kind cheap to add, and would say what a cell of this project can and cannot compute.
- Does a cell need a membrane and a threshold? Nothing so far has wanted one, but nothing so far weighs more than two inputs.
- Do cells have a refractory period, as the sensors of spec 001 do? Nothing stops one firing on consecutive cycles today.
- Lateral inhibition: wiring between cells, or something the layer does to them?
