from collections import namedtuple, OrderedDict
from typing import NamedTuple

import svgwrite
from svgwrite.path import Path
from svgwrite.shapes import Polyline
from svgwrite.text import Text


def make_svg():
    return ('')


# < svg
# viewBox = "0 0 2977.2 4208.4"
# xmlns = "http://www.w3.org/2000/svg"
# xmlns: xlink = "http://www.w3.org/1999/xlink"
# version = "1.2"
# baseProfile = "tiny" >


# < polyline
# class ="StaffLines"
# fill="none"
# stroke="#000000"
# stroke-width="2.00"
# stroke-linejoin="bevel"
# points="194.232,566.733 2835.47,566.733" / >

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
    point_y = get_note_position(current_staff_prop, 3, output_note)
    # TODO do a half note with clipping defs https://developer.mozilla.org/ru/docs/Web/SVG/Tutorial/Clipping_and_masking
    dwg.add(Path(d=moved_path(whole_note, starts[0].x + 100 + 100 * idx, starts[0].y + point_y)))
    dwg.add(Text(
        output_note.step + str(output_note.octave) + ['', '#', 'b'][output_note.alter],
        insert=(starts[0].x + 100 + 100 * idx, starts[0].y + point_y + 60),
        fill="rgb(110,110,110)",
        style="font-size:40px; font-family:Arial; font-weight: bold",
    ))

dwg.save(pretty=True)

with open('exhaust/out.svg', 'r') as output:
    print(output.read())
