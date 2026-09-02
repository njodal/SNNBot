"""Run a vehicle, headless, and say what happened."""

import argparse
import random

from .body.vehicle1 import Vehicle1
from .body.vehicle2 import Vehicle2
from .clock import Clock
from .control import GazeController, ProportionalController
from .layers.sensory import (CorrelationReflex, LearningReflex, PostureReflex,
                             Reflex)

from .recorder import Recorder
from .params import HEAD_EFFECTORS
from .world import World, experiment_path, wandering


def run(seconds=10.0, seed=1, object_deg=18.0, wired=False, controller=None,
        path=None, reflex=None, vehicle_cls=Vehicle1, eye_reflex=None,
        neck_reflex=None, vor=False):
    world = World(object_deg=object_deg, path=path)
    extra = {"reflex": reflex} if reflex is not None else {}
    if eye_reflex is not None or neck_reflex is not None:
        vehicle_cls = Vehicle2
        extra = {"eye_reflex": eye_reflex, "neck_reflex": neck_reflex, "vor": vor}
    vehicle = vehicle_cls(world, rng=random.Random(seed), wired=wired,
                          controller=controller, **extra)
    recorder, clock = Recorder(), Clock()
    for t in clock.times(int(seconds * 1000)):
        world.update(t)          # the world moves whether or not anyone looks
        for source, events in vehicle.step(t).items():
            recorder.record(t, source, events)
    return vehicle, recorder


def frozen(layer):
    """Done learning: what it has is what it will use."""
    layer.learning, layer.explore = False, 0.0
    return layer


def taught_pair(seconds, seed, object_deg):
    """Version B of spec 006: a layer on each joint, taught one at a time.

    The eye's is Version D of spec 005 unchanged. The neck's is the same circuit
    reading the head's propioceptive array, so what it learns about is where the
    eye is sitting rather than where the object is.

    The eye goes first and is frozen before the neck begins, and both halves of
    that are needed. A neck that babbles while the eye is being taught makes the
    object appear to move, which is the one thing Version D is taught against a
    still object to avoid. And a neck has nothing to learn from until the eye
    works: moving the neck does not move the head joint — it swings the gaze, and
    only the eye's answer to that moves what the neck's layer reads.
    """
    eye = LearningReflex(random.Random(seed), effectors=len(HEAD_EFFECTORS))
    run(seconds, seed + 1, object_deg, eye_reflex=eye)              # the eye alone
    frozen(eye)

    neck = PostureReflex(random.Random(seed + 3))
    run(seconds, seed + 1, object_deg, eye_reflex=eye, neck_reflex=neck, vor=True)
    return eye, frozen(neck)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seconds", type=float, default=10.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--object", type=float, default=18.0, help="degrees left of ahead")
    p.add_argument("--pid", action="store_true", help="run Version A, the ground truth")
    p.add_argument("--neck", action="store_true",
                   help="run Version A of Vehicle 2: a PID per joint — the eye on what "
                        "it sees, the neck on where the eye is sitting")
    p.add_argument("--reflex", action="store_true", help="run Version B, the reflex")
    p.add_argument("--correlation", action="store_true",
                   help="run Version C, the reflex on a neuromorphic eye")
    p.add_argument("--learn", type=float, metavar="SECONDS",
                   help="run Version D, taught for this long first")
    p.add_argument("--moving", action="store_true",
                   help="the object waits a second, then slides left for another")
    args = p.parse_args()

    vehicle_cls = Vehicle2 if args.neck else Vehicle1
    controller = (GazeController() if args.neck
                  else ProportionalController() if args.pid else None)
    reflex = Reflex() if args.reflex else CorrelationReflex() if args.correlation else None
    if args.neck and args.learn:
        eye_reflex, neck_reflex = taught_pair(args.learn, args.seed, args.object)
        print(f"taught {args.learn:g} s a layer\n")
        path = experiment_path(args.object) if args.moving else None
        vehicle, rec = run(args.seconds, args.seed, args.object, path=path,
                           eye_reflex=eye_reflex, neck_reflex=neck_reflex, vor=True)
        print(f"{args.seconds:g} s of a layer on each joint, seed {args.seed}, "
              f"object at {args.object:g} degrees\n")
        for source, n in sorted(rec.counts().items()):
            print(f"  {n:6d}  {source}")
        print(f"\n  eye ended at {vehicle.head_deg:+.1f} degrees, "
              f"neck at {vehicle.neck_deg:+.1f}, gaze at {vehicle.gaze_deg:+.1f}, "
              f"object seen by cell {vehicle.retina.busy_cell()}")
        return
    if args.learn:
        # The two go together: cells that read a speed, and an object that has
        # one to read. Either alone leaves the vehicle worse off than neither.
        reflex = LearningReflex(random.Random(args.seed), speed=True)
        taught, _ = run(args.learn, args.seed, args.object, reflex=reflex,
                        path=wandering(random.Random(args.seed + 7)))
        reflex.learning, reflex.explore = False, 0.0
        print(f"taught for {args.learn:g} s\n")
    path = experiment_path(args.object) if args.moving else None
    vehicle, rec = run(args.seconds, args.seed, args.object, controller=controller,
                       path=path, reflex=reflex, vehicle_cls=vehicle_cls)
    what = ('a PID on each joint' if args.neck
            else 'the ground truth' if args.pid else 'the reflex' if args.reflex
            else 'what it learnt' if args.learn
            else 'the correlation cells' if args.correlation else 'babbling')
    print(f"{args.seconds:g} s of {what}, "
          f"seed {args.seed}, object at {args.object:g} degrees\n")
    for source, n in sorted(rec.counts().items()):
        print(f"  {n:6d}  {source}")
    ended = f"head ended at {vehicle.head_deg:+.1f} degrees"
    if args.neck:
        ended += (f", neck at {vehicle.neck_deg:+.1f}, "
                  f"gaze at {vehicle.gaze_deg:+.1f}")
    print(f"\n  {ended}, object seen by cell {vehicle.retina.busy_cell()}")

    eye = rec.of("retina")
    print(f"\n  the eye fired {len(eye)} times; the first few:")
    for t, e in eye[:6]:
        print(f"    {t:6d} ms  {e}")


if __name__ == "__main__":
    main()
