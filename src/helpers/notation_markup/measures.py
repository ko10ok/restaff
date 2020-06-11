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
            octaves[k] = int(median([n.pitch.octave if n.pitch else None for n in v]))
        except:
            octaves[k] = None

    return octaves


# TODO reorganize measure guess
def calc_measure_length(page_prop, staff_prop, measures: List[Measure]):
    avg_measures_per_page = 4
    avg_measure_length = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // avg_measures_per_page

    max_notes_count = max([
        max([len(list(notes)) for staff, notes in groupby(measure.notes, lambda x: x.staff)])
        for measure in measures
    ])
    notes_count_multiplier = max(max_notes_count / 4, 0.5)
    return avg_measure_length * notes_count_multiplier


def fit_measure_length_in_page(page_prop: PageProperties,
                               staff_prop: StaffProperties,
                               measure_length,
                               measure_start_position):
    page_staff_end = page_prop.width - staff_prop.right_offset
    page_width_left = page_staff_end - measure_start_position
    return min(page_width_left, measure_length)


def max_guess_parted_measure_length(
        page_prop: PageProperties,
        staff_prop: StaffProperties,
        measures: List[Measure],
        measures_left_count,
        page_width_left):
    avg_measures_per_page = 4
    avg_measure_length = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // avg_measures_per_page

    max_notes_count = max([
        max([len(list(notes)) for staff, notes in groupby(measure.notes, lambda x: x.staff)])
        for measure in measures
    ])
    print(f'{max_notes_count=}')
    notes_count_multiplier = max(max_notes_count / 8, 0.5)

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
def place_next_measure(page_prop, staff_prop, last_measure_placement: MeasurePosition, measure_length):
    last_on_staff = False
    staff_unused_width = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // 20

    # measure length
    page_staff_end = page_prop.width - staff_prop.right_offset
    measure_start_position = last_measure_placement.end
    measure_end_position = measure_start_position + measure_length

    # if page_staff_end - measure_end_position < staff_unused_width:
    #     last_on_staff = True
    #     measure_end_position = page_staff_end

    return MeasurePosition(
        last_measure_placement.end, measure_end_position,
        first_on_staff=last_measure_placement.last_on_staff,
        last_on_staff=last_on_staff
    )


def correct_measure(page_prop: PageProperties, staff_prop: StaffProperties, measure_placement: MeasurePosition,
                    next_measure_length):
    page_staff_end = page_prop.width - staff_prop.right_offset
    if page_staff_end - measure_placement.end < next_measure_length:
        return MeasurePosition(
            start=measure_placement.start,
            end=page_staff_end,
            first_on_staff=False,
            last_on_staff=True
        )
    else:
        return measure_placement
