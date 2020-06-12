from pprint import pprint

from src.helpers import markup_title, staff_line, part_staff_positions, guess_measure_octave, position_part_staff, \
    title_place_heigh, staves_position_marker, read_music_xml, get_staffs_count, place_next_measure, render, \
    markup_measure, markup_measure_octave, notes_times, \
    get_note_sign, markup_note, calc_measure_length, fit_measure_length_in_page, correct_measure, get_rest_sign, \
    markup_measure_time, get_parted_measures, get_note_position
from src.types import ScoreSheet, StaffProperties, PageProperties, Point, MeasurePosition

## reads
music_xml_sheet = read_music_xml('examples/musicxml/His Theme chords at 25.musicxml')
pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)
pprint(sheet)

page_prop = PageProperties(width=2977.2, height=4208.4)

## setup
staff_prop = StaffProperties(
    left_offset=194.232,
    right_offset=2977.2 - 2835.47,
    top_offset=366.733,
    bottom_offset=50,
    staff_line_offset=25,
    staff_line_count=7,
    staff_offset=80,
    staff_count=get_staffs_count(sheet),
    parts_offset=140
)

default_octave = 5


## marking up
def markup_score_sheet(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    objects = []

    # mark up title, author
    objects += markup_title(page_prop, staff_prop, sheet)

    total_measures_count = max([len(part.measures) for part in sheet.parts])

    staves_position = Point(staff_prop.left_offset, staff_prop.top_offset)
    parted_measure_octaves = {}
    parted_measure_times = {}

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

            parts_staff_offsets = part_staff_positions(staff_prop, staves_position, sheet)
            for position in parts_staff_offsets.values():
                objects += staff_line(page_prop, staff_prop, position)

        parted_measures = get_parted_measures(sheet.parts, measure_index)
        measure_length = calc_measure_length(page_prop, staff_prop, parted_measures.values())

        # if current first measure wider then staff length
        if last_measure_placement.last_on_staff:
            measure_length = fit_measure_length_in_page(page_prop, staff_prop, measure_length,
                                                        last_measure_placement.end)

        measure_placement = place_next_measure(page_prop, staff_prop, last_measure_placement, measure_length)

        if measure_index + 1 < total_measures_count:
            parted_next_measures = get_parted_measures(sheet.parts, measure_index + 1)
            next_measure_length = calc_measure_length(
                page_prop, staff_prop, measures=parted_next_measures.values()
            )
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, next_measure_length)
        else:
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, page_prop.width)

        objects += markup_measure(staff_prop, staves_position, measure_index + 1, measure_placement)

        def measure_offset_point(measure_placement, staves_position):
            return Point(measure_placement.start, staves_position.y)

        measure_point = measure_offset_point(measure_placement, staves_position)

        measure_left_offset = 100
        measure_right_offset = 50
        measure_length = measure_placement.end - measure_placement.start - measure_left_offset - measure_right_offset

        # same values for all parts
        # TODO fix minor case with first parts non changing octave smaller offset. shifts all notes on such staff
        octave_left_offset = 0
        time_left_offset = 0

        for part in sheet.parts:
            guessed_staff_octave = guess_measure_octave(parted_measures[part.info.id])
            octave_changed = (parted_measure_octaves.get(part.info.id) != guessed_staff_octave) or \
                             measure_placement.first_on_staff
            parted_measure_octaves[part.info.id] = guessed_staff_octave

            measure_time = parted_measures[part.info.id].time
            time_changed = (parted_measure_times.get(part.info.id) != measure_time) or measure_placement.first_on_staff
            parted_measure_times[part.info.id] = measure_time

            for staff in range(1, part.staff_count + 1):
                staff_measure_position = position_part_staff(staff_prop, measure_point, sheet, part.info.id, staff)

                if time_changed:
                    objects += markup_measure_time(staff_prop, measure_time, staff_measure_position)

                if octave_changed:
                    octave_text = f'{guessed_staff_octave[staff] or default_octave}'
                    objects += markup_measure_octave(staff_prop, octave_text, staff_measure_position)

            if octave_changed:
                octave_left_offset = 50
            if time_changed:
                time_left_offset = 50

            note_offset = {
                part_staff: measure_point.x + measure_left_offset + octave_left_offset + time_left_offset
                for part_staff in range(1, part.staff_count + 1)
            }

            # proportional placement sucks in 32nd+ notes, possible solution is consider
            # note type (length) of minimal

            # TODO chords must be drawn separately with minimal note step length

            note_delta_offset = {
                part_staff: 0
                for part_staff in range(1, part.staff_count + 1)
            }

            chord_stepout = True

            for note in parted_measures[part.info.id].notes:
                if not note.chord:
                    for part_staff in range(1, part.staff_count + 1):
                        note_offset[note.staff] += note_delta_offset[note.staff]
                        note_delta_offset[note.staff] = 0

                part_position = position_part_staff(staff_prop, staves_position, sheet, part.info.id, note.staff)
                staff_octave = guessed_staff_octave[note.staff] or default_octave

                chord_offset = (50 if note.chord else 0)
                horizontal_note_position = note_offset[note.staff] + (chord_offset if chord_stepout else 0)
                print(f'{chord_offset=} {chord_stepout=} {note_offset[note.staff]=} {horizontal_note_position=}')

                print(f'{note=}')
                if not note.rest:
                    vertical_note_position = part_position.y + get_note_position(staff_prop, staff_octave, note.pitch)
                    note_sign = get_note_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_note_position))]
                else:
                    vertical_note_position = part_position.y + staff_prop.staff_height // 2
                    note_sign = get_rest_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_note_position))]

                note_lenght = measure_length / notes_times[note.type] if note.type else notes_times['whole']
                if note.chord:
                    chord_stepout = not chord_stepout
                    note_delta_offset[note.staff] = min(
                        note_lenght + (note_lenght / 2 if note.dot else 0),
                        note_delta_offset[note.staff]
                    )
                else:
                    chord_stepout = True
                    note_delta_offset[note.staff] = note_lenght + (note_lenght / 2 if note.dot else 0)

                print(f'{note_offset=}')
                print(f'{note_delta_offset=}')

    # markup measures:
    #  start stops
    #  octave sign (number)
    #  notes
    #  beams
    #  stems
    #  ligas
    # markup cross measures ligas and signs
    yield objects


markup = markup_score_sheet(page_prop, staff_prop, sheet)

file_path = 'exhaust/music_xml_out_{page_number}.svg'
for page_idx, page_markup in enumerate(markup_score_sheet(page_prop, staff_prop, sheet)):
    render(page_prop, page_markup, file_path, page_idx)
