from pprint import pprint

from src.helpers import markup_title, staff_line, part_staff_positions, guess_measure_octave, position_part_staff, \
    title_place_heigh, staves_position_marker, read_music_xml, get_staffs_count, place_next_measure, render, \
    markup_measure, markup_measure_octave, get_note_position, notes_times, \
    get_note_sign, markup_note, calc_measure_length, fit_measure_length_in_page, correct_measure, get_rest_sign, \
    markup_measure_time
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

default_octave = 5


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
        # measure_length = guess_measure_length(
        #     page_prop, staff_prop,
        #     total_measures_count=total_measures_count,
        #     measures=[part.measures[measure_number] for part in sheet.parts],
        #     measure_number=measure_number,
        #     measure_start_position=last_measure_placement.end
        # )
        measure_length = calc_measure_length(
            page_prop, staff_prop, measures=[part.measures[measure_index] for part in sheet.parts]
        )

        # if current first measure wider then staff length
        if last_measure_placement.last_on_staff:
            measure_length = fit_measure_length_in_page(page_prop, staff_prop, measure_length,
                                                        last_measure_placement.end)

        measure_placement = place_next_measure(page_prop, staff_prop, last_measure_placement, measure_length)

        if measure_index + 1 < total_measures_count:
            next_measure_length = calc_measure_length(
                page_prop, staff_prop, measures=[part.measures[measure_index + 1] for part in sheet.parts]
            )
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, next_measure_length)
        else:
            measure_placement = correct_measure(page_prop, staff_prop, measure_placement, page_prop.width)

        objects += markup_measure(staff_prop, staves_position, measure_index + 1, measure_placement)

        def measure_offset_point(measure_placement, staves_position):
            return Point(measure_placement.start, staves_position.y)

        measure_point = measure_offset_point(measure_placement, staves_position)
        # octaves numbers
        # TODO optimize not-changed octave drawing
        for part in sheet.parts:
            guessed_staff_octave = guess_measure_octave(part.measures[measure_index])
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

                staff_octave, is_changed = parted_measure_octaves[part.info.id]
                if is_changed:
                    octave_text = f'{staff_octave[staff] or default_octave}'
                    objects += markup_measure_octave(staff_prop, octave_text, staff_measure_position)

        for part in sheet.parts:
            measure_time = part.measures[measure_index].time
            if part.info.id not in parted_measure_times:
                parted_measure_times[part.info.id] = (measure_time, True)
            else:
                if parted_measure_times[part.info.id][0] != measure_time or measure_placement.first_on_staff:
                    parted_measure_times[part.info.id] = (measure_time, True)
                else:
                    parted_measure_times[part.info.id] = (measure_time, False)

        for part in sheet.parts:
            for staff in range(1, part.staff_count + 1):
                staff_measure_position = position_part_staff(staff_prop, measure_point, sheet, part.info.id, staff)
                print(part.info.id, staff, staff_measure_position)

                staff_time, is_changed = parted_measure_times[part.info.id]
                print(f'{staff_time=} {is_changed=}')

                if is_changed:
                    objects += markup_measure_time(staff_prop, staff_time, staff_measure_position)

        measure_left_offset = 100
        measure_right_offset = 50
        measure_length = measure_placement.end - measure_placement.start - measure_left_offset - measure_right_offset

        for part in sheet.parts:
            measure = part.measures[measure_index]
            measure_beats = int(measure.time.beats)
            measure_beat_type = int(measure.time.beat_type)

            timed_measure = measure_length / measure_beat_type

            octave_left_offset = 50 if parted_measure_octaves[part.info.id][1] else 0
            time_left_offset = 50 if parted_measure_times[part.info.id][1] else 0

            note_offset = {
                part_staff: measure_point.x + measure_left_offset + octave_left_offset + time_left_offset
                for part_staff in range(1, part.staff_count + 1)
            }

            # proportional placement sucks in 16th 32nd ... notes
            # might be partially fixed with dynamic measure length=f(measure_notes)
            # TODO chords must be drawn separately with minimal note step length
            for note in measure.notes:
                part_position = position_part_staff(staff_prop, staves_position, sheet, part.info.id, note.staff)
                staff_octave = parted_measure_octaves[part.info.id][0][note.staff] or default_octave
                # print(f'{note=}')
                if not note.rest:
                    vertical_note_position = part_position.y + get_note_position(staff_prop, staff_octave, note.pitch)
                    horizontal_note_position = note_offset[note.staff]
                    note_sign = get_note_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_note_position))]
                else:
                    print(f'{note=}')
                    vertical_note_position = part_position.y + staff_prop.staff_height // 2
                    horizontal_note_position = note_offset[note.staff]
                    note_sign = get_rest_sign(note)
                    objects += [markup_note(note_sign, Point(horizontal_note_position, vertical_note_position))]

                note_lenght = measure_length / notes_times[note.type] if note.type else notes_times['whole']
                note_offset[note.staff] += note_lenght + (note_lenght / 2 if note.dot else 0)

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
