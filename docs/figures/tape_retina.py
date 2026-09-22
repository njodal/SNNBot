"""The body of spec 013: a tape of numbers and the window that slides along it.

Draws `docs/images/tape_retina.png` — the twenty positions of the tape, the
three slots the retina covers at any moment, and the thirty sensors underneath
with the three that are firing.

The point of the figure is what it cannot show: nothing in it is labelled from
the retina's side. The slots are numbered 1 to 3 because they are places in the
retina, and the positions are numbered 1 to 20 for the reader only — no cell of
the network is ever told which position it is looking at.

Run it from the root of the repository:

    python3 docs/figures/tape_retina.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

OUT = Path(__file__).resolve().parent.parent / "images" / "tape_retina.png"

TAPE = [9, 3, 4, 7, 1, 1, 9, 3, 7, 2, 6, 10, 5, 1, 8, 4, 2, 10, 6, 5]
WIN = (3, 4, 5)                     # the positions under the window, 0 based
V = 10                              # symbols, and sensors per slot

BLACK, GREY, LW = "black", "0.85", 1.8

fig, ax = plt.subplots(figsize=(11.5, 5.5), dpi=150)
ax.set_xlim(0, 21)
ax.set_ylim(1.3, 11.8)
ax.set_aspect("equal")
ax.axis("off")


def box(x, y, w, h, fill="white", lw=LW):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=BLACK,
                           linewidth=lw, zorder=2))


def arrow(x, y, dx):
    ax.add_patch(FancyArrow(x, y, dx, 0, width=0.015, head_width=0.2,
                            head_length=0.28, length_includes_head=True,
                            color=BLACK, zorder=3))


# ---- the tape -------------------------------------------------------------
TY, TH = 9.0, 0.95
ax.text(10.5, 11.45, "the tape: 20 positions, each holding one symbol out of ten",
        ha="center", va="center", fontsize=12.5)

for i, v in enumerate(TAPE):
    x = 0.5 + i
    box(x, TY, 1, TH, fill=GREY if i in WIN else "white")
    ax.text(x + 0.5, TY + TH / 2, str(v), ha="center", va="center", fontsize=13,
            zorder=3)
# For the reader. The network never sees a position number.
for i, name in ((0, "position 1"), (19, "position 20")):
    ax.text(1.0 + i, TY - 0.3, name, ha="center", va="center", fontsize=8,
            color="0.4")

# the window
wx = 0.5 + WIN[0]
box(wx - 0.07, TY - 0.12, 3.14, TH + 0.24, fill="none", lw=3.2)
ax.text(wx - 0.32, TY + TH + 0.32, "slots", ha="right", va="center",
        fontsize=10, color="0.4")
for k, i in enumerate(WIN):
    ax.text(1.0 + i, TY + TH + 0.32, str(k + 1), ha="center", va="center",
            fontsize=10.5)

# the step
SY = TY + TH + 1.0
arrow(wx - 0.32, SY, -0.95)
ax.text(wx - 1.42, SY, "one step back", ha="right", va="center", fontsize=10)
arrow(wx + 3.39, SY, 0.95)
ax.text(wx + 4.49, SY, "one step forward", ha="left", va="center", fontsize=10)

# ---- the retina: one column of ten sensors per slot ------------------------
CTOP, CH, CW = 7.55, 0.5, 1.5
CENTRES = (4.0, 7.0, 10.0)

ax.text(3.05, CTOP + 0.3, "sensor", ha="right", va="center", fontsize=9,
        color="0.4")
for j in range(V):
    ax.text(3.05, CTOP - CH / 2 - j * CH, str(j + 1), ha="right", va="center",
            fontsize=9.5)

for k, cx in enumerate(CENTRES):
    shown = TAPE[WIN[k]]
    ax.plot([1.0 + WIN[k], cx], [TY - 0.05, CTOP + 0.06], color="0.45",
            linewidth=1.0, zorder=1)
    for j in range(V):
        box(cx - CW / 2, CTOP - (j + 1) * CH, CW, CH,
            fill=BLACK if j + 1 == shown else "white")
    ax.text(cx, CTOP - V * CH - 0.38, "slot %d" % (k + 1), ha="center",
            va="center", fontsize=10)
    ax.text(cx, CTOP - V * CH - 0.82, "sensor %d fires" % shown, ha="center",
            va="center", fontsize=9.5, color="0.35")

# ---- what it means --------------------------------------------------------
NOTE = (
    "Thirty change based sensors of spec 001, ten per slot.\n"
    "Three of them fire at any moment, one per slot.\n"
    "\n"
    "A column is a place code of a symbol: which of the\n"
    "ten fires is the number that is there. Nothing on\n"
    "any wire is a value — the same arrangement the\n"
    "propioceptive array of spec 001 uses for a contraction.\n"
    "\n"
    "A slot is a place in the retina and not a place in the\n"
    "world: the reading says what is in front of it, never\n"
    "where it is. One step forward and slots 1 and 2 come\n"
    "to show what slots 2 and 3 showed — that overlap, and\n"
    "the spike that said it stepped, are all there is to go on."
)
ax.text(12.1, 5.0, NOTE, ha="left", va="center", fontsize=10.5, linespacing=1.55)

fig.savefig(OUT, bbox_inches="tight", pad_inches=0.3, facecolor="white")
print("wrote %s" % OUT)
