from typing import List

from src.helpers import analyze_octave_drawing, analyze_time_drawing, get_parted_measures, calc_measure_length, \
    fit_measure_length_in_page, place_next_measure, correct_measure
from src.types import PageProperties, StaffProperties, Part, MeasurePlacement, MeasureDrawing


def place_staffs_measures(page_prop: PageProperties,
                          staff_prop: StaffProperties,
                          parts: List[Part],
                          start_measure_idx,
                          staff_octave_draws,
                          staff_time_draws) -> List[MeasureDrawing]:
    measures = []

    measure_placement = MeasurePlacement(0, staff_prop.left_offset, first_on_staff=False, last_on_staff=True)

    total_measures_count = max([len(part.measures) for part in parts])
    for measure_index in range(start_measure_idx, total_measures_count):
        print(f'--------------- {measure_index+1=} -----------------')

        last_measure_placement = measure_placement
        first_on_staff = last_measure_placement.last_on_staff
        last_measure = measure_index + 1 >= total_measures_count

        measure_octave_offset_draws = analyze_octave_drawing(staff_octave_draws, measure_index, first_on_staff)
        measure_time_offset_draws = analyze_time_drawing(staff_time_draws, measure_index, first_on_staff)

        parted_measures = get_parted_measures(parts, measure_index)
        measure_length = calc_measure_length(page_prop, staff_prop, parted_measures.values(),
                                             measure_octave_offset_draws,
                                             measure_time_offset_draws, last_measure_placement.end)

        # if current first measure wider then staff length
        if last_measure_placement.last_on_staff:
            measure_length = fit_measure_length_in_page(page_prop, staff_prop, measure_length,
                                                        last_measure_placement.end)

        measure_placement = place_next_measure(page_prop, staff_prop, last_measure_placement, measure_length)

        if not last_measure:
            parted_next_measures = get_parted_measures(parts, measure_index + 1)
            next_measure_octave_offset_draws = analyze_octave_drawing(staff_octave_draws, measure_index + 1,
                                                                      first_on_staff=False)
            next_measure_time_offset_draws = analyze_time_drawing(staff_time_draws, measure_index + 1,
                                                                  first_on_staff=False)

            next_measure_length = calc_measure_length(
                page_prop, staff_prop, parted_next_measures.values(), next_measure_octave_offset_draws,
                next_measure_time_offset_draws, first_on_staff=False
            )
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, next_measure_length)
        else:
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, page_prop.width)

        measure_left_offset = staff_prop.measure_offsets.left_offset

        if measure_octave_offset_draws or measure_time_offset_draws:
            measure_left_offset += staff_prop.measure_offsets.octave_left_offset
            measure_left_offset += staff_prop.measure_offsets.time_left_offset

        measure_right_offset = staff_prop.measure_offsets.right_offset

        measures += [
            MeasureDrawing(
                measure_placement.start,
                measure_placement.end,
                measure_left_offset,
                measure_right_offset,
                measure_octave_offset_draws,
                measure_time_offset_draws,
                first_on_staff=measure_placement.first_on_staff,
                last_on_staff=measure_placement.last_on_staff,
            )
        ]

        if measure_placement.last_on_staff:
            return measures


def part_staffs_positions(staff_prop: StaffProperties, part, part_start_position, parted_staffs_placement):
    part_staffs_positions = {}
    part_vertiacal_position = part_start_position
    for staff in range(1, part.staff_count + 1):
        part_vertiacal_position += parted_staffs_placement[(part.info.id, staff)].top_offset

        part_staffs_positions[staff] = part_vertiacal_position
        part_vertiacal_position += parted_staffs_placement[(part.info.id, staff)].heigth + \
                                   parted_staffs_placement[(part.info.id, staff)].bottom_offset
        part_vertiacal_position += staff_prop.staff_offset
    return part_staffs_positions


def part_height(staff_prop: StaffProperties, part, parted_staffs_placement):
    part_offset = 0
    for staff in range(1, part.staff_count + 1):
        part_offset += parted_staffs_placement[(part.info.id, staff)].top_offset + \
                       parted_staffs_placement[(part.info.id, staff)].heigth + \
                       parted_staffs_placement[(part.info.id, staff)].bottom_offset
    part_offset += staff_prop.staff_offset * (part.staff_count - 1)
    return part_offset
