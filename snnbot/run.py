"""Run a vehicle, headless, and say what happened."""

import argparse
import random

from .body.vehicle1 import Vehicle1
from .clock import Clock

from .recorder import Recorder
from .world import World


def run(seconds=10.0, seed=1, object_deg=18.0, wired=False):
    world = World(object_deg=object_deg)
    vehicle = Vehicle1(world, rng=random.Random(seed), wired=wired)
    recorder, clock = Recorder(), Clock()
    for t in clock.times(int(seconds * 1000)):
        for source, events in vehicle.step(t).items():
            recorder.record(t, source, events)
    return vehicle, recorder


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seconds", type=float, default=10.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--object", type=float, default=18.0, help="degrees left of ahead")
    args = p.parse_args()

    vehicle, rec = run(args.seconds, args.seed, args.object)
    print(f"{args.seconds:g} s of babbling, seed {args.seed}, "
          f"object at {args.object:g} degrees\n")
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
