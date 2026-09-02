"""Render a run of Vehicle 2 to an animated GIF: two joints, and what they sense.

The object stays where it is. What moves is the pair of joints, and the picture
is there to show what neither angle alone would: that the gaze holds still while
the two of them change places.
"""

import math
import random
from collections import deque

from PIL import Image, ImageDraw

from .animate import F, FS, FT, _zigzag
from ..body.vehicle2 import HEAD, LEFT, NECK, RIGHT, Vehicle2
from ..clock import Clock
from ..control import GazeController, RecentringController
from ..layers.sensory import PostureReflex
from ..events import ON
from ..params import (CELL_ANGLE_DEG, EYE_CELLS, OBJECT_RATE_DEG_S, PROP_SENSORS,
                      TICK_MS)
from ..world import World, experiment_path

W, H = 760, 760
CELL = 30
BASE = (430, 500)                   # the joint on the ground, the one fixed thing
NECK_LEN = 170
HEAD_JOINT = (BASE[0], BASE[1] - NECK_LEN)
EYE_L = BASE[0] - EYE_CELLS * CELL // 2   # centred on the joint it turns about,
                                          # so the middle cell is the one over it
EYE_T, EYE_B = HEAD_JOINT[1] - CELL, HEAD_JOINT[1]
HEAD_ANCHOR = (BASE[0], HEAD_JOINT[1] + 0.3 * NECK_LEN)   # where the head actuators pull
BAR_Y, BAR_HALF = BASE[1] - 0.45 * NECK_LEN, 55     # the neck's cross bar
GROUND_HALF, HATCH = 95, 48
# Where to draw a thing the vehicle takes to be infinitely far away. Measured
# from the base, which is the one point of the vehicle that does not move, and
# as far out as the frame allows: the closer it is drawn, the more the sight
# line swings as the neck carries the eye away from the base — a parallax the
# model does not have and the picture should not invent.
OBJECT_R = 440

ROWS = ((535, 567, "eye", EYE_CELLS), (577, 601, "head sense", PROP_SENSORS),
        (611, 635, "neck sense", PROP_SENSORS))
# Version B watches different things: the neck's own array is read by nobody,
# and what matters instead is the layer that reads the head's, and what it does.
ROWS_B = ((512, 540, "eye", EYE_CELLS), (550, 578, "head sense", PROP_SENSORS),
          (588, 612, "neck cells", PROP_SENSORS), (622, 634, "neck effectors", 2),
          (644, 656, "eye effectors", 2))
RASTER_L, RASTER_R = 170, W - 20
PLOT_R = W - 80          # the traces stop short of the edge, to be named there
WINDOW_MS = 3000
PLOT_T, PLOT_B = 672, 736


def standing_then_right(start_deg, still_ms, rate=OBJECT_RATE_DEG_S):
    """It stands where it is until the neck has taken over, and then goes right.

    Which asks the vehicle the other half of the question: not how it settles
    once it has caught something, but which joint does the following.
    """
    def where(t):
        return start_deg - rate * max(t - still_ms, 0) / 1000
    return where


def _rot(p, c, deg):
    """Turn a point about a centre. Positive is to the left, anticlockwise here."""
    a = math.radians(-deg)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(a) - dy * math.sin(a),
            c[1] + dx * math.sin(a) + dy * math.cos(a))


def _dashed(d, p0, p1, every=8):
    (x0, y0), (x1, y1) = p0, p1
    n = max(int(math.hypot(x1 - x0, y1 - y0) / every), 1)
    for k in range(0, n, 2):
        d.line([(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n),
                (x0 + (x1 - x0) * (k + 1) / n, y0 + (y1 - y0) * (k + 1) / n)],
               fill="black", width=1)


def frame(t, head_deg, neck_deg, busy, object_deg, raster, trace, scale,
          title="Version A: a PID on each joint", note=None, rows=ROWS):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    neck = lambda p: _rot(p, BASE, neck_deg)                        # noqa: E731
    hj = neck(HEAD_JOINT)
    head = lambda p: _rot(neck(p), hj, head_deg)                    # noqa: E731

    # the object, fixed out there. Drawn from where the head joint rests, the
    # eye taking it to be far enough away that no part of the vehicle sees it in
    # a direction of its own.
    ang = math.radians(object_deg)
    ox = BASE[0] - OBJECT_R * math.sin(ang)
    oy = BASE[1] - OBJECT_R * math.cos(ang)
    d.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], fill="black")
    d.text((ox + 17, oy), "object", fill="black", font=FS, anchor="lm")

    # the base does not move
    d.line([(BASE[0] - GROUND_HALF, BASE[1]), (BASE[0] + GROUND_HALF, BASE[1])],
           fill="black", width=5)
    for x in range(BASE[0] - GROUND_HALF, BASE[0] + GROUND_HALF + 1, 16):
        d.line([(x, BASE[1] + 3), (x - 13, BASE[1] + 20)], fill="black", width=2)

    # the neck: cross bar, stem, and the two actuators down to the base
    d.line([neck((BASE[0] - BAR_HALF, BAR_Y)), neck((BASE[0] + BAR_HALF, BAR_Y))],
           fill="black", width=3)
    d.line([BASE, hj], fill="black", width=3)
    for sign in (-1, 1):
        _zigzag(d, neck((BASE[0] + sign * BAR_HALF, BAR_Y)),
                (BASE[0] + sign * HATCH, BASE[1]), n=9, base=120)

    # the head: the two actuators from the eye down onto the neck
    for x in (EYE_L + CELL * 2.25, EYE_L + CELL * 6.75):
        _zigzag(d, head((x, EYE_B)), neck(HEAD_ANCHOR), n=9, base=130)

    # the eye
    if busy:
        x0, x1 = EYE_L + (busy - 1) * CELL, EYE_L + busy * CELL
        d.polygon([head((x0, EYE_T)), head((x1, EYE_T)),
                   head((x1, EYE_B)), head((x0, EYE_B))], fill="black")
        _dashed(d, (ox, oy), head(((x0 + x1) / 2, (EYE_T + EYE_B) / 2)))
    for c in range(1, EYE_CELLS):
        x = EYE_L + c * CELL
        d.line([head((x, EYE_T)), head((x, EYE_B))], fill="black", width=2)
    corners = [(EYE_L, EYE_T), (EYE_L + EYE_CELLS * CELL, EYE_T),
               (EYE_L + EYE_CELLS * CELL, EYE_B), (EYE_L, EYE_B), (EYE_L, EYE_T)]
    d.line([head(p) for p in corners], fill="black", width=2, joint="curve")
    for p in (hj, BASE):
        d.ellipse([p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10],
                  fill="white", outline="black", width=3)

    # the readout
    d.text((20, 24), f"{t / 1000:5.2f} s", fill="black", font=F, anchor="lm")
    d.text((20, 50), f"eye  {head_deg:+5.1f}°", fill="black", font=F, anchor="lm")
    d.text((20, 76), f"neck {neck_deg:+5.1f}°", fill="black", font=F, anchor="lm")
    d.text((20, 102), f"gaze {head_deg + neck_deg:+5.1f}°", fill="black", font=F, anchor="lm")
    d.text((20, 128), f"cell {busy if busy else '—'}", fill="black", font=F, anchor="lm")
    d.text((W - 20, 24), title, fill="black", font=F, anchor="rm")
    if note:
        d.text((W - 20, 50), note, fill="black", font=FS, anchor="rm")

    # what the vehicle itself has to go on
    for top, bottom, label, n in rows:
        d.line([(RASTER_L, bottom + 4), (RASTER_R, bottom + 4)], fill="black", width=1)
        d.text((RASTER_L - 12, (top + bottom) / 2), label, fill="black", font=FS,
               anchor="rm")
    for (rt, row, index, on) in raster:
        if t - rt > WINDOW_MS:
            continue
        x = RASTER_L + (RASTER_R - RASTER_L) * (1 - (t - rt) / WINDOW_MS)
        top, bottom, _, n = rows[row]
        y = top + (bottom - top) * (index - 1) / (n - 1)
        d.line([(x, y - 4), (x, y + 4)], fill="black", width=3 if on else 1)
    d.text((RASTER_L, rows[-1][1] + 12), f"the last {WINDOW_MS / 1000:g} s",
           fill="black", font=FT, anchor="lm")

    # and the ground truth, which it has not
    span, lo, hi = scale
    y_of = lambda deg: PLOT_B - (PLOT_B - PLOT_T) * (deg - lo) / (hi - lo)   # noqa: E731
    d.line([(RASTER_L, y_of(0)), (RASTER_R, y_of(0))], fill="black", width=1)
    d.text((RASTER_L - 12, y_of(0)), "0°", fill="black", font=FT, anchor="rm")
    d.text((RASTER_L - 12, PLOT_T), f"{hi:.0f}°", fill="black", font=FT, anchor="rm")
    if lo < 0:
        d.text((RASTER_L - 12, PLOT_B), f"{lo:.0f}°", fill="black", font=FT, anchor="rm")
    for name, wide, nudge in (("gaze", 4, -11), ("eye", 2, 0), ("neck", 2, 11)):
        pts = [(RASTER_L + (PLOT_R - RASTER_L) * s / max(span, 1), y_of(v[name]))
               for s, v in trace if s <= t]
        if len(pts) > 1:
            d.line(pts, fill="black", width=wide, joint="curve")
            if t > span * 0.2:      # before that the three are on top of each other
                d.text((pts[-1][0] + 6, pts[-1][1] + nudge), name, fill="black",
                       font=FT, anchor="lm")
    return im


def animate(path="vehicle2_a.gif", seconds=8.0, seed=1, object_deg=36.0, every=80,
            comfort=None, moving=False, note=None, right=None):
    where = (standing_then_right(object_deg, right * 1000) if right is not None
             else experiment_path(object_deg) if moving else None)
    world = World(object_deg=object_deg, path=where)
    neck = RecentringController() if comfort is None else RecentringController(comfort=comfort)
    vehicle = Vehicle2(world, rng=random.Random(seed),
                       controller=GazeController(neck=neck))
    raster, frames, trace = deque(maxlen=8000), [], []
    total = int(seconds * 1000)
    peak, low = 1.0, 0.0
    for t in Clock().times(total):
        world.update(t)
        fired = vehicle.step(t)
        for e in fired.get("retina", ()):
            raster.append((t, 0, e.address[0], e.p is ON))
        for row, joint in ((1, "head"), (2, "neck")):
            for e in fired.get(f"proprioception.{joint}.{LEFT}", ()):
                if e.p is ON:
                    raster.append((t, row, e.address[0], True))
        angles = {"eye": vehicle.head_deg, "neck": vehicle.neck_deg,
                  "gaze": vehicle.gaze_deg}
        peak, low = max(peak, *angles.values()), min(low, *angles.values())
        trace.append((t, angles))
        if t % (every * TICK_MS) == 0:
            frames.append((t, vehicle.head_deg, vehicle.neck_deg,
                           vehicle.retina.busy_cell(), world.object_deg, list(raster)))
    scale = (total, math.floor(low / 5) * 5, math.ceil(peak / 5) * 5)
    images = [frame(*f, trace, scale, note=note) for f in frames]
    images[0].save(path, save_all=True, append_images=images[1:],
                   duration=every * TICK_MS, loop=0, optimize=True)
    return path, len(images)


def animate_b(path="vehicle2_b.gif", seconds=11.0, seed=1, object_deg=36.0, every=100,
              taught=120.0, right=5.0, note=None, moving=False, truth=False):
    """Version B: a layer on each joint, the eye's taught first and then frozen.

    With `truth`, the head is driven by the ground truth of Version A instead —
    the rig of spec 006 that asks what the neck's layer learnt, rather than what
    the pair of them manage.
    """
    from ..run import taught_pair
    eye, neck = taught_pair(taught, seed, 18.0)
    where = (experiment_path(object_deg) if moving else
             standing_then_right(object_deg, right * 1000) if right else None)
    world = World(object_deg=object_deg, path=where)
    vehicle = Vehicle2(world, rng=random.Random(seed + 2), neck_reflex=neck, vor=True,
                       controller=GazeController(vor=False) if truth else None,
                       eye_reflex=None if truth else eye)
    raster, frames, trace = deque(maxlen=8000), [], []
    total = int(seconds * 1000)
    peak, low = 1.0, 0.0
    for t in Clock().times(total):
        world.update(t)
        fired = vehicle.step(t)
        for e in fired.get("retina", ()):
            raster.append((t, 0, e.address[0], e.p is ON))
        for e in fired.get(f"proprioception.{HEAD}.{LEFT}", ()):
            if e.p is ON:
                raster.append((t, 1, e.address[0], True))
        for e in fired.get("sensory.neck", ()):
            raster.append((t, 2, e.address[1], True))       # the sensor it arrived at
        for side in (LEFT, RIGHT):
            for _ in fired.get(f"effector.{NECK}.{side}", ()):
                raster.append((t, 3, 1 if side is LEFT else 2, True))
            for _ in fired.get(f"effector.{HEAD}.{side}", ()):
                raster.append((t, 4, 1 if side is LEFT else 2, True))
        angles = {"eye": vehicle.head_deg, "neck": vehicle.neck_deg,
                  "gaze": vehicle.gaze_deg}
        peak, low = max(peak, *angles.values()), min(low, *angles.values())
        trace.append((t, angles))
        if t % (every * TICK_MS) == 0:
            frames.append((t, vehicle.head_deg, vehicle.neck_deg,
                           vehicle.retina.busy_cell(), world.object_deg, list(raster)))
    scale = (total, math.floor(low / 5) * 5, math.ceil(peak / 5) * 5)
    images = [frame(*f, trace, scale, title="Version B: the neck's layer, learnt",
                    note=note, rows=ROWS_B) for f in frames]
    images[0].save(path, save_all=True, append_images=images[1:],
                   duration=every * TICK_MS, loop=0, optimize=True)
    return path, len(images)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="docs/images/vehicle2_a.gif")
    p.add_argument("--seconds", type=float, default=8.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--object", type=float, default=36.0)
    p.add_argument("--comfort", type=float, help="the eye's comfortable range")
    p.add_argument("--every", type=int, default=80, help="ticks between frames")
    p.add_argument("--moving", action="store_true", help="the object slides")
    p.add_argument("--right", type=float, metavar="SECONDS",
                   help="the object stands still for this long, then goes right")
    p.add_argument("--note", help="a line under the title")
    p.add_argument("--taught", type=float, metavar="SECONDS",
                   help="Version B: teach each layer for this long, the eye first")
    p.add_argument("--truth", action="store_true",
                   help="and put the head on Version A, to ask what the neck learnt")
    a = p.parse_args()
    if a.taught:
        path, n = animate_b(a.out, a.seconds, a.seed, a.object, a.every, a.taught,
                            a.right or 0.0, a.note, a.moving, a.truth)
    else:
        path, n = animate(a.out, a.seconds, a.seed, a.object, a.every, a.comfort,
                          a.moving, a.note, a.right)
    print(f"{n} frames -> {path}")
