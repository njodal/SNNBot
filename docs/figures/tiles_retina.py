"""Example 1 of spec 014: a row of numbered tiles and the retina that sees one.

Draws `docs/images/tiles_retina.png` — the tiles, the one the retina is on,
the ten sensors of the retina with the one that is firing, and the two
proprioceptive sensors that say which way it last moved.

Run it from the root of the repository:

    python3 docs/figures/tiles_retina.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent / "images" / "tiles_retina.png"

TILES = [4, 7, 1, 9, 3, 0, 6, 2, 8, 5]
AT = 4                              # the tile under the retina, 0 based
V = 10                              # digits, and sensors in the retina

BLACK, GREY, LW = "black", "0.85", 1.8

fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=150)
ax.set_xlim(0, 13.5)
ax.set_ylim(1.6, 11.8)
ax.set_aspect("equal")
ax.axis("off")


def box(x, y, w, h, fill="white", lw=LW):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=BLACK,
                           linewidth=lw, zorder=2))


def arrow(x, y, dx):
    ax.add_patch(FancyArrow(x, y, dx, 0, width=0.015, head_width=0.2,
                            head_length=0.28, length_includes_head=True,
                            color=BLACK, zorder=3))


# ---- the tiles ------------------------------------------------------------
TY, TH, TW, X0 = 9.0, 0.95, 1.2, 0.5
ax.text(6.75, 11.45,
        "the world: a row of tiles, each holding one number out of ten",
        ha="center", va="center", fontsize=12.5)

for i, v in enumerate(TILES):
    x = X0 + i * TW
    box(x, TY, TW, TH, fill=GREY if i == AT else "white")
    ax.text(x + TW / 2, TY + TH / 2, str(v), ha="center", va="center",
            fontsize=13, zorder=3)
# For the reader. The network never sees a tile number.
for i, name in ((0, "tile 1"), (len(TILES) - 1, "tile %d" % len(TILES))):
    ax.text(X0 + i * TW + TW / 2, TY - 0.3, name, ha="center", va="center",
            fontsize=8, color="0.4")

# the retina, one tile wide
rx = X0 + AT * TW
box(rx - 0.07, TY - 0.12, TW + 0.14, TH + 0.24, fill="none", lw=3.2)
ax.text(rx + TW / 2, TY + TH + 0.32, "retina", ha="center", va="center",
        fontsize=10.5)

# the moves
SY = TY + TH + 1.0
arrow(rx - 0.32, SY, -0.95)
ax.text(rx - 1.42, SY, "move left", ha="right", va="center", fontsize=10)
arrow(rx + TW + 0.39, SY, 0.95)
ax.text(rx + TW + 1.49, SY, "move right", ha="left", va="center", fontsize=10)

# ---- the retina: ten sensors, one per digit ---------------------------------
CTOP, CH, CW, CX = 7.55, 0.5, 1.5, 4.0
shown = TILES[AT]

ax.text(CX - CW / 2 - 0.25, CTOP + 0.3, "sensor", ha="right", va="center",
        fontsize=9, color="0.4")
ax.plot([rx + TW / 2, CX], [TY - 0.05, CTOP + 0.06], color="0.45",
        linewidth=1.0, zorder=1)
for j in range(V):
    box(CX - CW / 2, CTOP - (j + 1) * CH, CW, CH,
        fill=BLACK if j == shown else "white")
    ax.text(CX - CW / 2 - 0.25, CTOP - CH / 2 - j * CH, str(j), ha="right",
            va="center", fontsize=9.5)
ax.text(CX, CTOP - V * CH - 0.38, "retina", ha="center", va="center",
        fontsize=10)
ax.text(CX, CTOP - V * CH - 0.82, "sensor %d fires" % shown, ha="center",
        va="center", fontsize=9.5, color="0.35")

# ---- the proprioceptive sensors: which way it last moved -------------------
PX, PY = 7.4, CTOP - 2.0
for k, (name, fires) in enumerate((("left", False), ("right", True))):
    y = PY - k * (CH + 0.25)
    box(PX, y, CW, CH, fill=BLACK if fires else "white")
    ax.text(PX + CW + 0.25, y + CH / 2, name, ha="left", va="center",
            fontsize=9.5)
ax.text(PX + CW / 2, PY + CH + 0.45, "proprioceptive", ha="center",
        va="center", fontsize=10)
ax.text(PX + CW / 2, PY - CH - 0.25 - 0.45, "it just moved right",
        ha="center", va="center", fontsize=9.5, color="0.35")


fig.savefig(OUT, bbox_inches="tight", pad_inches=0.3, facecolor="white")
print("wrote %s" % OUT)
