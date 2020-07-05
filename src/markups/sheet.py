from collections import namedtuple

from src.helpers import calc_note_length, markup_note_body, get_rest_sign, markup_note, markup_measure_octave, \
    markup_measure_time, markup_measure, get_parted_measures, markup_part, title_place_heigh, \
    flat_measured_parted_staff, analyze_parts_staffs_times, analyze_parts_staffs_octaves, analyze_times, \
    analyze_octaves, markup_title, analyze_chord_followed_notes, get_note_position, markup_extra_staffs
from src.markups.chords import markup_chords
from src.markups.parts import analyze_parts_height
from src.markups.staffs import part_height, part_staffs_positions, place_staffs_measures
from src.types import Point, PageProperties, StaffProperties, ScoreSheet


def markup_score_sheet(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    objects = []

    objects += markup_title(page_prop, staff_prop, sheet)

    total_measures_count = max([len(part.measures) for part in sheet.parts])

    staves_position = Point(staff_prop.left_offset, staff_prop.top_offset)
    parted_measure_octaves = analyze_octaves(sheet.parts)
    parted_measure_times = analyze_times(sheet.parts)
    print(f'{parted_measure_octaves=}')
    print(f'{parted_measure_times=}')

    parted_measure_octaves = analyze_parts_staffs_octaves(sheet.parts)
    measures_octaves_changes = flat_measured_parted_staff(parted_measure_octaves)
    OctaveDraws = namedtuple('OctaveDraws', ['octave', 'draws'])
    staff_octave_draws = {
        k: OctaveDraws(octave_changes.octave, octave_changes.is_changed)
        for k, octave_changes in measures_octaves_changes.items()
    }

    parted_measure_times = analyze_parts_staffs_times(sheet.parts)
    measures_times_changes = flat_measured_parted_staff(parted_measure_times)
    TimeDraws = namedtuple('TimeDraws', ['time', 'draws'])
    staff_time_draws = {
        k: TimeDraws(time_changes.time, time_changes.is_changed)
        for k, time_changes in measures_times_changes.items()
    }
    print(f'{staff_octave_draws=}')
    print(f'{staff_time_draws=}')

    current_measure_idx = 0
    first_staff = True
    staves_vertical_position = 0

    # TODO not eq -> lt
    while current_measure_idx != total_measures_count:
        drawable_staff_measures = place_staffs_measures(page_prop, staff_prop, sheet.parts,
                                                        current_measure_idx, staff_octave_draws, staff_time_draws)
        print(f'{drawable_staff_measures=}')

        if first_staff:
            staves_vertical_position += title_place_heigh(page_prop, staff_prop)

        parted_staffs_placement = analyze_parts_height(staff_prop, sheet.parts, staff_octave_draws, current_measure_idx,
                                                       len(drawable_staff_measures))
        print(f'{parted_staffs_placement=}')

        staves_height = sum([staff_placement.total_height for staff_placement in
                             parted_staffs_placement.values()]) + staff_prop.staff_offset * (
                                len(parted_staffs_placement) - 1)

        print(f'{staves_vertical_position=} {staves_height=} {page_prop.height - staff_prop.bottom_offset=}')

        if staves_vertical_position + staves_height >= page_prop.height - staff_prop.bottom_offset:
            yield objects
            objects = []
            staves_vertical_position = staff_prop.top_offset
            print('===============  next page =======================')

        part_vertical_position = staves_vertical_position
        for part in sheet.parts:

            staff_positions = part_staffs_positions(staff_prop, part, part_vertical_position, parted_staffs_placement)
            print(f'{current_measure_idx=} {part.info.id=} {staff_positions=}')

            objects += markup_part(page_prop, staff_prop, staff_positions)

            for idx, measure in enumerate(drawable_staff_measures):

                measure_idx = current_measure_idx + idx
                print(f'{measure_idx=}')

                parted_measures = get_parted_measures(sheet.parts, measure_idx)

                position = Point(staff_prop.left_offset, part_vertical_position)
                measure_height = part_height(staff_prop, part, parted_staffs_placement)

                objects += markup_measure(staff_prop, position, measure_height, measure_idx + 1, measure)

                for staff in range(1, part.staff_count + 1):
                    staff_measure_position = Point(measure.start, staff_positions[staff])

                    if staff_time_draws[(measure_idx, part.info.id, staff)].draws or measure.first_on_staff:
                        time = staff_time_draws[(measure_idx, part.info.id, staff)].time
                        objects += markup_measure_time(staff_prop, time, staff_measure_position)

                    if staff_octave_draws[(measure_idx, part.info.id, staff)].draws or measure.first_on_staff:
                        octave_text = str(staff_octave_draws[(measure_idx, part.info.id, staff)].octave)
                        objects += markup_measure_octave(staff_prop, octave_text, staff_measure_position)

                note_offset = {
                    part_staff: measure.start + measure.left_offset
                    for part_staff in range(1, part.staff_count + 1)
                }

                # proportional placement sucks in 32nd+ notes, possible solution is consider
                # note type (length) of minimal

                # TODO chords must be drawn separately with minimal note step length

                chord_cord_minimal_len = 0

                chord_stepout = False

                chord_followed_notes = analyze_chord_followed_notes(parted_measures[part.info.id].notes)
                chords_notes = markup_chords(parted_measures[part.info.id].notes)

                for note in parted_measures[part.info.id].notes:
                    staff_octave = staff_octave_draws[(measure_idx, part.info.id, note.staff)].octave

                    not_chord_note = not note.chord and note not in chord_followed_notes
                    chord_note = note.chord or note in chord_followed_notes
                    last_chord_note = note.chord and note not in chord_followed_notes
                    first_chord_note = not note.chord and note in chord_followed_notes
                    chord_stepout = chord_note and chords_notes.get(note.id, {}).offset

                    chord_offset = (37 if chord_stepout else 0)
                    print(f'{chord_note=} {chord_offset=} {last_chord_note=} {chord_stepout=}')
                    horizontal_note_position = note_offset[note.staff]
                    # print(f'{chord_offset=} {chord_stepout=} {note_offset[note.staff]=} {horizontal_note_position=}')

                    staff_start_position = staff_positions[note.staff]

                    # TODO draw stems beams on group drawing
                    # TODO fix chord stems should be at top of chord
                    print(f'{note=}')
                    if not note.rest:
                        objects += markup_note(
                            staff_prop=staff_prop,
                            staff_start_position=staff_start_position,
                            staff_octave=staff_octave,
                            horizontal_note_position=horizontal_note_position,
                            chord_offset=chord_offset,
                            note=note,
                            chords_notes=chords_notes
                        )

                        note_vertical_offset = get_note_position(staff_prop, staff_octave, note.pitch)
                        objects += markup_extra_staffs(staff_prop, staff_start_position, horizontal_note_position,
                                                       note_vertical_offset)

                    else:
                        vertical_rest_position = staff_start_position + staff_prop.staff_height // 2
                        note_sign = get_rest_sign(note)
                        objects += [
                            markup_note_body(note_sign, Point(horizontal_note_position, vertical_rest_position))
                        ]

                    time = parted_measures[part.info.id].time
                    note_lenght = calc_note_length(measure, time, note)

                    if first_chord_note:
                        chord_cord_minimal_len = note_lenght

                    if not_chord_note:
                        note_offset[note.staff] += note_lenght
                        chord_stepout = False

                    if last_chord_note:
                        note_offset[note.staff] += chord_cord_minimal_len

            part_vertical_position += part_height(staff_prop, part, parted_staffs_placement) + staff_prop.staff_offset

        staves_vertical_position += staves_height + staff_prop.parts_offset
        first_staff = False
        current_measure_idx += len(drawable_staff_measures)

    # [~] markup measures:
    #  [x] start stops
    #  [x] octave sign (number)
    #  [x] notes
    #  [~] beams
    #  [~] stems
    #  [x] dots
    #  [~] chords
    #  [~] tuplets
    # [ ] markup cross measures ligas and signs
    #  ~  - needs refactoring or partial solution
    yield objects
