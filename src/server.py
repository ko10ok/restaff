import builtins
import logging
from uuid import uuid4

from aiohttp import web

from restaff.helpers import render_pdf, render_svgs, cleanup_temp_files, read_music_xml, get_staffs_count, \
    read_compressed_music_xml
from restaff.markups import markup_score_sheet
from restaff.types import ScoreSheet, StaffProperties, PageProperties, MeasureProperties

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
builtins.logger = logger


async def parse_file_form(request):
    return web.FileResponse('restaff/res/file_form.html')

# TODO make inmem file reading and inmem pdf rendering
async def parse_file(request):
    data = await request.post()
    input_file_name = data['music_file'].filename
    input_file = data['music_file'].file
    content = input_file.read()

    task_id = str(uuid4())

    input_file_full_path = f'./tmp/input-{task_id}-tmp-file.mxml'
    with open(input_file_full_path, 'wb') as file:
        file.write(content)

    tmp_file_pattern = f'./tmp/rendered-svgs-{task_id}-{{}}.svg'
    pdf_file_name = f'./tmp/rendered-pdf-{task_id}-{{}}.svg'

    logger.info(f'Rendering {input_file_full_path} into {pdf_file_name}')

    ## reads
    if '.mxl' in input_file_name:
        music_xml_sheet = read_compressed_music_xml(input_file_full_path)
    elif 'musicxml' in input_file_name:
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
        right_offset=40,
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

    file_path_pattern = tmp_file_pattern

    rendered_svg = render_svgs(page_prop, marked_pages, file_path_pattern)

    full_pdf_file_name = f'{pdf_file_name}'
    render_pdf(rendered_svg, full_pdf_file_name)

    with open(pdf_file_name, 'rb') as file:
        pdf = file.read()

    cleanup_temp_files(rendered_svg + [input_file_full_path, pdf_file_name])

    return web.Response(body=pdf, content_type='application/pdf')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/', parse_file_form)])
    app.add_routes([web.post('/restaff', parse_file)])

    web.run_app(app, host="0.0.0.0", port=8080)
