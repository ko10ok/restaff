import argparse
import os
from pprint import pprint

from src.helpers import read_music_xml, \
    get_staffs_count, render
from src.markups.sheet import markup_score_sheet
from src.types import ScoreSheet, StaffProperties, PageProperties, MeasureProperties

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Processing not compressed music xml into svg rendered score pages with alternative music notation'
    )
    parser.add_argument('-i', '--input-file', action='store', help='input file path', required=True)
    parser.add_argument('-o', '--output-dir', action='store', help='output directory path, default=input file path',
                        default=None)
    parser.add_argument('-p', '--filename-pattern', action='store', help='output directory path',
                        default='rendered-scores-{}.svg')

    args = parser.parse_args()

    input_file_full_path = args.input_file
    output_directory = args.output_dir or os.path.dirname(os.path.abspath(input_file_full_path))
    file_pattern = args.filename_pattern
    print(f'Rendering {input_file_full_path} into {output_directory}/{file_pattern}')

    ## reads
    music_xml_sheet = read_music_xml(input_file_full_path)
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

    file_path = f'{output_directory}/{file_pattern}'

    ## marking up and render
    for page_idx, page_markup in enumerate(markup_score_sheet(page_prop, staff_prop, sheet)):
        render(page_prop, page_markup, file_path.format(page_idx), page_idx)
