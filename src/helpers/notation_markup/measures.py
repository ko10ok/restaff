from itertools import groupby
from typing import List

from src.types import Measure, StaffProperties, PageProperties, MeasurePosition, MeasurePlacement


# TODO reorganize measure guess
def calc_measure_length(page_prop: PageProperties, staff_prop: StaffProperties, measures: List[Measure],
                        measure_octave_draws, measure_time_draws,
                        first_on_staff):
    octave_left_offset = (
        staff_prop.measure_offsets.octave_left_offset if (first_on_staff or measure_octave_draws) else 0)
    time_left_offset = (staff_prop.measure_offsets.time_left_offset if (first_on_staff or measure_time_draws) else 0)
    measure_left_offset = staff_prop.measure_offsets.left_offset
    measure_right_offset = staff_prop.measure_offsets.right_offset

    comfort_notesize = {
        'whole': 20,
        'half': 40,
        'quarter': 70,
        'eighth': 110,
        '16th': 150,
        '32nd': 220,
        '64nd': 330
    }

    measure_staff_grouped_notes = [groupby(measure.notes, lambda x: x.staff) for measure in measures]
    measure_notes_type = [
        [[{note.type: comfort_notesize.get(note.type, comfort_notesize['whole'])} for note in notes if not note.chord]
         for staff, notes in staff_grouped_notes]
        for staff_grouped_notes in measure_staff_grouped_notes
    ]
    print(f'{measure_notes_type=}')

    max_measure_notes_length = max([
        max([sum([sum([length for type, length in note.items()]) for note in staff]) for staff in parts])
        for parts in measure_notes_type
    ])
    measure_length = max_measure_notes_length + octave_left_offset + time_left_offset + measure_left_offset + measure_right_offset

    staff_length = page_prop.width - staff_prop.right_offset - staff_prop.left_offset
    minimal_accepted_measure_length = staff_length // 8
    print(f'{measure_length=} {minimal_accepted_measure_length=}')

    return max(measure_length, minimal_accepted_measure_length)


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

    return MeasurePlacement(
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
            first_on_staff=measure_placement.first_on_staff,
            last_on_staff=True
        )
    else:
        return measure_placement
