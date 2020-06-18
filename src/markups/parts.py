from collections import namedtuple
from typing import List

from src.helpers import get_note_position
from src.types import StaffProperties, Part


def analyze_parts_height(staff_prop: StaffProperties,
                         parts: List[Part],
                         staff_octave_draws,
                         current_measure_idx,
                         measures_count):
    top_offset = {}
    bottom_offset = {}
    for part in parts:
        for staff in range(1, part.staff_count + 1):
            top_offset[(part.info.id, staff)] = 0
            bottom_offset[(part.info.id, staff)] = 0
            for measure_idx, measure in enumerate(
                    part.measures[current_measure_idx:current_measure_idx + measures_count]):
                for note in measure.notes:
                    if note.staff == staff:
                        if not note.rest:
                            offset = 0
                            top_offset[(part.info.id, staff)] = max(
                                top_offset.get((part.info.id, staff), 0),
                                - get_note_position(staff_prop, staff_octave_draws[
                                    (current_measure_idx + measure_idx, part.info.id, staff)].octave, note.pitch)
                            )
                            bottom_offset[(part.info.id, staff)] = max(
                                bottom_offset.get((part.info.id, staff), 0),
                                get_note_position(staff_prop, staff_octave_draws[
                                    (current_measure_idx + measure_idx, part.info.id, staff)].octave,
                                                  note.pitch) - staff_prop.staff_height,
                            )
    StaffPlacement = namedtuple('StaffPlacement', ['top_offset', 'heigth', 'bottom_offset', 'total_height'])

    return {
        (part.info.id, staff): StaffPlacement(top_offset[(part.info.id, staff)], staff_prop.staff_height,
                                              bottom_offset[(part.info.id, staff)],
                                              top_offset[(part.info.id, staff)] + staff_prop.staff_height +
                                              bottom_offset[(part.info.id, staff)])
        for part in parts
        for staff in range(1, part.staff_count + 1)
    }
