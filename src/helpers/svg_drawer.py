from typing import List

import svgwrite
from svgwrite.base import BaseElement

from ..types import PageProperties


# TODO (?) split render result objects from BaseElement drawing object
def render(page_prop: PageProperties, objects: List[BaseElement], file_path='exhaust/music_xml_out.svg'):
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
