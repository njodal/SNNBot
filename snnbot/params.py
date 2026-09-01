"""Every number the simulator uses, and where it comes from.

SPEC values are written in a spec. PROVISIONAL values answer an open question of
a spec so that the thing can run; each one is a decision about the design still
waiting to be made, not an implementation detail.
"""

# --- time: spec 004 ---
TICK_MS = 1                       # SPEC 004: about what a spike takes, as in a
                                  # real one — a millisecond or two
REFRACTORY_MS = 2                 # SPEC 004: how long a cell is deaf to itself
                                  # after firing. This, and not the width of the
                                  # spike, is what caps a rate in biology and
                                  # what caps it here
MAX_RATE_HZ = 1000 // REFRACTORY_MS   # 500 Hz, the fastest anything can emit

# --- the eye: spec 001 (change based), spec 005 ---
EYE_CELLS = 9                     # SPEC 005: 1x9
CELL_ANGLE_DEG = 9.0              # PROVISIONAL: spec 005 leaves it to be fixed
T_REF_MS = REFRACTORY_MS          # SPEC 001, floored by the refractory period
SETTLE_MS = 5                     # PROVISIONAL: how long a thing has to stay
                                  # in a cell of the eye before the cell will
                                  # say so. Not a lie about when it was seen:
                                  # a sensor that needs a moment to be sure.
ORDER_DELAY_MS = 20               # SPEC 010: the eye reports a cell going empty
                                  # and the next going busy at the very same
                                  # instant, so something has to hold one back
                                  # for a correlation cell to have an order to
                                  # read. A delay cell on the arrival does it,
                                  # and it lands well inside their window rather
                                  # than on an edge of it.

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
STEERING = ((100, 200), (50, 300), (20, 500), (10, 1000))    # PROVISIONAL
# One more, gentler than any of the four, for going along with an object that
# has just reached the middle of the eye. The slowest of the ladder moves the
# head eight degrees in its run, near enough a whole cell, so using it to nudge
# overshoots every time. This one moves four, at four degrees a second — about
# the speed of the thing it is meant to keep up with.
ACCOMPANY = ((5, 1000),)                                     # PROVISIONAL
EFFECTORS = STEERING + ACCOMPANY

# How far one spike turns the head: it moves its own actuator by STEP and, since
# the two are coupled, the antagonist by STEP the other way.
DEG_PER_SPIKE = 2 * STEP * DEG_PER_UNIT

# --- Version A, the ground truth controller: spec 005 ---
CONTROL_TICK_MS = TICK_MS         # SPEC 005: it acts as often as the spiking one
KP = 2.0                          # SPEC 005: 1/s, so the eye closes the gap in
                                  # about half a second. Kp * tick stays far below
                                  # the 1 where it would start to overshoot.
MAX_TURN_RATE = STEERING[0][0] * DEG_PER_SPIKE   # SPEC 005: 80 deg/s, what the
                                  # spiking vehicle manages at its fastest. Its
                                  # fastest effector, that is, not the ceiling the
                                  # refractory allows — nothing here emits at 500 Hz

# --- Version C, the correlation cells: spec 005 ---
# SPEC 010: how long after its predecessor a successor still counts as the same
# move. Below the minimum the two are simultaneous rather than ordered, above the
# maximum they have nothing to do with each other. The eye's lag of 20 ms sits
# midway, with room on both sides — which is the whole reason the tick is a
# millisecond: at ten, the window and its own resolution were the same number and
# there was nowhere inside it to be.
CORRELATION_MIN_MS = 10           # PROVISIONAL
CORRELATION_MAX_MS = 50           # PROVISIONAL

# --- Version D, learning the wiring: spec 005 ---
LEARNING_RATE = 0.3               # PROVISIONAL: how much one reinforcing spike
                                  # moves a weight
ELIGIBILITY_MS = 800              # PROVISIONAL: how long a connection stays
                                  # eligible for the credit of what follows it
EXPLORE = 0.15                    # PROVISIONAL: how often it tries something
                                  # other than the best it knows
WEIGHT_MAX = 1.0                  # PROVISIONAL: the strongest a connection gets.
                                  # Without a ceiling an early run of luck piles
                                  # up more weight than later evidence can undo.

# --- the experiment: spec 005 ---
OBJECT_START_DEG = 18.0           # where the object waits, left of straight ahead
OBJECT_STILL_MS = 3000            # how long it stays there before moving
OBJECT_RATE_DEG_S = 5.0            # PROVISIONAL: how fast it then slides
OBJECT_LEFT_MS = 3000             # how long it goes left
OBJECT_RIGHT_MS = 6000            # and then how long back to the right

# --- babbling: spec 002 ---
BABBLE_EVERY_MS = 2000            # SPEC 002: about one time in two seconds
# Spec 002 also gives half a second as the length of a babble. That is read here
# as the cell's own duration of spec 003 — an uncontrolled cell emits for as long
# as it would have emitted had it been started. Reading it as a fixed 500 ms for
# every cell makes the 100 Hz one sweep the head across its whole range in a
# single babble, which is far past the one cell spec 004 asks for.
