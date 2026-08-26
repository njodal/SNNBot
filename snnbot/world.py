"""What is out there. For now: one object, somewhere in front of the vehicle.

Angles are degrees, measured from straight ahead, positive towards the left.
"""

from dataclasses import dataclass


@dataclass
class World:
    object_deg: float = 0.0

    def place(self, deg):
        self.object_deg = deg
