# 001 — Neuromorphic sensors

- **Status:** draft
- **Date:** 2026-08-19
- **Supersedes / Superseded by:** —

## Context

The project goal states that the bot must use *neuromorphic* sensors, brain and
effectors. "Neuromorphic" is used loosely in the literature, so this spec fixes
what it means **for SNNBot**: it is the contract every sensor in this repo must
satisfy, and the contract the spiking network can rely on at its input.

Vehicle 1 has one eye, retina style. That retina is the first sensor built to
this spec.

## Goal

Define what counts as a neuromorphic sensor in SNNBot, the event format its
output must use, and the parameters that describe any such sensor — so that
sensors, the network and the simulator can be developed against one interface.

## Scope

**In scope**

- The defining properties a sensor must have to be called neuromorphic here.
- The event (spike) representation shared by all sensors.
- The specific instantiation for Vehicle 1's retina.

**Out of scope**

- The neuron model and network topology of the brain (separate spec).
- Effectors (separate spec).
- Physical hardware. Everything here is defined so it can be simulated first and
  implemented in hardware later without changing the interface.

## Definition

A sensor is **neuromorphic** in SNNBot if it has all of the following properties.

1. **Event-driven.** The sensor produces output only when the quantity it
   measures changes. Silence is a valid and meaningful output: nothing changing
   means nothing transmitted.
2. **Asynchronous.** There is no frame rate, no global clock and no sampling
   loop. Each sensing element emits on its own, at the moment its condition is
   met.
3. **Spike output.** The only thing that leaves the sensor is a spike: an
   identical, dimensionless, instantaneous event. All information is carried by
   *which* element fired and *when* — never by an amplitude attached to the
   event.
4. **Local and independent elements.** Each sensing element decides on its own
   state alone. No element needs a value from another element, and no stage
   collects all elements before output can be produced.
5. **Change / contrast coded, not level coded.** The element responds to the
   temporal change of its input, relative to its own recent state, not to the
   absolute value. A constant stimulus, however strong, eventually goes silent.
6. **Sparse.** Under a static scene the output rate tends to zero; bandwidth is
   spent in proportion to how much is happening.

A device that samples all its elements on a fixed clock and emits a full array
of values is **not** a neuromorphic sensor under this spec, even if the values
are later converted to spike trains downstream. The conversion has to happen at
the element, before transmission.

## Event format

Every sensor emits a stream of events:

```
event := (t, address, p)
```

| Field     | Type            | Meaning                                              |
|-----------|-----------------|------------------------------------------------------|
| `t`       | time            | When the event occurred, in simulator time units      |
| `address` | sensor-specific | Which element fired (for the retina: row, column)     |
| `p`       | `ON` \| `OFF`   | Sign of the change that caused it                     |

`ON` means the measured quantity increased past threshold, `OFF` means it
decreased past threshold. There is no magnitude field: an event is an event.
This is the usual address-event representation (AER), and the reason for it is
property 3 above — it is what makes the sensor output directly injectable into
the spiking network without any decoding stage.

## Element model

Each element keeps a reference value `L_ref` of its input signal `L(t)`, and
fires when the signal has moved far enough from that reference:

- `L(t) = log(I(t))` — the log of the raw measurement, so that the threshold
  means *relative* change and the element works across a wide range of input
  intensities.
- If `L(t) − L_ref > θ` → emit `ON`, then set `L_ref = L(t)`.
- If `L_ref − L(t) > θ` → emit `OFF`, then set `L_ref = L(t)`.
- After emitting, the element is blind for a refractory period `t_ref`.

## Parameters

Any sensor built to this spec is described by:

| Parameter | Symbol  | Meaning                                                |
|-----------|---------|--------------------------------------------------------|
| Contrast threshold | `θ` | Relative change needed to emit an event            |
| Refractory period  | `t_ref` | Minimum time between two events from one element |
| Array shape        | —   | Number and arrangement of elements                     |
| Latency            | —   | Delay between the physical change and the event        |

## Vehicle 1 retina

The first sensor built to this spec.

- **Array shape:** 3 × 3, nine elements. Addresses are `(row, col)` with
  `row, col ∈ {1, 2, 3}`, row 1 at the top, column 1 at the left.
- **Channels:** each element has an `ON` and an `OFF` channel, so the retina
  presents 18 spike outputs to the brain.
- **Input:** scene luminance falling on the element. A dark object over an
  element lowers `L`, so its arrival produces `OFF` and its departure `ON`.

The two example stimuli in `docs/images/` show a dark cell in the middle row:
[`grid_3x3.png`](../docs/images/grid_3x3.png) at `(2,1)` and
[`grid_3x3_r2c3.png`](../docs/images/grid_3x3_r2c3.png) at `(2,3)`. A dark
object crossing the retina from left to right is *not* transmitted as those two
pictures. It is transmitted as the events at the boundaries between them —
`OFF` at the cell being entered, `ON` at the cell being left, in that time
order, and nothing at all from the six cells that never change. That difference
is the whole point of this spec.

## Acceptance criteria

- [ ] A sensor implementation emits nothing at all while its input is constant.
- [ ] Output is a time-ordered stream of `(t, address, p)` events and nothing else.
- [ ] No element reads another element's state; no stage waits for all elements.
- [ ] Doubling the input intensity everywhere, with the same relative changes,
      produces the same event stream.
- [ ] Two events from the same element are never closer together than `t_ref`.
- [ ] The retina reports the 3 × 3 addressing above, with ON and OFF channels.

## Open questions

- Values for `θ` and `t_ref` — to be fixed once the simulator's time base exists.
- Does the brain need ON and OFF as separate input channels, or is one polarity
  enough for Vehicle 1's behaviour?
- The simulator will likely render stimuli as frames internally. What frame rate
  is fine before the discretisation shows up as artefacts in the event stream?
- Which sensors beyond vision does the bot need (proximity, contact/whiskers,
  motor feedback)? Each would be a separate spec built on this definition.
