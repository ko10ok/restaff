from collections import namedtuple
from pprint import pprint
from typing import List

import svgwrite
from svgwrite.shapes import Polyline, Circle
from svgwrite.text import Text

from src.helpers import markup_title, staff_line, title_place_heigh, read_music_xml, \
    get_staffs_count, place_next_measure, render, \
    markup_measure, markup_measure_octave, notes_times, \
    get_note_sign, calc_measure_length, fit_measure_length_in_page, correct_measure, get_rest_sign, \
    markup_measure_time, get_parted_measures, get_note_position, analyze_octaves, analyze_times, analyze_chords, \
    analyze_parts_staffs_octaves, flat_measured_parted_staff, analyze_parts_staffs_times, analyze_octave_drawing, \
    analyze_time_drawing, markup_note_body
from src.types import ScoreSheet, StaffProperties, PageProperties, Point, MeasureProperties, Part, \
    MeasurePlacement

MeasureDrawing = namedtuple('MeasureDrawing',
                            ['start', 'end', 'left_offset', 'right_offset', 'octave_draws', 'time_draws',
                             'first_on_staff',
                             'last_on_staff'])


def analyze_parts_height(staff_prop: StaffProperties, parts: List[Part], staff_octave_draws, current_measure_idx,
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
                            top_offset[(part.info.id, staff)] = min(
                                top_offset.get((part.info.id, staff), 0),
                                get_note_position(staff_prop, staff_octave_draws[
                                    (current_measure_idx + measure_idx, part.info.id, staff)].octave, note.pitch)
                            )
                            bottom_offset[(part.info.id, staff)] = max(
                                top_offset.get((part.info.id, staff), 0),
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
            parted_next_measures = get_parted_measures(sheet.parts, measure_index + 1)
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


def part_staffs_positions(part, part_start_position, parted_staffs_placement):
    part_staffs_positions = {}
    part_vertiacal_position = part_start_position
    for staff in range(1, part.staff_count + 1):
        part_vertiacal_position += parted_staffs_placement[(part.info.id, staff)].top_offset

        part_staffs_positions[staff] = part_vertiacal_position
        part_vertiacal_position += parted_staffs_placement[(part.info.id, staff)].heigth + \
                                   parted_staffs_placement[(part.info.id, staff)].bottom_offset
        part_vertiacal_position += staff_prop.staff_offset
    return part_staffs_positions


def part_height(part, parted_staffs_placement):
    part_offset = 0
    for staff in range(1, part.staff_count + 1):
        part_offset += parted_staffs_placement[(part.info.id, staff)].top_offset + \
                       parted_staffs_placement[(part.info.id, staff)].heigth + \
                       parted_staffs_placement[(part.info.id, staff)].bottom_offset
    part_offset += staff_prop.staff_offset * (part.staff_count - 1)
    return part_offset


def markup_part(staff_positions):
    objects = []
    for staff, position in staff_positions.items():
        staves_position = Point(staff_prop.left_offset, position)
        objects += staff_line(page_prop, staff_prop, staves_position)
    return objects


def markup_note(staff_prop: StaffProperties, staff_start_position, staff_octave, horizontal_note_position, chord_offset,
                chord_stepout, note, chord_followed_notes):
    not_chord_note = not note.chord and note not in chord_followed_notes
    chord_note = note.chord or note in chord_followed_notes
    last_chord_note = note.chord and note not in chord_followed_notes
    first_chord_note = not note.chord and note in chord_followed_notes

    objects = []

    note_offset = get_note_position(staff_prop, staff_octave, note.pitch)

    vertical_note_position = staff_start_position + note_offset

    note_sign = get_note_sign(note)
    objects += [markup_note_body(
        note_sign,
        Point(
            horizontal_note_position + (chord_offset if chord_stepout else 0),
            vertical_note_position
        )
    )]

    if note.dot:
        addition = note_offset % staff_prop.staff_line_offset - staff_prop.staff_line_offset / 2
        objects += [
            Circle(
                center=(
                    horizontal_note_position + 35 + chord_offset,
                    vertical_note_position + addition
                ),
                r=4)
        ]

    if note.time_modification:
        objects += [Text(
            str(note.time_modification['actual-notes']),
            insert=(
                horizontal_note_position,
                staff_start_position - staff_prop.staff_offset // 2),
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

        # TODO extract beam|stemm drawing into note groups drawing
        print(f'{not_chord_note=} {last_chord_note=} {first_chord_note=}')
        if not_chord_note or last_chord_note:
            for idx in range(beams):
                half_note_offset = 17.5
                beam_length = 13
                beam_offset = idx * 15
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

    return objects


def calc_note_length(measure, time, note):
    note_lenght = (measure.end - measure.start - measure.left_offset - measure.right_offset) \
                  / (notes_times[note.type] if note.type else notes_times['whole'])

    note_lenght *= (time.beat_type / time.beats)

    if note.dot:
        note_lenght += note_lenght / 2

    if note.time_modification:
        print(f'{note.time_modification=}')
        actual = note.time_modification['actual-notes']
        normal = note.time_modification['normal-notes']
        note_lenght_multiplier = int(normal) / int(actual)
        print(f'{note.time_modification} {note_lenght_multiplier}')
        note_lenght = note_lenght * note_lenght_multiplier

    return note_lenght


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

            staff_positions = part_staffs_positions(part, part_vertical_position, parted_staffs_placement)
            print(f'{staff_positions}')
            objects += markup_part(staff_positions)

            for idx, measure in enumerate(drawable_staff_measures):

                measure_idx = current_measure_idx + idx

                parted_measures = get_parted_measures(sheet.parts, measure_idx)

                position = Point(staff_prop.left_offset, part_vertical_position)
                measure_height = part_height(part, parted_staffs_placement)

                objects += markup_measure(staff_prop, position, measure_height, measure_idx, measure)

                for staff in range(1, part.staff_count + 1):
                    staff_measure_position = Point(measure.start, staff_positions[staff])

                    if staff_time_draws[(measure_idx, part.info.id, staff)].draws or measure.first_on_staff:
                        time = staff_time_draws[(measure_idx, part.info.id, staff)].time
                        objects += markup_measure_time(staff_prop, time, staff_measure_position)

                    if staff_octave_draws[(measure_idx, part.info.id, staff)].draws or measure.first_on_staff:
                        octave_text = str(
                            staff_octave_draws[(measure_idx, part.info.id, staff)].octave or default_octave)
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

                chord_followed_notes = analyze_chords(parted_measures[part.info.id].notes)
                print(f'{chord_followed_notes=}')
                for note in parted_measures[part.info.id].notes:
                    staff_octave = staff_octave_draws[(measure_idx, part.info.id, note.staff)].octave

                    not_chord_note = not note.chord and note not in chord_followed_notes
                    chord_note = note.chord or note in chord_followed_notes
                    last_chord_note = note.chord and note not in chord_followed_notes
                    first_chord_note = not note.chord and note in chord_followed_notes

                    chord_offset = (37 if chord_note else 0)
                    horizontal_note_position = note_offset[note.staff]
                    # print(f'{chord_offset=} {chord_stepout=} {note_offset[note.staff]=} {horizontal_note_position=}')

                    staff_start_position = staff_positions[note.staff]

                    print(f'{note=}')
                    if not note.rest:
                        objects += markup_note(
                            staff_prop=staff_prop,
                            staff_start_position=staff_start_position,
                            staff_octave=staff_octave,
                            horizontal_note_position=horizontal_note_position,
                            chord_offset=chord_offset,
                            chord_stepout=chord_stepout,
                            note=note,
                            chord_followed_notes=chord_followed_notes
                        )
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

                    if chord_note:
                        chord_stepout = not chord_stepout

                    if not_chord_note:
                        note_offset[note.staff] += note_lenght
                        chord_stepout = False

                    if last_chord_note:
                        note_offset[note.staff] += chord_cord_minimal_len
                        chord_stepout = False

            part_vertical_position += part_height(part, parted_staffs_placement) + staff_prop.staff_offset

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

markup = markup_score_sheet(page_prop, staff_prop, sheet)

file_path = 'exhaust/music_xml_out_{page_number}.svg'
for page_idx, page_markup in enumerate(markup_score_sheet(page_prop, staff_prop, sheet)):
    render(page_prop, page_markup, file_path, page_idx)
