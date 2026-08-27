"""What is out there. For now: one object, somewhere in front of the vehicle.

Angles are degrees, measured from straight ahead, positive towards the left.
One object is all this vehicle needs: with a single source of light there is
never more than one cell of the eye occupied, which is what spec 005 asks for
without having to model any lateral inhibition.
"""

from dataclasses import dataclass
from typing import Callable, Optional

from .params import (OBJECT_MOVING_MS, OBJECT_RATE_DEG_S, OBJECT_START_DEG,
                     OBJECT_STILL_MS)


@dataclass
class World:
    object_deg: float = 0.0
    path: Optional[Callable[[int], float]] = None   # None: it stands still

    def place(self, deg):
        self.object_deg = deg

    def update(self, t):
        """The world moves on its own. Nothing in the vehicle can move it."""
        if self.path is not None:
            self.object_deg = self.path(t)


def still_then_left(start_deg=OBJECT_START_DEG, still_ms=OBJECT_STILL_MS,
                    rate=OBJECT_RATE_DEG_S, moving_ms=OBJECT_MOVING_MS):
    """The experiment: a second of nothing, then a second sliding to the left.

    The still part is there to let the vehicle settle before anything is asked
    of it, so that what happens next is a response and not a leftover.
    """
    def where(t):
        if t <= still_ms:
            return start_deg
        return start_deg + rate * min(t - still_ms, moving_ms) / 1000
    return where
