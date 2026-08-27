"""Every number the simulator uses, and where it comes from.

SPEC values are written in a spec. PROVISIONAL values answer an open question of
a spec so that the thing can run; each one is a decision about the design still
waiting to be made, not an implementation detail.
"""

# --- time: spec 004 ---
TICK_MS = 10                      # SPEC 004: a spike takes 10 ms to happen
MAX_RATE_HZ = 1000 // TICK_MS     # 100 Hz, the fastest anything can emit

# --- the eye: spec 001 (change based), spec 005 ---
EYE_CELLS = 9                     # SPEC 005: 1x9
CELL_ANGLE_DEG = 9.0              # PROVISIONAL: spec 005 leaves it to be fixed
T_REF_MS = TICK_MS                # SPEC 001, floored by the spike duration

# --- proprioception: spec 001 (threshold based), spec 005 ---
PROP_SENSORS = 10                 # SPEC 005: 1x10 per actuator
PROP_RATE_HZ = 50                 # PROVISIONAL: spec 001 says it fires while in
                                  # range, never how often

# --- the actuators: spec 003 ---
CONTRACTION_MIN = 0               # SPEC 003: the range, fully relaxed ...
CONTRACTION_MAX = 100             # ... to fully contracted
CONTRACTION_REST = 50             # PROVISIONAL: head centred when both are equal
STEP = 1                          # PROVISIONAL, derived below
RELAX_MS = 300                    # PROVISIONAL: spec 003 relax time

# --- the geometry of Vehicle 1: spec 005 ---
DEG_PER_UNIT = 0.4                # PROVISIONAL: head angle per unit of imbalance
                                  # between the two contractions

# One spike moves one actuator by STEP and, since the two are coupled, the other
# by STEP the other way, so the head turns 2 * STEP * DEG_PER_UNIT = 0.8 degrees.
# A babble of 0.5 s at 20 Hz is 10 spikes, so about 8 degrees: near one cell of
# the eye, which spec 004 asks for. The full range is then +-40 degrees, and the
# 10 proprioceptive levels span 80 of them against the 81 the eye covers, so the
# two modalities end up with comparable resolution.

# --- the effector layer: spec 003 ---
# (frequency in Hz, duration in ms). Every period must be a whole number of ticks.
EFFECTORS = ((100, 200), (50, 300), (20, 500), (10, 1000))   # PROVISIONAL

# How far one spike turns the head: it moves its own actuator by STEP and, since
# the two are coupled, the antagonist by STEP the other way.
DEG_PER_SPIKE = 2 * STEP * DEG_PER_UNIT

# --- Version A, the ground truth controller: spec 005 ---
CONTROL_TICK_MS = TICK_MS         # SPEC 005: it acts as often as the spiking one
KP = 2.0                          # PROVISIONAL: 1/s, so the eye closes the gap in
                                  # about half a second. Kp * tick stays far below
                                  # the 1 where it would start to overshoot.
MAX_TURN_RATE = MAX_RATE_HZ * DEG_PER_SPIKE   # SPEC 005: 80 deg/s, what the
                                  # spiking vehicle manages at its fastest

# --- the experiment: spec 005 ---
OBJECT_START_DEG = 18.0           # where the object waits, left of straight ahead
OBJECT_STILL_MS = 1000            # how long it stays there before moving
OBJECT_RATE_DEG_S = 20.0          # PROVISIONAL: how fast it then slides left
OBJECT_MOVING_MS = 1000           # and for how long

# --- babbling: spec 002 ---
BABBLE_EVERY_MS = 2000            # SPEC 002: about one time in two seconds
# Spec 002 also gives half a second as the length of a babble. That is read here
# as the cell's own duration of spec 003 — an uncontrolled cell emits for as long
# as it would have emitted had it been started. Reading it as a fixed 500 ms for
# every cell makes the 100 Hz one sweep the head across its whole range in a
# single babble, which is far past the one cell spec 004 asks for.
