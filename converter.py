from itertools import islice
from pprint import pprint

from svgwrite.path import Path

from src import read_music_xml, ScoreSheet, StaffProperties, PageProperties, render, markup_title, \
    staves_position_marker, whole_note, staff_position_marker, get_staffs_count, staff_line, moved_path

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


## marking up
def markup_score_sheet(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    objects = []
    # mark up title, author
    objects += markup_title(page_prop, staff_prop, sheet)
    # markup stuffs and parts groups
    staff_marker_source = staves_position_marker(page_prop, staff_prop)

    # stuff markup test - demo with pages projection
    for idx, point in enumerate(islice(staff_marker_source, 2)):
        for staff_position in staff_position_marker(staff_prop, point):
            objects += [
                Path(d=moved_path(whole_note.centred, point.x + 100 * idx, staff_position.y))
            ]
            objects += staff_line(page_prop, staff_prop, staff_position)

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
