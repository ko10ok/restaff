from collections import namedtuple, OrderedDict
from pprint import pprint
from typing import NamedTuple, List, Any

import svgwrite
from svgwrite.path import Path
from svgwrite.shapes import Polyline
from svgwrite.text import Text

from src import read_music_xml, ScoreSheet, Part, Measure

list_width = 2977.2
list_height = 4208.4
view_box = '{} {} {} {}'.format(0, 0, list_width, list_height)

dwg = svgwrite.Drawing('exhaust/music_xml_out.svg', size=(f'{list_width}px', f'{list_height}px'), profile='tiny',
                       viewBox=view_box)

start_x = 194.232
lenght = 2835.47 - 194.232
start_y = 566.733
step_lines_y = 25
# step_staff_y = 162.5
step_staff_y = 230
step_parts_y = 500

Point = namedtuple('Point', ['x', 'y'])

PageProperties = namedtuple('Page', ['width', 'height'])


class StaffProperties(NamedTuple):
    left_offset: Any
    right_offset: Any
    top_offset: Any
    staff_line_offset: Any
    staff_line_count: Any
    staff_offset: Any
    staff_count: Any
    parts_offset: Any

    @property
    def staff_height(self):
        return self.staff_line_offset * (self.staff_line_count - 1)

    @property
    def parts_height(self):
        return self.staff_height * self.staff_count + self.staff_offset * (self.staff_count - 1)

    def parts_count_per_page(self, page: PageProperties):
        return int((page.height - self.top_offset) // (self.parts_height + self.parts_offset))


# Note = namedtuple('Note', ['note', 'octave', 'alter'])

class Note(NamedTuple):
    step: str
    octave: int
    alter: int = 0

    @classmethod
    def from_note(self, note: OrderedDict):
        return Note(note.get('step'), int(note.get('octave')), int(note.get('alter', 0)))


notes_offsets = {
    'C': (0.5, 0),
    'C#': (1, -1),
    'Db': (1, -1),
    'D': (1, 0),
    'D#': (1, 1),
    'Eb': (1, -1),
    'E': (1.5, 0),
    'Fb': (1.5, 0),
    'E#': (2, -1),
    'F': (2, -1),
    'F#': (2, 0),
    'Gb': (2, 0),
    'G': (2, 1),
    'G#': (2.5, 0),
    'Ab': (2.5, 0),
    'A': (3, -1),
    'A#': (3, 0),
    'Bb': (3, 0),
    'B': (3, 1),
    'Cb': (3, 1),
    'B#': (3.5, 0),
}


def get_note_orientation(note: Note) -> int:
    note = note.step + ['', '#', 'b'][note.alter]
    note_grade, note_orientation = notes_offsets[note]
    return note_orientation


def get_note_position(staff_prop, staff_base_octave, note: Note) -> int:
    last_line = (staff_prop.staff_line_count - 1) * staff_prop.staff_line_offset

    octave_offset = staff_prop.staff_line_offset * 3  # 2 lines 3 spaces divides 1 octave
    note_octave_offset = (note.octave - staff_base_octave) * octave_offset

    note = note.step + ['', '#', 'b'][note.alter]
    note_grade, note_orientation = notes_offsets[note]

    note_offset = note_grade * staff_prop.staff_line_offset

    return last_line - note_octave_offset - note_offset


# < path
# class ="Note"
# d="M574.42,855.498 C572.076,855.498 570.384,856.311 569.342,857.936 C568.175,859.498 567.592,861.618 567.592,864.295 C567.592,867.358 568.404,869.993 570.029,872.201 C571.654,874.347 573.446,875.847 575.404,876.701 C577.154,877.545 579.009,877.967 580.967,877.967 C583.248,877.967 584.972,877.155 586.139,875.53 C587.243,873.894 587.795,871.774 587.795,869.17 C587.795,866.108 586.983,863.472 585.358,861.264 C583.733,859.181 581.977,857.681 580.092,856.764 C578.196,855.92 576.305,855.498 574.42,855.498 M577.748,852.967 C584.779,852.967 590.639,854.332 595.326,857.061 C600.076,859.8 602.451,863.024 602.451,866.733 C602.451,870.701 600.009,873.957 595.123,876.498 C590.238,879.165 584.446,880.498 577.748,880.498 C570.842,880.498 564.983,879.134 560.17,876.405 C555.347,873.665 552.936,870.441 552.936,866.733 C552.936,862.764 555.41,859.509 560.358,856.967 C565.243,854.3 571.04,852.967 577.748,852.967"
# / >


whole_note = "M574.42,855.498 C572.076,855.498 570.384,856.311 569.342,857.936 C568.175,859.498 567.592,861.618 567.592,864.295 C567.592,867.358 568.404,869.993 570.029,872.201 C571.654,874.347 573.446,875.847 575.404,876.701 C577.154,877.545 579.009,877.967 580.967,877.967 C583.248,877.967 584.972,877.155 586.139,875.53 C587.243,873.894 587.795,871.774 587.795,869.17 C587.795,866.108 586.983,863.472 585.358,861.264 C583.733,859.181 581.977,857.681 580.092,856.764 C578.196,855.92 576.305,855.498 574.42,855.498 M577.748,852.967 C584.779,852.967 590.639,854.332 595.326,857.061 C600.076,859.8 602.451,863.024 602.451,866.733 C602.451,870.701 600.009,873.957 595.123,876.498 C590.238,879.165 584.446,880.498 577.748,880.498 C570.842,880.498 564.983,879.134 560.17,876.405 C555.347,873.665 552.936,870.441 552.936,866.733 C552.936,862.764 555.41,859.509 560.358,856.967 C565.243,854.3 571.04,852.967 577.748,852.967"
lower_whole_note_x30 = "M1482.26,415 C1472.27,161.56 1077.98,-12.21 660.97,8.84 C243.95,29.9 25.57,260.37 16.38,342.33 C7.18,424.3 10.72,412.53 226.89,415 C443.07,417.47 445.13,424.2 456.13,462.05 C468.28,503.89 487.15,542.19 512.74,576.97 C561.49,641.34 615.24,686.33 673.98,711.95 C726.47,737.27 782.12,749.93 840.85,749.93 C909.27,749.93 960.99,725.57 996,676.83 C1029.11,627.75 1037.09,531.56 1037.09,453.45 C1037.09,419.7 1126.82,417.89 1210.63,415 C1338.98,410.57 1480.76,417.8 1478.69,415 M744.29,0 C955.2,0 1130.98,40.95 1271.58,122.81 C1414.07,204.97 1485.31,301.68 1485.31,412.94 C1485.31,531.97 1412.06,629.64 1265.49,705.86 C1118.95,785.87 945.21,825.85 744.29,825.85 C537.13,825.85 361.38,784.94 217,703.07 C72.32,620.88 0,524.17 0,412.94 C0,293.88 74.21,196.24 222.64,119.99 C369.17,39.99 543.07,0 744.29,0"
upper_whole_note_x30 = "M644.46,75.92 C574.15,75.92 523.39,100.31 492.13,149.06 C457.13,195.91 439.64,259.51 439.64,339.81 C439.64,361.86 418.1,418.24 197.09,415 C109.01,413.71 -99.3,407.38 93.75,606.5 C181.24,696.74 343.67,767.72 498.73,797.74 C644.77,826 785.98,815.87 798.01,815.93 C1004.72,817.05 1293.97,709.22 1378.03,622.5 C1462.09,535.78 1442.14,554.91 1471.64,486.12 C1478.14,470.99 1485.08,429.15 1455.56,422.31 C1350.91,398.05 1056.97,434.97 1047.66,404.39 C1035.47,364.41 997.18,282.33 972.57,248.89 C923.82,186.4 871.15,141.41 814.6,113.9 C757.73,88.58 701,75.92 644.46,75.92 M744.29,0 C955.2,0 1130.98,40.95 1271.58,122.81 C1414.07,204.97 1485.31,301.68 1485.31,412.94 C1485.31,531.97 1412.06,629.64 1265.49,705.86 C1118.95,785.87 945.21,825.85 744.29,825.85 C537.13,825.85 361.38,784.94 217,703.07 C72.32,620.88 0,524.17 0,412.94 C0,293.88 74.21,196.24 222.64,119.99 C369.17,39.99 543.07,0 744.29,0"
# lower_whole_note_x30 = scaled_path(lower_whole_note_x30, 0.033)
# upper_whole_note_x30 = scaled_path(upper_whole_note_x30, 0.033)
lower_whole_note = 'M48.915,13.695 C48.585,5.331 35.573,-0.403 21.812,0.292 C8.050,0.987 0.844,8.592 0.541,11.297 C0.237,14.002 0.354,13.613 7.487,13.695 C14.621,13.777 14.689,13.999 15.052,15.248 C15.453,16.628 16.076,17.892 16.920,19.040 C18.529,21.164 20.303,22.649 22.241,23.494 C23.974,24.330 25.810,24.748 27.748,24.748 C30.006,24.748 31.713,23.944 32.868,22.335 C33.961,20.716 34.224,17.541 34.224,14.964 C34.224,13.850 37.185,13.790 39.951,13.695 C44.186,13.549 48.865,13.787 48.797,13.695 M24.562,0.000 C31.522,0.000 37.322,1.351 41.962,4.053 C46.664,6.764 49.015,9.955 49.015,13.627 C49.015,17.555 46.598,20.778 41.761,23.293 C36.925,25.934 31.192,27.253 24.562,27.253 C17.725,27.253 11.926,25.903 7.161,23.201 C2.387,20.489 0.000,17.298 0.000,13.627 C0.000,9.698 2.449,6.476 7.347,3.960 C12.183,1.320 17.921,0.000 24.562,0.000'
upper_whole_note = 'M21.267,2.505 C18.947,2.505 17.272,3.310 16.240,4.919 C15.085,6.465 14.508,8.564 14.508,11.214 C14.508,11.941 13.797,13.802 6.504,13.695 C3.597,13.652 -3.277,13.444 3.094,20.015 C5.981,22.992 11.341,25.335 16.458,26.325 C21.277,27.258 25.937,26.924 26.334,26.926 C33.156,26.963 42.701,23.404 45.475,20.543 C48.249,17.681 47.591,18.312 48.564,16.042 C48.779,15.543 49.008,14.162 48.033,13.936 C44.580,13.136 34.880,14.354 34.573,13.345 C34.171,12.026 32.907,9.317 32.095,8.213 C30.486,6.151 28.748,4.667 26.882,3.759 C25.005,2.923 23.133,2.505 21.267,2.505 M24.562,0.000 C31.522,0.000 37.322,1.351 41.962,4.053 C46.664,6.764 49.015,9.955 49.015,13.627 C49.015,17.555 46.598,20.778 41.761,23.293 C36.925,25.934 31.192,27.253 24.562,27.253 C17.725,27.253 11.926,25.903 7.161,23.201 C2.387,20.489 0.000,17.298 0.000,13.627 C0.000,9.698 2.449,6.476 7.347,3.960 C12.183,1.320 17.921,0.000 24.562,0.000'


def moved_path(d, position_x, position_y, offset_x=0, offset_y=0):
    str_points = d.split(' ')
    points = [
        (action := b[0], start_from := action.isalpha(), pair := b.split(','), float(pair[0][start_from:]),
         float(pair[1]))
        for b in str_points
    ]
    center_x = (min([point[3] for point in points]) + max([point[3] for point in points])) / 2
    center_y = (min([point[4] for point in points]) + max([point[4] for point in points])) / 2

    target_x, target_y = position_x + offset_x, position_y + offset_y

    centred_path = ' '.join([
        f'{action if start_from else ""}{(x - center_x + target_x):.3f},{(y - center_y + target_y):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


#  Readed  writing experiments
music_xml_sheet = read_music_xml('examples/musicxml/His Theme experiments multi instruments.musicxml')
pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)


def get_part_staves_count(part: Part):
    return part.measures[0].staves


def distribute_staffs(parts: List[Part]):
    part_staff_mapping = {}
    total = 0

    for part in parts:
        part_staff_count = get_part_staves_count(part)

        part_staff_mapping.update({
            part.info.id: total
        })
        total += part_staff_count
    part_staff_mapping.update({'total_count': total})
    return part_staff_mapping


staff_mapping = distribute_staffs(sheet.parts)
print(staff_mapping)

current_page = PageProperties(width=2977.2, height=4208.4)
current_staff_prop = StaffProperties(
    left_offset=194.232,
    right_offset=2977.2 - 2835.47,
    top_offset=566.733,
    staff_line_offset=25,
    staff_line_count=7,
    staff_offset=80,
    staff_count=staff_mapping['total_count'],
    parts_offset=140
)


def staff_line(x, y, lenght):
    lines = []
    for i in range(7):
        dotted_lines = [1, 1, 0, 1, 1, 0, 1]
        line = Polyline(
            points=[(x, y + i * step_lines_y), (x + lenght, y + i * step_lines_y)]
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
def get_staff_position(page: PageProperties, staff_prop: StaffProperties, part_number, staff_number=0) -> Point:
    part_y_position = staff_prop.top_offset + (staff_prop.parts_height + staff_prop.parts_offset) * part_number
    staff_y_position = part_y_position + (staff_prop.staff_height + staff_prop.staff_offset) * staff_number
    # assert staff_y_position <= page.height, 'To far on page'

    return Point(x=staff_prop.left_offset, y=staff_y_position)


def measure_width(page: PageProperties, staff_prop: StaffProperties, measure: Measure):
    staff_length = page.width - staff_prop.right_offset - staff_prop.left_offset
    default_measure_width = int(staff_length // 4)
    # mby base_notes = measure.time.beat_type
    # scaled_on_notes_count = default_measure_width * (len(measure.notes | filter on max from parts) / measure.time.beat_type)

    print('width', default_measure_width)
    # if cutoff >
    return round(default_measure_width, 3)


def get_measure_position(page: PageProperties, staff_prop: StaffProperties, part: Part, measure_num):
    staff_length = page.width - staff_prop.right_offset - staff_prop.left_offset
    current_offset = 0
    current_staff = 0

    for measure in part.measures:

        if measure.number == measure_num:
            print('thhs one')

        offset = current_offset % staff_length

        width = measure_width(page, staff_prop, measure)
        current_offset += width

        print(a := {
            'measure_number': measure.number,
            'origin_width': measure.display.width,
            'cutoff': page.width - staff_prop.left_offset - offset,
            'calc_width': measure_width(page, staff_prop, measure),
            'current_offset': current_offset,
            'offset_from_staff_start': offset,
            'staff': current_staff,
            'end': min(offset + width, staff_length)
        })
        yield a

        if current_offset + 400 >= staff_length:  # default_measure_width
            print('ooooooy')
            current_offset = 0
            current_staff += 1


def markup_sheet_staffs(page: PageProperties, staff_prop: StaffProperties):
    part_count_per_page = staff_prop.parts_count_per_page(page)
    staff_length = page.width - staff_prop.right_offset - staff_prop.left_offset
    for part_idx in range(part_count_per_page):
        for staff_idx in range(staff_prop.staff_count):
            staff_point = get_staff_position(page, staff_prop, part_idx, staff_idx)
            lines = staff_line(staff_point.x, staff_point.y, staff_length)
            for line in lines:
                yield line


def render(svg_drawing, objects):
    for obj in objects:
        svg_drawing.add(obj)


staff_lines = markup_sheet_staffs(current_page, current_staff_prop)
render(dwg, staff_lines)

measures_positions = get_measure_position(current_page, current_staff_prop, sheet.parts[0], 1)
lines = []
for measure in list(measures_positions):
    staff_position = get_staff_position(current_page, current_staff_prop, measure['staff'])
    print(staff_position)
    lines += [Polyline(
        points=[(staff_position.x + measure['offset_from_staff_start'], staff_position.y),
                (staff_position.x + measure['offset_from_staff_start'],
                 staff_position.y + current_staff_prop.parts_height)]
    ).stroke(
        color=svgwrite.rgb(0, 0, 0),
        width=4,
        linejoin='bevel',
    ),
        Polyline(
            points=[(staff_position.x + measure['end'], staff_position.y),
                    (staff_position.x + measure['end'],
                     staff_position.y + current_staff_prop.parts_height)]
        ).stroke(
            color=svgwrite.rgb(0, 0, 0),
            width=4,
            linejoin='bevel',
        )
    ]

render(dwg, staff_lines)
render(dwg, lines)

# notes drawing

Notes = [
    OrderedDict([('step', 'A'), ('alter', '1'), ('octave', '3')]),
    OrderedDict([('step', 'A'), ('alter', '-1'), ('octave', '3')]),
    OrderedDict([('step', 'G'), ('octave', '3')]),
    OrderedDict([('step', 'A'), ('octave', '3')]),
    OrderedDict([('step', 'B'), ('octave', '3')]),
    OrderedDict([('step', 'B'), ('octave', '4')]),
    OrderedDict([('step', 'F'), ('alter', '1'), ('octave', '5')]),
    OrderedDict([('step', 'B'), ('octave', '5')]),
    OrderedDict([('step', 'D'), ('alter', '1'), ('octave', '6')]),
    OrderedDict([('step', 'C'), ('alter', '1'), ('octave', '6')]),
    OrderedDict([('step', 'C'), ('alter', '-1'), ('octave', '2')]),
    OrderedDict([('step', 'C'), ('alter', '0'), ('octave', '3')]),
    OrderedDict([('step', 'C'), ('alter', '1'), ('octave', '3')]),
]

staff_point = get_staff_position(current_page, current_staff_prop, 0, 0)

for idx, note in enumerate(Notes):
    output_note = Note.from_note(note)

    note_orientation = get_note_orientation(output_note)
    oriented_note = [whole_note, upper_whole_note, lower_whole_note][note_orientation]

    point_y = get_note_position(current_staff_prop, 3, output_note)
    dwg.add(
        Path(d=moved_path(oriented_note, staff_point.x + 100 + 100 * idx, staff_point.y + point_y))
    )
    dwg.add(Text(
        output_note.step + str(output_note.octave) + ['', '#', 'b'][output_note.alter],
        insert=(staff_point.x + 100 + 100 * idx, staff_point.y + point_y + 60),
        fill="rgb(110,110,110)",
        style="font-size:40px; font-family:Arial; font-weight: bold",
    ))

dwg.save(pretty=True)

# with open('exhaust/music_xml_out.svg', 'r') as output:
#     print(output.read())
