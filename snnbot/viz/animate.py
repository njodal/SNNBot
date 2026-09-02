"""Render a run to an animated GIF: the vehicle moving, and what it fired.

The object stays where it is. What moves is the head, and with it which cell of
the eye is looking at the object.
"""

import math
import random
from collections import deque

from PIL import Image, ImageDraw, ImageFont

from ..body.vehicle1 import LEFT, RIGHT, Vehicle1
from ..clock import Clock
from ..control import ProportionalController
from ..layers.sensory import CorrelationReflex, LearningReflex, Reflex, ValueReflex
from ..events import ON
from ..params import CELL_ANGLE_DEG, EYE_CELLS, TICK_MS
from ..world import World, experiment_path, wandering

W, H = 760, 760
CELL = 34
EYE_L = (W - EYE_CELLS * CELL) // 2
EYE_T, EYE_B = 250, 250 + CELL
JOINT = (W // 2, EYE_B)
BASE_Y = 440

# How far out to draw the object. The eye works in angles measured from the
# joint, so a perpendicular dropped from the object onto the head only lands on
# the cell that is actually seeing it if the object is drawn at this distance —
# the one where a cell's width and a cell's angle are the same thing.
OBJECT_R = CELL * 180 / (math.pi * CELL_ANGLE_DEG)
WINDOW_MS = 2000                    # how much of the past the raster shows
RASTER_L, RASTER_R = 170, W - 20
ROWS = ((500, 552, "eye"), (566, 584, "effector L"), (594, 612, "effector R"))


def _font(sz):
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", sz)


F, FS, FT = _font(20), _font(15), _font(14)


def _rot(p, deg):
    a = math.radians(deg)
    dx, dy = p[0] - JOINT[0], p[1] - JOINT[1]
    return (JOINT[0] + dx * math.cos(a) - dy * math.sin(a),
            JOINT[1] + dx * math.sin(a) + dy * math.cos(a))


REST_LENGTH = math.hypot(CELL * 2.25, BASE_Y - EYE_B)


def _zigzag(d, p0, p1, n=11, base=REST_LENGTH):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    amp = min(8 * (base / L) ** 2, L * 0.14)     # a short actuator has fatter waves
    px, py = -dy / L, dx / L
    pts = [(x0, y0)]
    for i in range(n + 1):
        t = 0.16 + 0.68 * i / n
        s = 0 if i in (0, n) else amp * (1 if i % 2 else -1)
        pts.append((x0 + dx * t + px * s, y0 + dy * t + py * s))
    pts.append((x1, y1))
    d.line(pts, fill="black", width=3, joint="curve")


NAMES = {"ProportionalController": "Version A: ground truth",
         "Reflex": "Version B: reflex",
         "CorrelationReflex": "Version C: correlation cells",
         "LearningReflex": "Version D: what it learnt",
         "ValueReflex": "Version E: what it worked out"}


def _title(controller, reflex):
    """Which vehicle this is, by what is driving it."""
    return NAMES.get(type(controller or reflex).__name__, "motor babbling")


def frame(t, head_deg, busy, object_deg, levels, raster, title="motor babbling",
          note=None, values=None):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    # A head turned to the left is a head whose left end has been pulled down, so
    # on screen the bar turns the other way round from the angle.
    tilt = -head_deg

    # the object, fixed out there
    ang = math.radians(object_deg)
    ox, oy = JOINT[0] - OBJECT_R * math.sin(ang), JOINT[1] - OBJECT_R * math.cos(ang)
    d.ellipse([ox - 11, oy - 11, ox + 11, oy + 11], fill="black")
    d.text((ox + 18, oy), "object", fill="black", font=FS, anchor="lm")

    # stem and base do not move
    d.line([JOINT, (JOINT[0], BASE_Y)], fill="black", width=3)
    d.line([(JOINT[0] - 120, BASE_Y), (JOINT[0] + 120, BASE_Y)], fill="black", width=5)
    for x in range(JOINT[0] - 120, JOINT[0] + 121, 16):
        d.line([(x, BASE_Y + 3), (x - 13, BASE_Y + 20)], fill="black", width=2)

    # the two actuators
    for side, at in ((LEFT, (EYE_L + CELL * 2.25, EYE_B)), (RIGHT, (EYE_L + CELL * 6.75, EYE_B))):
        _zigzag(d, _rot(at, tilt), (JOINT[0], BASE_Y))

    # the eye
    if busy:
        x0, x1 = EYE_L + (busy - 1) * CELL, EYE_L + busy * CELL
        d.polygon([_rot((x0, EYE_T), tilt), _rot((x1, EYE_T), tilt),
                   _rot((x1, EYE_B), tilt), _rot((x0, EYE_B), tilt)], fill="black")
        # Which cell of the head the object falls on, dropped straight onto it.
        a = math.radians(tilt)
        ux, uy = math.cos(a), math.sin(a)                  # along the head
        mx, my = _rot((EYE_L + EYE_CELLS * CELL / 2, (EYE_T + EYE_B) / 2), tilt)
        along = (ox - mx) * ux + (oy - my) * uy
        fx, fy = mx + along * ux, my + along * uy          # the foot on the head
        sx, sy = ox + (ox - fx) * 0.35, oy + (oy - fy) * 0.35
        for k in range(0, 26, 2):
            d.line([(sx + (fx - sx) * k / 26, sy + (fy - sy) * k / 26),
                    (sx + (fx - sx) * (k + 1) / 26, sy + (fy - sy) * (k + 1) / 26)],
                   fill="black", width=1)

    for c in range(1, EYE_CELLS):
        x = EYE_L + c * CELL
        d.line([_rot((x, EYE_T), tilt), _rot((x, EYE_B), tilt)], fill="black", width=3)
    corners = [(EYE_L, EYE_T), (EYE_L + EYE_CELLS * CELL, EYE_T),
               (EYE_L + EYE_CELLS * CELL, EYE_B), (EYE_L, EYE_B), (EYE_L, EYE_T)]
    d.line([_rot(p, tilt) for p in corners], fill="black", width=2, joint="curve")
    d.ellipse([JOINT[0] - 12, JOINT[1] - 12, JOINT[0] + 12, JOINT[1] + 12],
              fill="white", outline="black", width=3)

    # the readout
    d.text((20, 24), f"{t / 1000:5.2f} s", fill="black", font=F, anchor="lm")
    d.text((20, 50), f"head {head_deg:+5.1f}°", fill="black", font=F, anchor="lm")
    d.text((20, 76), f"cell {busy if busy else '—'}", fill="black", font=F, anchor="lm")
    d.text((W - 20, 24), title, fill="black", font=F, anchor="rm")
    if note:
        d.text((W - 20, 76), note, fill="black", font=FS, anchor="rm")
    d.text((W - 20, 50), f"contraction  L {levels[LEFT]:5.1f}   R {levels[RIGHT]:5.1f}",
           fill="black", font=FS, anchor="rm")

    # the raster of the last couple of seconds
    for top, bottom, label in ROWS:
        d.line([(RASTER_L, bottom + 4), (RASTER_R, bottom + 4)], fill="black", width=1)
        d.text((RASTER_L - 12, (top + bottom) / 2), label, fill="black", font=FS, anchor="rm")
    for (rt, row, cell, on) in raster:
        if t - rt > WINDOW_MS:
            continue
        x = RASTER_L + (RASTER_R - RASTER_L) * (1 - (t - rt) / WINDOW_MS)
        top, bottom, _ = ROWS[row]
        if row == 0:
            y = top + (bottom - top) * (cell - 1) / (EYE_CELLS - 1)
            d.line([(x, y - 4), (x, y + 4)], fill="black", width=3 if on else 1)
        else:
            d.line([(x, top), (x, bottom)], fill="black", width=2)
    d.text((RASTER_L, 630), f"the last {WINDOW_MS / 1000:g} s", fill="black", font=FS, anchor="lm")

    if values:                      # the hump it worked out, cell by cell
        base, high, wide = 730, 70, 44
        most = max(max(values.values()), 0.01)
        for cell, worth in sorted(values.items()):
            x = RASTER_L + (cell - 1) * wide
            tall = max(worth, 0) / most * high
            d.rectangle([x, base - tall, x + wide - 10, base], fill="black")
            d.text((x + (wide - 10) / 2, base + 14), str(cell), fill="black",
                   font=FT, anchor="mm")
        d.text((RASTER_L + 9 * wide + 16, base - high / 2),
               "what it worked out\neach cell is worth", fill="black", font=FT, anchor="lm")
    return im


def animate(path="babbling.gif", seconds=8.0, seed=2, object_deg=18.0, every=80,
            controller=None, moving=False, reflex=None):
    world = World(object_deg=object_deg,
                  path=experiment_path(object_deg) if moving else None)
    vehicle = Vehicle1(world, rng=random.Random(seed), controller=controller,
                       reflex=reflex)
    clock, raster, frames = Clock(), deque(maxlen=4000), []
    for t in clock.times(int(seconds * 1000)):
        world.update(t)          # the world moves whether or not anyone looks
        fired = vehicle.step(t)
        for e in fired.get("retina", ()):
            raster.append((t, 0, e.address[0], e.p is ON))
        for row, side in ((1, LEFT), (2, RIGHT)):
            for _ in fired.get(f"effector.{side}", ()):
                raster.append((t, row, 0, True))
        if t % (every * TICK_MS) == 0:
            levels = {s: vehicle.actuators[s].level for s in (LEFT, RIGHT)}
            frames.append(frame(t, vehicle.head_deg, vehicle.retina.busy_cell(),
                                world.object_deg, levels, list(raster),
                                _title(controller, reflex),
                                values=getattr(getattr(reflex, "critic", None), "value", None)))
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=every * TICK_MS, loop=0, optimize=True)
    return path, len(frames)


def _taught(a, cls=LearningReflex):
    """The vehicle that learns, put through its schooling before anyone watches.

    Against an object that wanders, and with the cells that read a speed: the
    two go together, either alone leaving it worse off than neither.
    """
    from ..body.vehicle1 import Vehicle1
    from ..clock import Clock
    reflex = cls(random.Random(a.seed), speed=True)
    world = World(object_deg=a.object, path=wandering(random.Random(a.seed + 7)))
    v = Vehicle1(world, rng=random.Random(a.seed), reflex=reflex)
    for t in Clock().times(int((a.value or a.learn) * 1000)):
        world.update(t)
        v.step(t)
    reflex.learning, reflex.explore = False, 0.0
    return reflex


def learning(path="learning.gif", train_s=240.0, windows=((0, 8), (116, 124), (232, 240)),
             seed=1, object_deg=18.0, every=100):
    """Watch it being taught: the same eight seconds early, halfway and at the end.

    The object never moves, so the only thing that can make it visible is the
    vehicle moving itself. Early on that is all there is — flailing, and the
    object wherever it happens to fall. By the end the flailing has been
    replaced by whatever the weights have come to say.
    """
    from ..layers.sensory import LearningReflex

    reflex = LearningReflex(random.Random(seed))
    world = World(object_deg=object_deg)
    vehicle = Vehicle1(world, rng=random.Random(seed + 1), reflex=reflex)
    raster, frames = deque(maxlen=4000), []
    for t in Clock().times(int(train_s * 1000)):
        fired = vehicle.step(t)
        for e in fired.get("retina", ()):
            raster.append((t, 0, e.address[0], e.p is ON))
        for row, side in ((1, LEFT), (2, RIGHT)):
            for _ in fired.get(f"effector.{side}", ()):
                raster.append((t, row, 0, True))
        if t % (every * TICK_MS) or not any(a * 1000 <= t < b * 1000 for a, b in windows):
            continue
        knows = sum(any(w.values()) for w in reflex.weights.values())
        levels = {s: vehicle.actuators[s].level for s in (LEFT, RIGHT)}
        frames.append(frame(t, vehicle.head_deg, vehicle.retina.busy_cell(),
                            object_deg, levels, list(raster), "Version D: being taught",
                            f"taught {t / 1000:5.1f} s   ·   {knows} of 72 cells know something"))
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=every * TICK_MS, loop=0, optimize=True)
    return path, len(frames)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="babbling.gif")
    p.add_argument("--seconds", type=float, default=8.0)
    p.add_argument("--seed", type=int, default=2)
    p.add_argument("--object", type=float, default=18.0)
    p.add_argument("--pid", action="store_true", help="Version A, the ground truth")
    p.add_argument("--reflex", action="store_true", help="Version B, the reflex")
    p.add_argument("--correlation", action="store_true", help="Version C")
    p.add_argument("--learn", type=float, metavar="SECONDS",
                   help="Version D, taught for this long first")
    p.add_argument("--value", type=float, metavar="SECONDS",
                   help="Version E, taught for this long first")
    p.add_argument("--every", type=int, default=80, help="ticks between frames")
    p.add_argument("--moving", action="store_true", help="the object slides left")
    a = p.parse_args()
    path, n = animate(a.out, a.seconds, a.seed, a.object, a.every,
                      controller=ProportionalController() if a.pid else None,
                      moving=a.moving, reflex=_taught(a, ValueReflex) if a.value else
                             _taught(a) if a.learn else
                             Reflex() if a.reflex else
                             CorrelationReflex() if a.correlation else None)
    print(f"{n} frames -> {path}")
