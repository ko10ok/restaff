import builtins
import cgi
import logging
import os
from uuid import uuid4

from aiohttp import web
from aiohttp_wsgi import WSGIHandler

from restaff.helpers import render_pdf, render_svgs, cleanup_temp_files, read_music_xml, get_staffs_count, \
    read_compressed_music_xml
from restaff.helpers.murmur2 import murmur2
from restaff.markups import markup_score_sheet
from restaff.types import ScoreSheet, StaffProperties, PageProperties, MeasureProperties

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
builtins.logger = logger


def parse_file_form():
    with open('restaff/res/file_form.html', 'r') as f:
        file_content = f.read()
    return file_content


# TODO make inmem file reading and inmem pdf rendering
def parse_file(form):
    try:
        fileitem = form['music_file']
    except KeyError:
        fileitem = None

    input_file_name = str(fileitem.filename)
    input_file = fileitem.file
    content = input_file.read()

    hash = murmur2(content)

    task_id = str(uuid4())

    input_file_full_path = f'./tmp/input-{hash}-tmp-file.mxml'
    if not os.path.exists(input_file_full_path):
        with open(input_file_full_path, 'wb') as file:
            file.write(content)

    tmp_file_pattern = f'./tmp/rendered-svgs-{task_id}-{{}}.svg'

    pdf_file_name = f'./tmp/rendered-pdf-{hash}.pdf'
    if os.path.exists(pdf_file_name):
        logger.info(f'already rendered {pdf_file_name}')
        with open(pdf_file_name, 'rb') as file:
            pdf = file.read()

        return web.Response(body=pdf, content_type='application/pdf')

    logger.info(f'Rendering {input_file_full_path} into {pdf_file_name}')

    ## reads
    if input_file_name.lower().endswith('.mxl'):
        music_xml_sheet = read_compressed_music_xml(input_file_full_path)
    elif input_file_name.lower().endswith('.musicxml') or input_file_name.lower().endswith('.xml'):
        music_xml_sheet = read_music_xml(input_file_full_path)
    else:
        return web.Response(body=b'<html><body><h2>not supported format</h2><a href="/">back</a><body></html>', content_type='text/html', status=400)
    sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)

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

    file_path_pattern = tmp_file_pattern

    rendered_svg = render_svgs(page_prop, marked_pages, file_path_pattern)

    full_pdf_file_name = f'{pdf_file_name}'
    render_pdf(rendered_svg, full_pdf_file_name)

    with open(pdf_file_name, 'rb') as file:
        pdf = file.read()

    cleanup_temp_files(rendered_svg)

    return web.Response(body=pdf, content_type='application/pdf')


def application(environ, start_response):
    extra_headers = []
    if environ.get('PATH_INFO') == '/':
        status = '200 OK'
        content = parse_file_form().encode('utf8')
        content_type = 'text/html'
    elif environ.get('PATH_INFO') == '/restaff':
        # use cgi module to read data
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        if 'music_file' in form:
            res = parse_file(form)
            status = str(res.status) + ' OK'
            content = res.body
            content_type = res.content_type
        else:
            status = '308 Permanent Redirect'
            content = b''
            content_type = 'text/html'
            extra_headers = [('Location ', '/')]
    else:
        status = '404 NOT FOUND'
        content = 'Page not found.'.encode('utf8')
        content_type = 'text/html'
    response_headers = [('Content-Type', content_type), ('Content-Length', str(len(content)))] + extra_headers
    start_response(status, response_headers)
    yield content


if __name__ == '__main__':
    wsgi_handler = WSGIHandler(application)
    app = web.Application()
    app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
    web.run_app(app)
