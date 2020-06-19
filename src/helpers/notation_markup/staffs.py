import svgwrite
from svgwrite.shapes import Polyline, Circle
from svgwrite.text import Text

from .title import title_place_heigh
from ...types import PageProperties, StaffProperties, Point, ScoreSheet, MeasurePosition, TimeMeasure


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


# exctract paging logic to basic offset
def staves_position_paginator_marker(page_prop: PageProperties, staff_prop: StaffProperties):
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


def staves_position_marker(page_prop: PageProperties, staff_prop: StaffProperties, top_offset):
    line = 0
    while True:
        part_y_position = top_offset + (staff_prop.parts_height + staff_prop.parts_offset) * line

        if part_y_position + staff_prop.parts_height > page_prop.height - staff_prop.bottom_offset:
            return

        yield Point(
            x=staff_prop.left_offset,
            y=part_y_position
        )
        line += 1


def staff_position_marker(staff_prop: StaffProperties, offset_point: Point):
    for staff_number in range(staff_prop.staff_count):
        staff_y_position = offset_point.y + (staff_prop.staff_height + staff_prop.staff_offset) * staff_number
        yield Point(
            x=offset_point.x,
            y=staff_y_position
        )


def part_staff_positions(staff_prop: StaffProperties, offset_point: Point, sheet: ScoreSheet):
    staffs_positions = staff_position_marker(staff_prop, offset_point)
    staffs_ids = []
    for part in sheet.parts:
        voices = part.measures[0].staves
        for staff in range(voices):
            staffs_ids += [(part.info.id, staff + 1)]
            print(part.info.id, staff)
    return dict(zip(staffs_ids, staffs_positions))


def enumerate_sheet_staff(sheet: ScoreSheet):
    idx = 0
    staff_map = {}
    for part in sheet.parts:
        if part.info.id not in staff_map:
            staff_map[part.info.id] = {}
        for staff in range(1, part.staff_count + 1):
            staff_map[part.info.id][staff] = idx
            idx += 1
    return staff_map


def resolve_part_staff(sheet: ScoreSheet, part_id, staff):
    staff_map = enumerate_sheet_staff(sheet)
    return staff_map[part_id][staff]


def position_part_staff(staff_prop: StaffProperties, offset_point: Point, sheet: ScoreSheet, part_id, staff):
    staffs_positions = staff_position_marker(staff_prop, offset_point)
    stuff_number = resolve_part_staff(sheet, part_id, staff)
    return list(staffs_positions)[stuff_number]


def markup_measure(staff_prop: StaffProperties, staves_position, height, measure_number,
                   measure_placement: MeasurePosition):
    return [
               Polyline(
                   points=[(measure_placement.start, staves_position.y),
                           (measure_placement.start, staves_position.y + height)]
               ).stroke(
                   color=svgwrite.rgb(0, 0, 0),
                   width=2,
                   linejoin='bevel',
               )
           ] + ([
                    Polyline(
                        points=[(measure_placement.end, staves_position.y),
                                (measure_placement.end, staves_position.y + height)]
                    ).stroke(
                        color=svgwrite.rgb(0, 0, 0),
                        width=2,
                        linejoin='bevel',
                    )
                ] if measure_placement.last_on_staff else []) + (
               [
                   Text(
                       str(measure_number),
                       insert=(measure_placement.start - 5,
                               staves_position.y - 10),
                       fill="rgb(0,0,0)",
                       style=f"font-size:{staff_prop.staff_line_offset}; font-family:Arial",
                   )
               ] if measure_placement.first_on_staff or 'debug' else []
           )


def markup_measure_octave(staff_prop: StaffProperties, octave_text, staff_measure_point):
    x = staff_measure_point.x + 25
    y = staff_measure_point.y + staff_prop.staff_height - staff_prop.staff_line_offset
    r = staff_prop.staff_line_offset * 0.8
    font_size = staff_prop.staff_line_offset * 1.45
    return [
        Circle(center=(x, y), r=r, fill="rgb(255,255,255)", stroke="rgb(0,0,0)", stroke_width=2),
        Text(
            octave_text,
            insert=(x, y + font_size * 0.35),
            fill="rgb(0,0,0)",
            text_anchor="middle",
            style=f"font-size:{font_size}; font-family:Arial",
        )]


def markup_measure_time(staff_prop: StaffProperties, time: TimeMeasure, staff_measure_point):
    return [
        Text(
            str(time.beats),
            insert=(staff_measure_point.x + 60,
                    staff_measure_point.y + staff_prop.staff_line_offset * 2.75),
            fill="rgb(0,0,0)",
            text_decoration="underline",
            style=f"font-size:{staff_prop.staff_line_offset * 2.5}; font-family:Arial; font-weight: bold",
        ),
        Text(
            str(time.beat_type),
            insert=(staff_measure_point.x + 60,
                    staff_measure_point.y + staff_prop.staff_line_offset * 5),
            fill="rgb(0,0,0)",
            style=f"font-size:{staff_prop.staff_line_offset * 2.5}; font-family:Arial; font-weight: bold",
        )]


def markup_part(page_prop: PageProperties, staff_prop: StaffProperties, staff_positions):
    objects = []
    for staff, position in staff_positions.items():
        staves_position = Point(staff_prop.left_offset, position)
        objects += staff_line(page_prop, staff_prop, staves_position)
    return objects
