from itertools import groupby
from typing import List, Dict

from ...types import Measure, StaffProperties, PageProperties, MeasurePosition


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


# TODO reorganize measure guess
def max_guess_parted_measure_length(
        page_prop: PageProperties,
        staff_prop: StaffProperties,
        measures: List[Measure],
        measures_left_count,
        page_width_left):
    avg_measures_per_page = 5
    avg_measure_length = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // avg_measures_per_page

    notes_count_multiplier = 1

    suggested_measure_count = page_width_left // (avg_measure_length * notes_count_multiplier)
    if suggested_measure_count > measures_left_count:
        suggested_measure_count = measures_left_count

    suggested_length = round(page_width_left // suggested_measure_count, 3)

    print(f'{avg_measure_length=} {suggested_measure_count=}')
    print(f'{page_width_left=} {measures_left_count=} {suggested_length=}')
    return suggested_length


def guess_measure_length(page_prop, staff_prop, total_measures_count, measures, measure_number, measure_start_position):
    page_staff_end = page_prop.width - staff_prop.right_offset
    measures_left_count = total_measures_count - measure_number
    page_width_left = page_staff_end - measure_start_position

    print(f'{page_width_left=} {measure_start_position=} {measures_left_count=}')
    measure_length = max_guess_parted_measure_length(
        page_prop=page_prop,
        staff_prop=staff_prop,
        measures=measures,
        measures_left_count=measures_left_count,
        page_width_left=page_width_left
    )
    return measure_length


# only horizontal coords
def place_next_measure(page_prop, staff_prop, start_measure_position, measure_length):
    last_in_line = False
    staff_unused_width = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // 20

    # measure length
    page_staff_end = page_prop.width - staff_prop.right_offset
    measure_start_position = start_measure_position
    measure_end_position = measure_start_position + measure_length

    if page_staff_end - measure_end_position < staff_unused_width:
        last_in_line = True
        measure_end_position = page_staff_end

    return MeasurePosition(start_measure_position, measure_end_position, last_in_line)
