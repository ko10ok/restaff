import argparse
import os

from src.helpers import render_pdf, render_svgs, cleanup_temp_files, read_music_xml, get_staffs_count, \
    read_compressed_music_xml
from src.markups.sheet import markup_score_sheet
from src.types import ScoreSheet, StaffProperties, PageProperties, MeasureProperties

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Processing not compressed music xml into svg rendered score pages with alternative music notation'
    )
    parser.add_argument('-i', '--input-file', action='store', help='input file path', required=True)
    parser.add_argument('--pdf', action='store', help='output file path', default='rendered-scores.pdf')
    parser.add_argument('--keep-tmp', action='store_true', help='store temperal svg pictures', default=False)
    parser.add_argument('-o', '--output-dir', action='store', help='temperal files output directory path, default = input file path', default=None)

    args = parser.parse_args()

    input_file_full_path = args.input_file
    output_directory = args.output_dir or os.path.dirname(os.path.abspath(input_file_full_path))
    tmp_file_pattern = 'rendered-scores-{}.svg'
    keep_tmp_files = args.keep_tmp
    pdf_file_name = args.pdf

    print(f'args: {args}')
    print(f'Rendering {input_file_full_path} into {pdf_file_name}')

    ## reads
    if '.mxl' in input_file_full_path:
        music_xml_sheet = read_compressed_music_xml(input_file_full_path)
    elif 'musicxml' in input_file_full_path:
        music_xml_sheet = read_music_xml(input_file_full_path)
    else:
        exit(1)
    # pprint(music_xml_sheet)
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

    marked_pages = markup_score_sheet(page_prop, staff_prop, sheet)

    file_path_pattern = f'{output_directory}/{tmp_file_pattern}'

    rendered_svg = render_svgs(page_prop, marked_pages, file_path_pattern)

    full_pdf_file_name = f'{pdf_file_name}'
    render_pdf(rendered_svg, full_pdf_file_name)

    if not keep_tmp_files:
        cleanup_temp_files(rendered_svg)
