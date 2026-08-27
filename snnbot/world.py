"""What is out there. For now: one object, somewhere in front of the vehicle.

Angles are degrees, measured from straight ahead, positive towards the left.
One object is all this vehicle needs: with a single source of light there is
never more than one cell of the eye occupied, which is what spec 005 asks for
without having to model any lateral inhibition.
"""

from dataclasses import dataclass
from typing import Callable, Optional

from .params import (OBJECT_LEFT_MS, OBJECT_RATE_DEG_S, OBJECT_RIGHT_MS,
                     OBJECT_START_DEG, OBJECT_STILL_MS)


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


def experiment_path(start_deg=OBJECT_START_DEG, still_ms=OBJECT_STILL_MS,
                    rate=OBJECT_RATE_DEG_S, left_ms=OBJECT_LEFT_MS,
                    right_ms=OBJECT_RIGHT_MS):
    """Where the object is through the experiment of spec 005.

    A while of nothing, then off to the left, then a longer while back to the
    right, and still again. The still part at the start is there to let the
    vehicle settle, so that what follows is a response and not a leftover. The
    turn is there because following something is not the same as following it
    back: it is the reversal that asks the vehicle whether it noticed.
    """
    def where(t):
        if t <= still_ms:
            return start_deg
        gone_left = min(t - still_ms, left_ms) / 1000
        deg = start_deg + rate * gone_left
        if t <= still_ms + left_ms:
            return deg
        gone_right = min(t - still_ms - left_ms, right_ms) / 1000
        return deg - rate * gone_right
    return where
