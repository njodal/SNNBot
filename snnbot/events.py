"""The one thing that crosses between components: a spike."""

from dataclasses import dataclass
from enum import Enum


class Polarity(Enum):
    ON = "on"
    OFF = "off"

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Event:
    """`(t, address, p)` of spec 001. No magnitude: an event is an event."""

    t: int                  # milliseconds
    address: tuple          # which element fired, its shape is the sensor's own
    p: Polarity

    def __str__(self):
        return f"{','.join(str(a) for a in self.address)} {self.p}"


ON, OFF = Polarity.ON, Polarity.OFF
