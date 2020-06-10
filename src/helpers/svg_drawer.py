from typing import List

import svgwrite
from svgwrite.base import BaseElement

from ..types import PageProperties


# TODO (?) split render result objects from BaseElement drawing object
def render(page_prop: PageProperties, objects: List[BaseElement], file_path, page_number):
    view_box = '{} {} {} {}'.format(0, 0, page_prop.width, page_prop.height)

    file_path='exhaust/music_xml_out_{page_number}.svg'

    dwg = svgwrite.Drawing(
        file_path.format(page_number=page_number),
        size=(f'{page_prop.width}px', f'{page_prop.height}px'),
        profile='tiny',
        viewBox=view_box
    )

    for obj in objects:
        dwg.add(obj)
    dwg.save(pretty=True)
