from collections import namedtuple, OrderedDict
from typing import NamedTuple

import svgwrite
from svgwrite.path import Path
from svgwrite.shapes import Polyline
from svgwrite.text import Text

list_width = 2977.2
list_height = 4208.4
view_box = '{} {} {} {}'.format(0, 0, list_width, list_height)

dwg = svgwrite.Drawing('exhaust/out.svg', size=(f'{list_width}px', f'{list_height}px'), profile='tiny',
                       viewBox=view_box)

start_x = 194.232
lenght = 2835.47 - 194.232
start_y = 566.733
step_lines_y = 25
# step_staff_y = 162.5
step_staff_y = 230
step_parts_y = 500

Point = namedtuple('Point', ['x', 'y'])

Notation = namedtuple('Notation', ['staff_line_counts', 'strokes'])
StaffProperties = namedtuple('StaffProperties',
                             ['left_offset', 'right_offset', 'top_offset', 'staff_line_offset', 'staff_line_count',
                              'voice_offset', 'voice_count', 'staff_offset'])
PageProperties = namedtuple('Page', ['width', 'height'])

current_notation = Notation(
    staff_line_counts=7,
    strokes=['dotted', 'dotted', 'bold', 'dotted', 'dotted', 'bold', 'dotted']
)

current_page = PageProperties(width=2977.2, height=4208.4)
current_staff_prop = StaffProperties(
    left_offset=194.232,
    right_offset=2977.2 - 2835.47,
    top_offset=566.733,
    staff_line_offset=25,
    staff_line_count=7,
    voice_offset=80,
    voice_count=2,
    staff_offset=120
)


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


def get_staff_start_positions(page: PageProperties, staff_prop: StaffProperties):
    start_position = staff_prop.top_offset
    voice_length = (staff_prop.staff_line_count - 1) * staff_prop.staff_line_offset
    staff_length = staff_prop.voice_count * voice_length + (staff_prop.voice_count - 1) * staff_prop.voice_offset

    staff_count_per_page = int((page.height - staff_prop.top_offset) // (staff_length + staff_prop.staff_offset))
    return [
        Point(
            x=staff_prop.left_offset,
            y=start_position + part_line * (staff_length + staff_prop.staff_offset)
        )
        for part_line in range(staff_count_per_page)
    ]


print(starts := get_staff_start_positions(current_page, current_staff_prop))


def line_gen(start_x, lenght, start_y):
    lines = []
    for i in range(7):
        dotted_lines = [1, 1, 0, 1, 1, 0, 1]
        line = Polyline(
            points=[(start_x, start_y + i * step_lines_y), (start_x + lenght, start_y + i * step_lines_y)]
        ).stroke(
            color=svgwrite.rgb(0, 0, 0),
            width=2,
            linejoin='bevel',
        )
        if dotted_lines[i]:
            line.dasharray([2])
        lines.append(line)
    return lines


def add_stan(start_x, lenght, start_y):
    for line in line_gen(start_x, lenght, start_y):
        dwg.add(line)


for part_line in range(int(list_height // step_parts_y) - 1):
    for idx, staff in enumerate([0, 1]):
        add_stan(start_x, lenght, start_y + idx * step_staff_y + part_line * step_parts_y)

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


# Reader format
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
]

for idx, note in enumerate(Notes):
    output_note = Note.from_note(note)

    note_orientation = get_note_orientation(output_note)

    oriented_note = [whole_note, upper_whole_note, lower_whole_note][note_orientation]
    point_y = get_note_position(current_staff_prop, 3, output_note)
    dwg.add(
        Path(d=moved_path(oriented_note, starts[0].x + 100 + 100 * idx, starts[0].y + point_y))
    )
    dwg.add(Text(
        output_note.step + str(output_note.octave) + ['', '#', 'b'][output_note.alter],
        insert=(starts[0].x + 100 + 100 * idx, starts[0].y + point_y + 60),
        fill="rgb(110,110,110)",
        style="font-size:40px; font-family:Arial; font-weight: bold",
    ))

dwg.save(pretty=True)

with open('exhaust/out.svg', 'r') as output:
    print(output.read())
