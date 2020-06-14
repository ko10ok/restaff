from pprint import pprint

import svgwrite
from svgwrite.shapes import Polyline, Circle
from svgwrite.text import Text

from src.helpers import markup_title, staff_line, part_staff_positions, position_part_staff, \
    title_place_heigh, staves_position_marker, read_music_xml, get_staffs_count, place_next_measure, render, \
    markup_measure, markup_measure_octave, notes_times, \
    get_note_sign, markup_note, calc_measure_length, fit_measure_length_in_page, correct_measure, get_rest_sign, \
    markup_measure_time, get_parted_measures, get_note_position, analyze_octaves, analyze_times, debug_point, \
    analyze_chords
from src.types import ScoreSheet, StaffProperties, PageProperties, Point, MeasurePosition, MeasureProperties

## reads
music_xml_sheet = read_music_xml('examples/musicxml/His Theme chords at 25.musicxml')
pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)
pprint(sheet)

page_prop = PageProperties(width=2977.2, height=4208.4)

## setup
measure_prop = MeasureProperties(
    octave_left_offset=50,
    time_left_offset=50,
    left_offset=100,
    right_offset=50,
)

staff_prop = StaffProperties(
    left_offset=194.232,
    right_offset=2977.2 - 2835.47,
    top_offset=366.733,
    bottom_offset=50,
    staff_line_offset=25,
    staff_line_count=7,
    staff_offset=80,
    staff_count=get_staffs_count(sheet),
    parts_offset=140,
    measure_offsets=measure_prop,
)

default_octave = 5


## marking up
def markup_score_sheet(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    objects = []

    objects += markup_title(page_prop, staff_prop, sheet)

    total_measures_count = max([len(part.measures) for part in sheet.parts])

    staves_position = Point(staff_prop.left_offset, staff_prop.top_offset)
    parted_measure_octaves = analyze_octaves(sheet.parts)
    parted_measure_times = analyze_times(sheet.parts)
    print(f'{parted_measure_octaves=}')
    print(f'{parted_measure_times=}')
    staff_marker_source = staves_position_marker(page_prop, staff_prop, title_place_heigh(page_prop, staff_prop))

    measure_placement = MeasurePosition(0, staff_prop.left_offset, first_on_staff=False, last_on_staff=True)

    for measure_index in range(total_measures_count):
        print(f'--------------- {measure_index+1=} -----------------')

        last_measure_placement = measure_placement
        if last_measure_placement.last_on_staff:

            # setup initial measure placement
            last_measure_placement = MeasurePosition(
                0, staff_prop.left_offset,
                first_on_staff=last_measure_placement.first_on_staff,
                last_on_staff=True
            )

            # get new staff
            try:
                staves_position = next(staff_marker_source)
            except:
                # flush page
                yield objects
                objects = []

                # reinitialize page staffs marker
                staff_marker_source = staves_position_marker(page_prop, staff_prop, staff_prop.top_offset)
                staves_position = next(staff_marker_source)

            # TODO recalc staffs offsets considering min|max note offset
            #  for preventing different staff's notes intersection
            parts_staff_offsets = part_staff_positions(staff_prop, staves_position, sheet)
            for position in parts_staff_offsets.values():
                objects += staff_line(page_prop, staff_prop, position)

        parted_measures = get_parted_measures(sheet.parts, measure_index)

        measure_octave_changed = any([
            staff.is_changed for staff in parted_measure_octaves[measure_index + 1].values()
        ])
        measure_time_changed = any([
            staff.is_changed for staff in parted_measure_times[measure_index + 1].values()
        ])
        measure_length = calc_measure_length(page_prop, staff_prop, parted_measures.values(), measure_octave_changed,
                                             measure_time_changed, last_measure_placement)

        print(f'{measure_index} {measure_length}')

        # if current first measure wider then staff length
        if last_measure_placement.last_on_staff:
            measure_length = fit_measure_length_in_page(page_prop, staff_prop, measure_length,
                                                        last_measure_placement.end)

        measure_placement = place_next_measure(page_prop, staff_prop, last_measure_placement, measure_length)

        if measure_index + 1 < total_measures_count:
            parted_next_measures = get_parted_measures(sheet.parts, measure_index + 1)
            next_measure_octave_changed = any([
                staff.is_changed for staff in parted_measure_octaves[measure_index + 1].values()
            ])
            next_measure_time_changed = any([
                staff.is_changed for staff in parted_measure_times[measure_index + 1].values()
            ])

            next_measure_length = calc_measure_length(
                page_prop, staff_prop, parted_next_measures.values(), next_measure_octave_changed,
                next_measure_time_changed, first_on_staff=False
            )
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, next_measure_length)
        else:
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, page_prop.width)

        objects += markup_measure(staff_prop, staves_position, measure_index + 1, measure_placement)

        def measure_offset_point(measure_placement, staves_position):
            return Point(measure_placement.start, staves_position.y)

        measure_point = measure_offset_point(measure_placement, staves_position)

        measure_left_offset = staff_prop.measure_offsets.left_offset
        measure_right_offset = staff_prop.measure_offsets.right_offset

        measure_octave_draws = measure_octave_changed or measure_placement.first_on_staff
        measure_time_draws = measure_time_changed or measure_placement.first_on_staff
        measure_length = measure_placement.end - measure_placement.start - measure_left_offset - measure_right_offset

        # same values for all parts
        octave_left_offset = 0
        time_left_offset = 0

        for part in sheet.parts:
            guessed_staff_octave, octave_changed = parted_measure_octaves[measure_index + 1][part.info.id]

            measure_time, time_changed = parted_measure_times[measure_index + 1][part.info.id]

            for staff in range(1, part.staff_count + 1):
                staff_measure_position = position_part_staff(staff_prop, measure_point, sheet, part.info.id, staff)

                if time_changed or measure_placement.first_on_staff:
                    objects += markup_measure_time(staff_prop, measure_time, staff_measure_position)

                if octave_changed or measure_placement.first_on_staff:
                    octave_text = f'{guessed_staff_octave[staff] or default_octave}'
                    objects += markup_measure_octave(staff_prop, octave_text, staff_measure_position)

            if measure_octave_draws:
                octave_left_offset = staff_prop.measure_offsets.octave_left_offset
            if measure_time_draws:
                time_left_offset = staff_prop.measure_offsets.time_left_offset

            note_offset = {
                part_staff: measure_point.x + measure_left_offset + octave_left_offset + time_left_offset
                for part_staff in range(1, part.staff_count + 1)
            }

            # proportional placement sucks in 32nd+ notes, possible solution is consider
            # note type (length) of minimal

            # TODO chords must be drawn separately with minimal note step length

            chord_cord_minimal_len = 0

            chord_stepout = False

            chord_followed_notes = analyze_chords(parted_measures[part.info.id].notes)
            print(f'{chord_followed_notes=}')

            for note in parted_measures[part.info.id].notes:

                part_position = position_part_staff(staff_prop, staves_position, sheet, part.info.id, note.staff)
                staff_octave = guessed_staff_octave[note.staff] or default_octave

                not_chord_note = not note.chord and note not in chord_followed_notes
                chord_note = note.chord or note in chord_followed_notes
                last_chord_note = note.chord and note not in chord_followed_notes
                first_chord_note = not note.chord and note in chord_followed_notes

                chord_offset = (37 if chord_note else 0)
                horizontal_note_position = note_offset[note.staff]
                # print(f'{chord_offset=} {chord_stepout=} {note_offset[note.staff]=} {horizontal_note_position=}')

                print(f'{note=}')
                if not note.rest:
                    vertical_note_position = part_position.y + get_note_position(staff_prop, staff_octave, note.pitch)
                    note_sign = get_note_sign(note)
                    objects += [markup_note(note_sign,
                                            Point(horizontal_note_position + (chord_offset if chord_stepout else 0),
                                                  vertical_note_position))]
                    if note.dot:
                        objects += [
                            Circle(
                                center=(
                                    horizontal_note_position + 35 + chord_offset,
                                    vertical_note_position - staff_prop.staff_line_offset // 2
                                ),
                                r=4)
                        ]

                    if note.time_modification:
                        objects += [Text(
                            str(note.time_modification['actual-notes']),
                            insert=(
                            horizontal_note_position, part_position.y - staff_prop.staff_offset // 2),
                            fill="rgb(110,110,110)",
                            style="font-size:15px; font-family:Arial",
                        )]

                    objects += []
                    flag = {
                        'whole': (0, 0),
                        'half': (1, 0),
                        'quarter': (1, 0),
                        'eighth': (1, 1),
                        '16th': (1, 2),
                        '32nd': (1, 3),
                    }
                    stem, beams = flag[note.type]
                    if stem:
                        half_note_offset = 17.5
                        stem_lenght = 80
                        objects += [
                            Polyline(
                                points=[(horizontal_note_position + half_note_offset, vertical_note_position),
                                        (horizontal_note_position + half_note_offset,
                                         vertical_note_position - stem_lenght)]
                            ).stroke(
                                color=svgwrite.rgb(0, 0, 0),
                                width=3,
                                linejoin='bevel',
                            )
                        ]

                        print(f'{not_chord_note=} {last_chord_note=} {first_chord_note=}')
                        if not_chord_note or last_chord_note:
                            for idx in range(beams):
                                half_note_offset = 17.5
                                beam_length = 13
                                beam_offset = idx * 15
                                objects += [debug_point(Point(horizontal_note_position + half_note_offset,
                                                              vertical_note_position - stem_lenght + beam_offset + 10 * idx))]
                                objects += [
                                    Polyline(
                                        points=[(horizontal_note_position + half_note_offset,
                                                 vertical_note_position - stem_lenght + beam_offset + 10),
                                                (horizontal_note_position + half_note_offset + beam_length,
                                                 vertical_note_position - stem_lenght + beam_offset + 10 + 30)]
                                    ).stroke(
                                        color=svgwrite.rgb(0, 0, 0),
                                        width=3,
                                        linejoin='bevel',
                                    )
                                ]

                else:
                    vertical_rest_position = part_position.y + staff_prop.staff_height // 2
                    note_sign = get_rest_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_rest_position))]

                note_lenght = (measure_length - octave_left_offset - time_left_offset) \
                              / notes_times[note.type] if note.type else notes_times['whole']

                if note.dot:
                    note_lenght += note_lenght / 2

                if note.time_modification:
                    print(f'{note.time_modification=}')
                    actual = note.time_modification['actual-notes']
                    normal = note.time_modification['normal-notes']
                    note_lenght_multiplier = int(normal) / int(actual)
                    print(f'{note.time_modification} {note_lenght_multiplier}')
                    note_lenght = note_lenght * note_lenght_multiplier

                if first_chord_note:
                    chord_cord_minimal_len = note_lenght

                if chord_note:
                    chord_stepout = not chord_stepout

                if not_chord_note:
                    note_offset[note.staff] += note_lenght
                    chord_stepout = False

                if last_chord_note:
                    note_offset[note.staff] += chord_cord_minimal_len
                    chord_stepout = False

                # print(f'{note_offset=}')
                # print(f'{note_delta_offset=}')

    # [~] markup measures:
    #  [x] start stops
    #  [x] octave sign (number)
    #  [~] notes
    #  [~] beams
    #  [~] stems
    #  [~] dots
    #  [~] chords
    #  [~] tuplets
    # [ ] markup cross measures ligas and signs
    #  ~  - needs refactoring or partial solution
    yield objects


markup = markup_score_sheet(page_prop, staff_prop, sheet)

file_path = 'exhaust/music_xml_out_{page_number}.svg'
for page_idx, page_markup in enumerate(markup_score_sheet(page_prop, staff_prop, sheet)):
    render(page_prop, page_markup, file_path, page_idx)
