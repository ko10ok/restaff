from pprint import pprint

import svgwrite
from svgwrite.shapes import Polyline
from svgwrite.text import Text

from src import read_music_xml, ScoreSheet, StaffProperties, PageProperties, render, markup_title, \
    get_staffs_count, staff_line, part_staff_positions, guess_measure_octave, \
    max_guess_parted_measure_length, Point, position_part_staff, title_place_heigh, staves_position_marker, debug_text

## reads
music_xml_sheet = read_music_xml('examples/musicxml/His Theme experiments multi instruments.musicxml')
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
    measure_start_position = staff_prop.left_offset
    staves_position = Point(staff_prop.left_offset, staff_prop.top_offset)
    staff_unused_width = (page_prop.width - staff_prop.right_offset - staff_prop.left_offset) // 20
    parted_measure_octaves = {}

    staff_marker_source = staves_position_marker(page_prop, staff_prop, title_place_heigh(page_prop, staff_prop))

    for measure_number in range(total_measures_count):
        print(f'--------------- {measure_number=} -----------------')

        if start_line:
            measure_start_position = staff_prop.left_offset
            measure_end_position = staff_prop.left_offset
            try:
                staves_position = next(staff_marker_source)
            except:
                # flush page
                yield objects
                objects = []

                # switch page
                staff_marker_source = staves_position_marker(page_prop, staff_prop, staff_prop.top_offset)
                staves_position = next(staff_marker_source)

            parts_staff_offsets = part_staff_positions(staff_prop, staves_position, sheet)
            for position in parts_staff_offsets.values():
                objects += staff_line(page_prop, staff_prop, position)
            start_line = False

        # measure length

        measures_left_count = total_measures_count - measure_number
        page_staff_end = page_prop.width - staff_prop.right_offset
        measure_start_position = measure_end_position
        page_width_left = page_staff_end - measure_start_position
        measure_length = max_guess_parted_measure_length(
            page_prop=page_prop,
            staff_prop=staff_prop,
            measures=[part.measures[measure_number] for part in sheet.parts],
            measures_left_count=measures_left_count,
            page_width_left=page_width_left
        )

        measure_end_position = measure_start_position + measure_length

        objects += [debug_text(Point(measure_start_position, staves_position.y), f'm{measure_number} start')]
        objects += [debug_text(Point(measure_end_position, staves_position.y + 100), f'm{measure_number} stop')]

        if page_staff_end - measure_end_position < staff_unused_width:
            start_line = True
            measure_end_position = page_staff_end

        objects += [Polyline(
            points=[(measure_start_position, staves_position.y),
                    (measure_start_position, staves_position.y + staff_prop.parts_height)]
        ).stroke(
            color=svgwrite.rgb(0, 0, 0),
            width=2,
            linejoin='bevel',
        )]
        objects += [Polyline(
            points=[(measure_end_position, staves_position.y),
                    (measure_end_position, staves_position.y + staff_prop.parts_height)]
        ).stroke(
            color=svgwrite.rgb(0, 0, 0),
            width=2,
            linejoin='bevel',
        )]

        measure_left_offset = 50
        measure_right_offset = 50

        # octaves numbers
        for part in sheet.parts:
            if part.info.id not in parted_measure_octaves:
                parted_measure_octaves[part.info.id] = guess_measure_octave(part.measures[measure_number])
        for part in sheet.parts:
            for staff in range(1, part.staff_count + 1):
                staff_octave_point = position_part_staff(staff_prop, staves_position, sheet, part.info.id, staff)
                font_size = staff_prop.staff_line_offset * 2
                objects += [Text(
                    f'{parted_measure_octaves[part.info.id][staff] or default_octave}o',
                    insert=(staff_octave_point.x + 5, staff_octave_point.y + staff_prop.staff_height),
                    fill="rgb(0,0,0)",
                    style=f"font-size:{font_size}; font-family:Arial",
                )]

        for part in sheet.parts:
            measure = part.measures[measure_number]
            print(f'{measure_number}, {len(measure.notes)}')

            for note in measure.notes:
                print(f'{note.name} {part.info.id} {note.staff} {parts_staff_offsets[(part.info.id, note.staff or 1)]}')

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
