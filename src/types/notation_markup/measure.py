from collections import namedtuple
from typing import NamedTuple

MeasurePosition = namedtuple('MeasurePosition', ['start', 'end', 'first_on_staff', 'last_on_staff'])


class MeasurePlacement(NamedTuple):
    start: float
    end: float
    first_on_staff: bool
    last_on_staff: bool
