"""The sequence cell of spec 010: one order fires it, another leaves it quiet.

Draws `docs/images/sequence_cell.png`, in the manner of the correlation cell's
figure: the same three spikes arrive in both cases, and only their order
differs.

Run it from the root of the repository:

    python3 docs/figures/sequence_cell.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent / "images" / "sequence_cell.png"

BLACK, LW, R = "black", 1.8, 1.0

fig, ax = plt.subplots(figsize=(9.5, 7.0), dpi=150)
ax.set_xlim(0, 12)
ax.set_ylim(0.4, 9.6)
ax.set_aspect("equal")
ax.axis("off")


def line(x0, x1, y):
    ax.plot([x0, x1], [y, y], color=BLACK, linewidth=LW, zorder=1)


def spike(x, y, h=0.45):
    ax.plot([x, x], [y, y + h], color=BLACK, linewidth=LW, zorder=3)


def dot(x, y):
    ax.add_patch(Circle((x, y), 0.13, facecolor=BLACK, zorder=4))


def case(cy, spikes_at, verdict, out_spike):
    cx, x_in = 6.2, 1.9
    ys = (cy + 0.75, cy, cy - 0.75)
    for k, (y, sx) in enumerate(zip(ys, spikes_at)):
        ax.text(x_in - 0.25, y, "i%d" % (k + 1), ha="right", va="center",
                fontsize=11.5)
        line(x_in, cx - R, y)
        spike(sx, y)
        dot(cx - R, y)
    ax.add_patch(Circle((cx, cy), R, facecolor="white", edgecolor=BLACK,
                        linewidth=2.2, zorder=2))
    ax.text(cx, cy, "sequence", ha="center", va="center", fontsize=10,
            zorder=5)
    line(cx + R, 11.2, cy)
    if out_spike:
        spike(9.4, cy)
    ax.text(11.2, cy - 0.5, verdict, ha="right", va="center", fontsize=11.5)


ax.text(6.0, 9.1, "it is the order that decides, not that all three arrived",
        ha="center", va="center", fontsize=12.5)

case(7.2, (2.8, 3.6, 4.4), "fires", True)
ax.plot([2.8, 4.4], [5.75, 5.75], color=BLACK, linewidth=1.0)
for x in (2.8, 4.4):
    ax.plot([x, x], [5.65, 5.85], color=BLACK, linewidth=1.0)
ax.text(3.6, 5.4, "each within a window of the one before", ha="center",
        va="center", fontsize=10)

case(2.9, (3.6, 2.8, 4.4), "stays quiet", False)

ax.add_patch(FancyArrow(1.9, 0.85, 2.6, 0, width=0.012, head_width=0.18,
                        head_length=0.26, length_includes_head=True,
                        color=BLACK))
ax.text(4.75, 0.85, "time", ha="left", va="center", fontsize=11.5)

fig.savefig(OUT, bbox_inches="tight", pad_inches=0.3, facecolor="white")
print("wrote %s" % OUT)
