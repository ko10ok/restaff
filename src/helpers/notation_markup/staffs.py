import svgwrite
from svgwrite.shapes import Polyline

from .title import title_place_heigh
from ...types import PageProperties, StaffProperties, Point


def staff_line(page_prop: PageProperties, staff_prop: StaffProperties, point: Point):
    x, y = point
    lines = []
    lenght = page_prop.width - point.x - staff_prop.right_offset
    for i in range(7):
        dotted_lines = [1, 1, 0, 1, 1, 0, 1]
        line = Polyline(
            points=[(x, y + i * staff_prop.staff_line_offset), (x + lenght, y + i * staff_prop.staff_line_offset)]
        ).stroke(
            color=svgwrite.rgb(0, 0, 0),
            width=2,
            linejoin='bevel',
        )
        if dotted_lines[i]:
            line.dasharray([2])
        lines.append(line)
    return lines


# TODO add pages?
# def get_staff_position(page: PageProperties, staff_prop: StaffProperties, part_number, staff_number=0) -> Point:
#     part_y_position = staff_prop.top_offset + (staff_prop.parts_height + staff_prop.parts_offset) * part_number
#     staff_y_position = part_y_position + (staff_prop.staff_height + staff_prop.staff_offset) * staff_number
#     assert staff_y_position <= page.height, 'To far on page'
#
#     return Point(x=staff_prop.left_offset, y=staff_y_position)

def staves_position_marker(page_prop: PageProperties, staff_prop: StaffProperties):
    page = 0
    line = 0
    while True:
        if page == 0:
            top_offset = title_place_heigh(page_prop, staff_prop)
        else:
            top_offset = staff_prop.top_offset

        part_y_position = top_offset + (staff_prop.parts_height + staff_prop.parts_offset) * line

        if part_y_position + staff_prop.parts_height > page_prop.height - staff_prop.bottom_offset:
            page += 1
            line = 0
            continue

        yield Point(
            x=staff_prop.left_offset,
            y=part_y_position
        )
        line += 1


def staff_position_marker(staff_prop: StaffProperties, offset_point: Point):
    for staff_number in range(staff_prop.staff_count):
        staff_y_position = offset_point.y + (staff_prop.staff_height + staff_prop.staff_offset) * staff_number
        yield Point(
            x=staff_prop.left_offset,
            y=staff_y_position
        )
