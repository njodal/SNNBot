"""Example 1 of spec 014: the one sequence cell that records one step.

Draws `docs/images/episodic_sequence_cell.png` — a sequence cell whose three
inputs are the tile in front of the retina, the move that followed, and the
tile that came next, and which fires on the last of them.

Run it from the root of the repository:

    python3 docs/figures/episodic_sequence_cell.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent / "images" / "episodic_sequence_cell.png"

BLACK, LW, R = "black", 1.8, 1.0

fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=150)
ax.set_xlim(0, 12)
ax.set_ylim(0.4, 5.8)
ax.set_aspect("equal")
ax.axis("off")


def line(x0, x1, y):
    ax.plot([x0, x1], [y, y], color=BLACK, linewidth=LW, zorder=1)


def spike(x, y, h=0.45):
    ax.plot([x, x], [y, y + h], color=BLACK, linewidth=LW, zorder=3)


def dot(x, y):
    ax.add_patch(Circle((x, y), 0.13, facecolor=BLACK, zorder=4))


ax.text(6.0, 5.4, "one step of the world, kept as one cell",
        ha="center", va="center", fontsize=12.5)

cx, cy, x_in = 6.2, 3.3, 2.1
rows = (("tile X", 2.9), ("move right", 3.7), ("tile Y", 4.5))
for k, ((name, sx), y) in enumerate(zip(rows, (cy + 0.75, cy, cy - 0.75))):
    ax.text(x_in - 0.25, y, name, ha="right", va="center", fontsize=11.5)
    line(x_in, cx - R, y)
    spike(sx, y)
    dot(cx - R, y)

ax.add_patch(Circle((cx, cy), R, facecolor="white", edgecolor=BLACK,
                    linewidth=2.2, zorder=2))
ax.text(cx, cy, "sequence", ha="center", va="center", fontsize=10, zorder=5)
ax.text(cx, cy - R - 0.32, "tile X, moved right, tile Y", ha="center",
        va="center", fontsize=9.5, color="0.35")

line(cx + R, 11.2, cy)
spike(9.4, cy)
ax.text(11.2, cy - 0.5, "fires", ha="right", va="center", fontsize=11.5)

ax.add_patch(FancyArrow(2.1, 0.95, 2.6, 0, width=0.012, head_width=0.18,
                        head_length=0.26, length_includes_head=True,
                        color=BLACK))
ax.text(4.95, 0.95, "time", ha="left", va="center", fontsize=11.5)

fig.savefig(OUT, bbox_inches="tight", pad_inches=0.3, facecolor="white")
print("wrote %s" % OUT)
