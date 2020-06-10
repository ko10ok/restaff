from pprint import pprint

from src import read_music_xml, ScoreSheet, StaffProperties, PageProperties, get_staffs_count, render, markup_title

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
    # markup measures:
    #  start stops
    #  octave sign (number)
    #  notes
    #  beams
    #  stems
    #  ligas
    # markup cross measures ligas and signs
    return objects


markup = markup_score_sheet(page_prop, staff_prop, sheet)

render(page_prop, markup)
