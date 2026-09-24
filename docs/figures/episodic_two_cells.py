"""Example 1 of spec 014: the two correlation cells that record one step.

Draws `docs/images/episodic_two_cells.png` — the first cell pairs the tile
that was in front of the retina with the move that followed, and the second
pairs that cell's spike with the tile that came next.

Run it from the root of the repository:

    python3 docs/figures/episodic_two_cells.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent / "images" / "episodic_two_cells.png"

BLACK, LW, R = "black", 1.8, 0.72

fig, ax = plt.subplots(figsize=(11.5, 5.6), dpi=150)
ax.set_xlim(0, 14)
ax.set_ylim(0.6, 7.4)
ax.set_aspect("equal")
ax.axis("off")


def line(x0, x1, y):
    ax.plot([x0, x1], [y, y], color=BLACK, linewidth=LW, zorder=1,
            solid_capstyle="butt")


def spike(x, y, h=0.5):
    ax.plot([x, x], [y, y + h], color=BLACK, linewidth=LW, zorder=3)


def dot(x, y):
    ax.add_patch(Circle((x, y), 0.13, facecolor=BLACK, edgecolor=BLACK,
                        zorder=4))


def cell(cx, cy, name):
    ax.add_patch(Circle((cx, cy), R, facecolor="white", edgecolor=BLACK,
                        linewidth=2.2, zorder=2))
    ax.text(cx, cy, name, ha="center", va="center", fontsize=10, zorder=5)


def label(x, y, s, **kw):
    ax.text(x, y, s, ha="right", va="center", fontsize=11.5, **kw)


ax.text(7.0, 7.05, "one step of the world, kept as one chain of two cells",
        ha="center", va="center", fontsize=12.5)

# ---- cell 1: tile X, then move right --------------------------------------
C1 = (4.6, 5.3)
DY = 0.42
X_IN = 1.6

label(X_IN - 0.25, C1[1] + DY, "tile X")
line(X_IN, C1[0] - R, C1[1] + DY)
spike(2.3, C1[1] + DY)
dot(C1[0] - R, C1[1] + DY)

label(X_IN - 0.25, C1[1] - DY, "move right")
line(X_IN, C1[0] - R, C1[1] - DY)
spike(3.3, C1[1] - DY)
dot(C1[0] - R, C1[1] - DY)

cell(*C1, "correlation")
ax.text(C1[0], C1[1] - R - 0.32, "tile X, then moved right", ha="center",
        va="center", fontsize=9.5, color="0.35")

# its output: right, then down into cell 2
C2 = (9.4, 3.1)
ELBOW = 7.1
line(C1[0] + R, ELBOW, C1[1])
spike(6.2, C1[1])
ax.plot([ELBOW, ELBOW], [C1[1], C2[1] + DY], color=BLACK, linewidth=LW,
        zorder=1)
line(ELBOW, C2[0] - R, C2[1] + DY)
dot(C2[0] - R, C2[1] + DY)

# ---- cell 2: that, then tile Y --------------------------------------------
label(X_IN - 0.25, C2[1] - DY, "tile Y")
line(X_IN, C2[0] - R, C2[1] - DY)
spike(7.9, C2[1] - DY)
dot(C2[0] - R, C2[1] - DY)

cell(*C2, "correlation")
ax.text(C2[0], C2[1] - R - 0.32, "tile X, moved right, tile Y", ha="center",
        va="center", fontsize=9.5, color="0.35")

line(C2[0] + R, 13.4, C2[1])
spike(11.6, C2[1])
ax.text(13.4, C2[1] - 0.45, "fires", ha="right", va="center", fontsize=11.5)

# ---- time -----------------------------------------------------------------
ax.add_patch(FancyArrow(1.6, 1.15, 3.0, 0, width=0.012, head_width=0.18,
                        head_length=0.26, length_includes_head=True,
                        color=BLACK))
ax.text(4.85, 1.15, "time", ha="left", va="center", fontsize=11.5)


fig.savefig(OUT, bbox_inches="tight", pad_inches=0.3, facecolor="white")
print("wrote %s" % OUT)
