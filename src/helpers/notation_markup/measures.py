from itertools import groupby
from typing import List, Dict

from ...types import Measure, StaffProperties, PageProperties


def guess_measure_octave(measure: Measure) -> Dict[int, int]:
    notes = {k: list(v) for k, v in groupby(measure.notes, lambda x: x.staff)}
    from statistics import median
    octaves = {}
    for k, v in notes.items():
        if k is None:
            k = 1
        try:
            octaves[k] = median([n.pitch.octave if n.pitch else None for n in v])
        except:
            octaves[k] = None

    return octaves


def max_guess_parted_measure_length(
        page_prop: PageProperties,
        staff_prop: StaffProperties,
        measures: List[Measure],
        measures_left_count,
        page_width_left):
    avg_measures_per_page = 5
    avg_measure_length = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // avg_measures_per_page

    notes_count_multiplier = 1

    suggested_measure_count = page_width_left // (avg_measure_length*notes_count_multiplier)
    if suggested_measure_count > measures_left_count:
        suggested_measure_count = measures_left_count

    suggested_length = round(page_width_left // suggested_measure_count, 3)

    print(f'{avg_measure_length=} {suggested_measure_count=}')
    print(f'{page_width_left=} {measures_left_count=} {suggested_length=}')
    return suggested_length
