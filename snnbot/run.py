"""Run a vehicle, headless, and say what happened."""

import argparse
import random

from .body.vehicle1 import Vehicle1
from .clock import Clock
from .control import ProportionalController

from .recorder import Recorder
from .world import World, still_then_left


def run(seconds=10.0, seed=1, object_deg=18.0, wired=False, controller=None,
        path=None):
    world = World(object_deg=object_deg, path=path)
    vehicle = Vehicle1(world, rng=random.Random(seed), wired=wired, controller=controller)
    recorder, clock = Recorder(), Clock()
    for t in clock.times(int(seconds * 1000)):
        world.update(t)          # the world moves whether or not anyone looks
        for source, events in vehicle.step(t).items():
            recorder.record(t, source, events)
    return vehicle, recorder


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seconds", type=float, default=10.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--object", type=float, default=18.0, help="degrees left of ahead")
    p.add_argument("--pid", action="store_true", help="run Version A, the ground truth")
    p.add_argument("--moving", action="store_true",
                   help="the object waits a second, then slides left for another")
    args = p.parse_args()

    controller = ProportionalController() if args.pid else None
    path = still_then_left(args.object) if args.moving else None
    vehicle, rec = run(args.seconds, args.seed, args.object, controller=controller,
                       path=path)
    print(f"{args.seconds:g} s of {'the ground truth' if args.pid else 'babbling'}, "
          f"seed {args.seed}, object at {args.object:g} degrees\n")
    for source, n in sorted(rec.counts().items()):
        print(f"  {n:6d}  {source}")
    print(f"\n  head ended at {vehicle.head_deg:+.1f} degrees, "
          f"object seen by cell {vehicle.retina.busy_cell()}")

    eye = rec.of("retina")
    print(f"\n  the eye fired {len(eye)} times; the first few:")
    for t, e in eye[:6]:
        print(f"    {t:6d} ms  {e}")


if __name__ == "__main__":
    main()
