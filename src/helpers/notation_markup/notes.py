from typing import NamedTuple

from svgwrite.path import Path

from ..path_editor import moved_path
from ...types import NotePitch, Note, Point

# (multiplier from 1 staff line, lower upper half note)
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

notes_times = {
    'whole': 1,
    'half': 2,
    'quarter': 4,
    'eighth': 8,
    '16th': 16,
    '32nd': 32,
    '64nd': 64
}


class NoteImage(NamedTuple):
    centred: str
    lower: str
    upper: str


whole_note = NoteImage(
    centred="M574.42,855.498 C572.076,855.498 570.384,856.311 569.342,857.936 C568.175,859.498 567.592,861.618 567.592,864.295 C567.592,867.358 568.404,869.993 570.029,872.201 C571.654,874.347 573.446,875.847 575.404,876.701 C577.154,877.545 579.009,877.967 580.967,877.967 C583.248,877.967 584.972,877.155 586.139,875.53 C587.243,873.894 587.795,871.774 587.795,869.17 C587.795,866.108 586.983,863.472 585.358,861.264 C583.733,859.181 581.977,857.681 580.092,856.764 C578.196,855.92 576.305,855.498 574.42,855.498 M577.748,852.967 C584.779,852.967 590.639,854.332 595.326,857.061 C600.076,859.8 602.451,863.024 602.451,866.733 C602.451,870.701 600.009,873.957 595.123,876.498 C590.238,879.165 584.446,880.498 577.748,880.498 C570.842,880.498 564.983,879.134 560.17,876.405 C555.347,873.665 552.936,870.441 552.936,866.733 C552.936,862.764 555.41,859.509 560.358,856.967 C565.243,854.3 571.04,852.967 577.748,852.967",
    lower='M48.915,13.695 C48.585,5.331 35.573,-0.403 21.812,0.292 C8.050,0.987 0.844,8.592 0.541,11.297 C0.237,14.002 0.354,13.613 7.487,13.695 C14.621,13.777 14.689,13.999 15.052,15.248 C15.453,16.628 16.076,17.892 16.920,19.040 C18.529,21.164 20.303,22.649 22.241,23.494 C23.974,24.330 25.810,24.748 27.748,24.748 C30.006,24.748 31.713,23.944 32.868,22.335 C33.961,20.716 34.224,17.541 34.224,14.964 C34.224,13.850 37.185,13.790 39.951,13.695 C44.186,13.549 48.865,13.787 48.797,13.695 M24.562,0.000 C31.522,0.000 37.322,1.351 41.962,4.053 C46.664,6.764 49.015,9.955 49.015,13.627 C49.015,17.555 46.598,20.778 41.761,23.293 C36.925,25.934 31.192,27.253 24.562,27.253 C17.725,27.253 11.926,25.903 7.161,23.201 C2.387,20.489 0.000,17.298 0.000,13.627 C0.000,9.698 2.449,6.476 7.347,3.960 C12.183,1.320 17.921,0.000 24.562,0.000',
    upper='M21.267,2.505 C18.947,2.505 17.272,3.310 16.240,4.919 C15.085,6.465 14.508,8.564 14.508,11.214 C14.508,11.941 13.797,13.802 6.504,13.695 C3.597,13.652 -3.277,13.444 3.094,20.015 C5.981,22.992 11.341,25.335 16.458,26.325 C21.277,27.258 25.937,26.924 26.334,26.926 C33.156,26.963 42.701,23.404 45.475,20.543 C48.249,17.681 47.591,18.312 48.564,16.042 C48.779,15.543 49.008,14.162 48.033,13.936 C44.580,13.136 34.880,14.354 34.573,13.345 C34.171,12.026 32.907,9.317 32.095,8.213 C30.486,6.151 28.748,4.667 26.882,3.759 C25.005,2.923 23.133,2.505 21.267,2.505 M24.562,0.000 C31.522,0.000 37.322,1.351 41.962,4.053 C46.664,6.764 49.015,9.955 49.015,13.627 C49.015,17.555 46.598,20.778 41.761,23.293 C36.925,25.934 31.192,27.253 24.562,27.253 C17.725,27.253 11.926,25.903 7.161,23.201 C2.387,20.489 0.000,17.298 0.000,13.627 C0.000,9.698 2.449,6.476 7.347,3.960 C12.183,1.320 17.921,0.000 24.562,0.000'
)

# TODO make partial note filled draft
note_signs = {
    'whole': whole_note
}


def get_note_name(note_pitch: NotePitch):
    return note_pitch.step + ['', '#', 'b'][note_pitch.alter]


def get_note_position(staff_prop, staff_base_octave, note: Note) -> int:
    last_line = (staff_prop.staff_line_count - 1) * staff_prop.staff_line_offset

    octave_offset = staff_prop.staff_line_offset * 3  # 2 lines 3 spaces divides 1 octave
    note_octave_offset = (note.octave - staff_base_octave) * octave_offset

    note_name = note.step + ['', '#', 'b'][note.alter]
    note_grade, note_orientation = notes_offsets[note_name]

    note_offset = note_grade * staff_prop.staff_line_offset

    return last_line - note_octave_offset - note_offset


def get_note_sign(note: Note):
    note_name = note.pitch.step + ['', '#', 'b'][note.pitch.alter]
    note_grade, note_orientation = notes_offsets[note_name]

    if note.type not in note_signs:
        note_sign = whole_note
    else:
        note_sign = note_signs[note.type]
    return getattr(note_sign, ['centred', 'lower', 'upper'][note_orientation])


def markup_note(sign, note_position: Point):
    return Path(d=moved_path(sign, note_position.x, note_position.y))

    #
    # output_note = Note.from_note(note)
    #
    # note_orientation = get_note_orientation(output_note)
    # oriented_note = [whole_note, upper_whole_note, lower_whole_note][note_orientation]
    #
    # point_y = get_note_position(current_staff_prop, 3, output_note)
    # dwg.add(
    #     Path(d=moved_path(oriented_note, staff_point.x + 100 + 100 * idx, staff_point.y + point_y))
    # )
    # dwg.add(Text(
    #     output_note.step + str(output_note.octave) + ['', '#', 'b'][output_note.alter],
    #     insert=(staff_point.x + 100 + 100 * idx, staff_point.y + point_y + 60),
    #     fill="rgb(110,110,110)",
    #     style="font-size:40px; font-family:Arial; font-weight: bold",
    # ))
