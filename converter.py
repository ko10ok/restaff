from pprint import pprint

from src.helpers import read_music_xml, \
    get_staffs_count, render
from src.markups.sheet import markup_score_sheet
from src.types import ScoreSheet, StaffProperties, PageProperties, MeasureProperties

## reads
music_xml_sheet = read_music_xml('examples/musicxml/notmania_ru-Ballade_pour_Adeline_.xml')
pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)
# pprint(sheet)

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

file_path = 'exhaust/music_xml_out_{page_number}.svg'

## marking up and render
for page_idx, page_markup in enumerate(markup_score_sheet(page_prop, staff_prop, sheet)):
    render(page_prop, page_markup, file_path, page_idx)
