from typing import List

import svgwrite
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from svgwrite.base import BaseElement

from restaff.types import PageProperties


# TODO (?) split render result objects from BaseElement drawing object
def render(page_prop: PageProperties, objects: List[BaseElement], file_path, page_number):
    view_box = '{} {} {} {}'.format(0, 0, page_prop.width, page_prop.height)

    dwg = svgwrite.Drawing(
        file_path,
        size=(f'{page_prop.width}px', f'{page_prop.height}px'),
        profile='tiny',
        viewBox=view_box
    )

    for obj in objects:
        dwg.add(obj)
    dwg.save(pretty=True)


def render_svgs(page_prop: PageProperties, marked_pages, file_path_pattern):
    pages_files = []
    for page_idx, page_markup in enumerate(marked_pages):
        full_file_name = file_path_pattern.format(page_idx)
        render(page_prop, page_markup, full_file_name, page_idx)
        pages_files += [full_file_name]
    return pages_files


def render_pdf(pages_files, pdf_file_name):
    from reportlab.pdfgen import canvas
    cnvs = canvas.Canvas(pdf_file_name)
    for page_file in pages_files:
        logger.debug(f'Rendering {page_file} to {pdf_file_name}')

        rl_score_image = svg2rlg(page_file)

        cnvs.setPageSize((rl_score_image.width, rl_score_image.height))
        renderPDF.draw(rl_score_image, cnvs, 0, 0)
        cnvs.showPage()
    cnvs.save()
