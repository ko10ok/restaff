from pprint import pprint

from src.helpers import markup_title, staff_line, part_staff_positions, guess_measure_octave, position_part_staff, \
    title_place_heigh, staves_position_marker, read_music_xml, get_staffs_count, guess_measure_length, \
    place_next_measure, render, markup_measure, markup_measure_octave, get_note_position, notes_times, \
    get_note_sign, markup_note
from src.types import ScoreSheet, StaffProperties, PageProperties, Point, MeasurePosition

## reads
music_xml_sheet = read_music_xml('examples/musicxml/His Theme notes dots timings.musicxml')
pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)
pprint(sheet)

page_prop = PageProperties(width=2977.2, height=4208.4)

## setup
staff_prop = StaffProperties(
    left_offset=194.232,
    right_offset=2977.2 - 2835.47,
    top_offset=566.733,
    bottom_offset=50,
    staff_line_offset=25,
    staff_line_count=7,
    staff_offset=80,
    staff_count=get_staffs_count(sheet),
    parts_offset=140
)

default_octave = 3


## marking up
def markup_score_sheet(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    objects = []

    # mark up title, author
    objects += markup_title(page_prop, staff_prop, sheet)

    total_measures_count = max([len(part.measures) for part in sheet.parts])

    start_line = True
    staves_position = Point(staff_prop.left_offset, staff_prop.top_offset)
    staff_unused_width = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // 20
    parted_measure_octaves = {}

    staff_marker_source = staves_position_marker(page_prop, staff_prop, title_place_heigh(page_prop, staff_prop))

    measure_placement = MeasurePosition(0, staff_prop.left_offset, first_on_staff=False, last_on_staff=True)

    for measure_number in range(total_measures_count):
        print(f'--------------- {measure_number=} -----------------')

        last_measure_placement = measure_placement
        if last_measure_placement.last_on_staff:

            # setup initial measure placement
            last_measure_placement = MeasurePosition(
                0, staff_prop.left_offset,
                first_on_staff=False,
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

        # forward measure
        measure_length = guess_measure_length(
            page_prop, staff_prop,
            total_measures_count=total_measures_count,
            measures=[part.measures[measure_number] for part in sheet.parts],
            measure_number=measure_number,
            measure_start_position=last_measure_placement.end
        )
        measure_placement = place_next_measure(page_prop, staff_prop, last_measure_placement, measure_length)
        objects += markup_measure(staff_prop, staves_position, measure_placement)

        def measure_offset_point(measure_placement, staves_position):
            return Point(measure_placement.start, staves_position.y)

        measure_point = measure_offset_point(measure_placement, staves_position)
        # octaves numbers
        # TODO optimize not-changed octave drawing
        for part in sheet.parts:
            guessed_staff_octave = guess_measure_octave(part.measures[measure_number])
            if part.info.id not in parted_measure_octaves:
                parted_measure_octaves[part.info.id] = (guessed_staff_octave, True)
            else:
                if parted_measure_octaves[part.info.id][0] != guessed_staff_octave or measure_placement.first_on_staff:
                    parted_measure_octaves[part.info.id] = (guessed_staff_octave, True)
                else:
                    parted_measure_octaves[part.info.id] = (guessed_staff_octave, False)

        print(parted_measure_octaves)
        for part in sheet.parts:
            for staff in range(1, part.staff_count + 1):
                staff_measure_position = position_part_staff(staff_prop, measure_point, sheet, part.info.id, staff)
                print(part.info.id, staff, staff_measure_position)

                staff_octave_changes = parted_measure_octaves[part.info.id]
                octave_text = f'{staff_octave_changes[0][staff] or default_octave}' if staff_octave_changes[1] else ''
                objects += [markup_measure_octave(staff_prop, octave_text, staff_measure_position)]

        measure_left_offset = 100
        measure_right_offset = 50
        measure_length = measure_placement.end - measure_placement.start - measure_left_offset - measure_right_offset

        for part in sheet.parts:
            measure = part.measures[measure_number]
            measure_beats = int(measure.time.beats)
            measure_beat_type = int(measure.time.beat_type)

            timed_measure = measure_length / measure_beat_type

            note_offset = {
                part_staff: measure_point.x + measure_left_offset
                for part_staff in range(1, part.staff_count + 1)
            }

            for note in measure.notes:

                part_position = position_part_staff(staff_prop, staves_position, sheet, part.info.id, note.staff or 1)
                staff_octave = parted_measure_octaves[part.info.id][0][note.staff or 1] or default_octave
                # print(f'{note.name=} {part.info.id=} {note.staff=} {staff_octave=} {note.type=} {note.time_modification=} {note.dot=} {parts_staff_offsets[(part.info.id, note.staff or 1)]}')
                print(f'{note=}')
                if not note.rest:
                    vertical_note_position = part_position.y + get_note_position(staff_prop, staff_octave, note.pitch)
                    horizontal_note_position = note_offset[note.staff or 1]
                    note_sign = get_note_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_note_position))]
                else:
                    pass

                note_lenght = measure_length / notes_times[note.type] if note.type else notes_times['whole']
                note_offset[note.staff or 1] += note_lenght + (note_lenght / 2 if note.dot else 0)

            octaves = guess_measure_octave(measure)

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
