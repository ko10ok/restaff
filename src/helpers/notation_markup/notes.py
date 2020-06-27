from typing import NamedTuple

import svgwrite
from svgwrite.path import Path
from svgwrite.shapes import Circle, Polyline
from svgwrite.text import Text

from src.helpers.svg_drawing.path_editor import moved_path
from ...types import NotePitch, Note, Point, StaffProperties

# (multiplier from 1 staff line, lower upper half note)
notes_offsets = {
    'C': (0.5, 0),
    'C#': (1, -1),
    'Db': (1, -1),
    'D': (1, 0),
    'D#': (1, 1),
    'Eb': (1, 1),
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
    centred='M-3.270,-11.230 C-5.620,-11.230 -7.310,-10.420 -8.350,-8.800 C-9.520,-7.230 -10.100,-5.110 -10.100,-2.440 C-10.100,0.630 -9.290,3.260 -7.660,5.470 C-6.040,7.610 -4.250,9.110 -2.290,9.970 C-0.540,10.810 1.320,11.230 3.270,11.230 C5.550,11.230 7.280,10.420 8.440,8.800 C9.550,7.160 10.100,5.040 10.100,2.440 C10.100,-0.620 9.290,-3.260 7.660,-5.470 C6.040,-7.550 4.280,-9.050 2.400,-9.970 C0.500,-10.810 -1.390,-11.230 -3.270,-11.230 M0.050,-13.760 C7.080,-13.760 12.940,-12.400 17.630,-9.670 C22.380,-6.930 24.760,-3.710 24.760,0.000 C24.760,3.970 22.310,7.220 17.430,9.760 C12.540,12.430 6.750,13.760 0.050,13.760 C-6.850,13.760 -12.710,12.400 -17.520,9.670 C-22.340,6.930 -24.760,3.710 -24.760,0.000 C-24.760,-3.970 -22.280,-7.220 -17.330,-9.760 C-12.450,-12.430 -6.650,-13.760 0.050,-13.760',
    upper='M-9.910,0.000 C-10.330,-2.570 -10.150,-4.890 -9.390,-6.950 C-8.960,-8.100 -7.670,-10.620 -4.710,-11.110 C-3.250,-11.350 -0.540,-11.220 1.790,-10.240 C4.160,-9.250 6.150,-7.310 6.910,-6.450 C8.510,-4.650 9.520,-2.500 9.950,0.000 L24.760,0.000 C24.690,-3.250 22.630,-6.290 18.590,-9.130 C14.550,-11.970 8.360,-13.520 0.010,-13.760 C-2.770,-13.770 -5.390,-13.530 -7.850,-13.050 C-12.050,-12.240 -15.810,-10.730 -18.450,-9.130 C-22.640,-6.600 -24.740,-3.560 -24.740,0.000 L-9.910,0.000',
    lower='M9.920,0.000 C10.340,2.570 10.170,4.890 9.400,6.950 C8.980,8.100 7.680,10.620 4.730,11.110 C3.260,11.350 0.550,11.220 -1.770,10.240 C-4.150,9.250 -6.130,7.310 -6.900,6.450 C-8.500,4.650 -9.510,2.500 -9.930,0.000 L-24.740,0.000 C-24.670,3.250 -22.610,6.290 -18.570,9.130 C-14.530,11.970 -8.340,13.520 0.010,13.760 C2.780,13.770 5.400,13.530 7.870,13.050 C12.070,12.240 15.830,10.730 18.470,9.130 C22.660,6.600 24.750,3.560 24.760,0.000 L9.920,0.000',
)

partial_note = NoteImage(
    centred='M0.060,-13.760 C7.090,-13.760 12.950,-12.400 17.630,-9.670 C22.380,-6.930 24.760,-3.710 24.760,0.000 C24.760,3.970 22.310,7.220 17.430,9.760 C12.550,12.430 6.760,13.760 0.060,13.760 C-6.840,13.760 -12.700,12.400 -17.510,9.670 C-22.330,6.930 -24.740,3.710 -24.740,0.000 C-24.740,-3.970 -22.270,-7.220 -17.320,-9.760 C-12.440,-12.430 -6.640,-13.760 0.060,-13.760',
    upper='M-9.910,0.000 L9.950,0.000 L24.760,0.000 C24.690,-3.250 22.630,-6.290 18.590,-9.130 C14.550,-11.970 8.360,-13.520 0.010,-13.760 C-2.770,-13.770 -5.390,-13.530 -7.850,-13.050 C-12.050,-12.240 -15.810,-10.730 -18.450,-9.130 C-22.640,-6.600 -24.740,-3.560 -24.740,0.000 L-9.910,0.000',
    lower='M9.920,0.000 L-9.930,0.000 L-24.740,0.000 C-24.670,3.250 -22.610,6.290 -18.570,9.130 C-14.530,11.970 -8.340,13.520 0.010,13.760 C2.780,13.770 5.400,13.530 7.870,13.050 C12.070,12.240 15.830,10.730 18.470,9.130 C22.660,6.600 24.750,3.560 24.760,0.000 L9.920,0.000',
)

# TODO make partial note filled draft
note_signs = {
    'whole': whole_note,
    'half': whole_note,
    'partial_note': partial_note
}

rest_signs = {
    'whole': 'M17.781,7.815 L-17.766,7.815 C-18.422,7.815 -18.750,7.495 -18.750,6.845 L-18.750,-6.825 C-18.750,-7.485 -18.422,-7.815 -17.766,-7.815 L17.781,-7.815 C18.427,-7.815 18.750,-7.485 18.750,-6.825 L18.750,6.845 C18.750,7.495 18.427,7.815 17.781,7.815',
    'half': 'M-11.580,-3.995 C-11.580,-5.175 -10.920,-6.475 -9.610,-7.905 C-8.640,-8.945 -7.210,-10.185 -5.310,-11.625 C-3.880,-12.595 -2.490,-14.055 -1.120,-16.015 C0.180,-17.895 0.830,-19.955 0.830,-22.165 C0.830,-24.775 -0.010,-27.085 -1.700,-29.095 L-5.220,-33.295 C-5.480,-33.555 -5.610,-33.885 -5.610,-34.275 S-5.420,-35.015 -5.030,-35.345 C-4.570,-35.675 -4.180,-35.845 -3.860,-35.845 C-3.400,-35.845 -3.040,-35.645 -2.780,-35.245 L12.360,-17.275 C13.010,-16.435 13.330,-15.595 13.330,-14.745 C13.330,-13.575 12.680,-12.265 11.380,-10.845 C10.530,-9.925 9.140,-8.685 7.190,-7.125 C5.690,-6.215 4.260,-4.755 2.890,-2.735 C1.590,-0.845 0.940,1.205 0.940,3.425 C0.940,6.165 1.720,8.475 3.280,10.365 L11.670,20.225 C11.870,20.415 12.030,20.745 12.160,21.205 C12.160,21.655 12.000,22.045 11.670,22.375 C11.220,22.705 10.820,22.865 10.500,22.865 C10.380,22.865 9.860,22.505 8.940,21.785 C7.960,21.005 6.660,20.255 5.030,19.535 C3.210,18.825 1.420,18.475 -0.340,18.475 C-1.970,18.475 -3.300,18.925 -4.340,19.835 C-5.250,20.745 -5.700,22.505 -5.700,25.115 C-5.700,29.085 -4.760,32.205 -2.870,34.485 C-2.680,34.745 -2.640,35.075 -2.780,35.455 C-2.900,35.715 -3.130,35.845 -3.470,35.845 C-3.920,35.845 -4.920,34.675 -6.480,32.335 C-8.120,29.865 -9.650,27.025 -11.080,23.835 C-12.580,20.445 -13.330,17.645 -13.330,15.435 C-13.330,12.635 -11.990,11.235 -9.330,11.235 C-6.260,11.235 -2.290,12.275 2.600,14.365 L-10.590,-1.465 C-11.250,-2.315 -11.580,-3.155 -11.580,-3.995',
    'quarter': 'M-5.325,-23.250 C-3.435,-23.250 -2.005,-22.720 -1.025,-21.680 C-0.045,-20.510 0.475,-19.400 0.535,-18.360 C0.675,-17.380 1.005,-16.270 1.525,-15.040 C2.105,-14.000 2.855,-13.480 3.755,-13.480 C4.475,-13.480 5.555,-14.290 6.995,-15.920 C8.295,-17.340 9.235,-18.620 9.825,-19.730 C10.145,-20.380 10.595,-20.700 11.175,-20.700 L11.285,-20.700 C11.935,-20.640 12.385,-20.310 12.645,-19.730 L0.355,22.270 C-0.305,22.930 -1.215,23.250 -2.395,23.250 C-3.565,23.250 -4.475,22.930 -5.115,22.270 L6.605,-10.360 C2.435,-8.860 -1.085,-8.110 -3.945,-8.110 C-6.285,-8.110 -8.305,-8.860 -10.005,-10.360 C-11.765,-11.780 -12.645,-13.670 -12.645,-16.010 C-12.645,-18.030 -11.925,-19.720 -10.495,-21.090 C-9.065,-22.530 -7.345,-23.250 -5.325,-23.250',
    'eighth': 'M-1.175,-35.750 C0.785,-35.750 2.185,-35.220 3.025,-34.180 C3.935,-33.070 4.485,-31.960 4.685,-30.860 C4.745,-29.750 5.075,-28.650 5.675,-27.540 C6.055,-26.500 6.765,-25.980 7.815,-25.980 C8.465,-25.980 9.445,-26.760 10.745,-28.320 C12.235,-30.150 13.185,-31.450 13.575,-32.230 C13.895,-32.880 14.355,-33.200 14.935,-33.200 C14.935,-33.200 14.975,-33.200 15.045,-33.200 C15.625,-33.140 16.055,-32.810 16.315,-32.230 L-1.565,34.770 C-2.205,35.430 -3.115,35.750 -4.295,35.750 C-5.465,35.750 -6.375,35.430 -7.035,34.770 L3.025,2.050 C-1.335,3.610 -4.885,4.390 -7.615,4.390 C-9.955,4.390 -11.975,3.650 -13.675,2.160 C-15.435,0.720 -16.315,-1.170 -16.315,-3.510 C-16.315,-5.530 -15.635,-7.220 -14.265,-8.590 C-12.825,-10.020 -11.105,-10.730 -9.075,-10.730 C-7.135,-10.730 -5.735,-10.210 -4.875,-9.170 C-3.905,-8.060 -3.325,-6.960 -3.125,-5.860 C-2.925,-4.550 -2.605,-3.440 -2.145,-2.530 C-1.695,-1.490 -0.985,-0.960 -0.005,-0.960 C0.775,-0.960 1.885,-1.880 3.325,-3.700 C4.815,-5.400 5.725,-6.740 6.065,-7.710 L10.635,-22.860 C6.475,-21.360 2.995,-20.610 0.205,-20.610 C-2.145,-20.610 -4.165,-21.360 -5.865,-22.860 C-7.625,-24.280 -8.505,-26.170 -8.505,-28.510 C-8.505,-30.530 -7.785,-32.220 -6.345,-33.590 C-4.915,-35.030 -3.195,-35.750 -1.175,-35.750',
    '16th': 'M1.915,-48.250 C3.795,-48.250 5.235,-47.720 6.215,-46.680 C7.175,-45.510 7.705,-44.400 7.775,-43.360 C7.895,-42.380 8.225,-41.270 8.745,-40.040 C9.325,-39.000 10.075,-38.480 10.995,-38.480 C11.575,-38.480 12.515,-39.260 13.815,-40.820 C14.995,-42.510 15.775,-43.810 16.165,-44.730 C16.485,-45.380 16.945,-45.700 17.535,-45.700 L17.635,-45.700 C18.275,-45.640 18.735,-45.310 18.995,-44.730 L-2.585,47.270 C-3.235,47.930 -4.175,48.250 -5.415,48.250 C-6.515,48.250 -7.435,47.930 -8.145,47.270 L0.445,14.550 C-3.655,16.110 -7.245,16.890 -10.305,16.890 C-12.585,16.890 -14.635,16.150 -16.465,14.660 C-18.145,13.160 -18.995,11.270 -18.995,8.990 C-18.995,6.970 -18.275,5.280 -16.855,3.910 C-15.475,2.480 -13.815,1.770 -11.865,1.770 C-9.975,1.770 -8.535,2.290 -7.575,3.330 C-6.525,4.440 -5.975,5.540 -5.895,6.640 C-5.715,7.950 -5.385,9.060 -4.935,9.970 C-4.475,11.010 -3.725,11.540 -2.685,11.540 C-1.965,11.540 -0.855,10.620 0.635,8.800 C2.005,6.980 2.855,5.550 3.175,4.500 L7.085,-10.450 C2.725,-8.890 -0.825,-8.110 -3.555,-8.110 C-5.895,-8.110 -7.915,-8.860 -9.615,-10.360 C-11.375,-11.780 -12.255,-13.670 -12.255,-16.010 C-12.255,-18.030 -11.535,-19.720 -10.105,-21.090 C-8.675,-22.530 -6.955,-23.250 -4.935,-23.250 C-2.975,-23.250 -1.575,-22.720 -0.725,-21.680 C0.175,-20.570 0.735,-19.460 0.925,-18.360 C1.125,-17.050 1.455,-15.950 1.915,-15.040 C2.365,-14.000 3.075,-13.480 4.055,-13.480 C4.775,-13.480 5.815,-14.390 7.175,-16.210 C8.545,-17.840 9.395,-19.170 9.725,-20.210 L13.725,-35.360 C9.625,-33.860 6.165,-33.110 3.365,-33.110 C1.095,-33.110 -0.955,-33.860 -2.775,-35.360 C-4.475,-36.840 -5.325,-38.730 -5.325,-41.010 C-5.325,-43.030 -4.605,-44.720 -3.165,-46.090 C-1.795,-47.530 -0.105,-48.250 1.915,-48.250',
    '32nd': 'M1.915,-48.250 C3.795,-48.250 5.235,-47.720 6.215,-46.680 C7.185,-45.510 7.705,-44.400 7.775,-43.360 C7.895,-42.380 8.225,-41.270 8.745,-40.040 C9.325,-39.000 10.075,-38.480 10.995,-38.480 C11.575,-38.480 12.515,-39.260 13.825,-40.820 C14.995,-42.510 15.775,-43.810 16.165,-44.730 C16.485,-45.380 16.945,-45.700 17.535,-45.700 L17.635,-45.700 C18.275,-45.640 18.735,-45.310 18.995,-44.730 L-2.585,47.270 C-3.235,47.930 -4.175,48.250 -5.415,48.250 C-6.515,48.250 -7.425,47.930 -8.145,47.270 L0.445,14.550 C-3.655,16.110 -7.245,16.890 -10.305,16.890 C-12.585,16.890 -14.635,16.150 -16.465,14.660 C-18.145,13.160 -18.995,11.270 -18.995,8.990 C-18.995,6.970 -18.275,5.280 -16.855,3.910 C-15.475,2.480 -13.815,1.770 -11.865,1.770 C-9.975,1.770 -8.535,2.290 -7.565,3.330 C-6.525,4.440 -5.975,5.540 -5.895,6.640 C-5.715,7.950 -5.385,9.060 -4.925,9.970 C-4.475,11.010 -3.725,11.540 -2.675,11.540 C-1.965,11.540 -0.855,10.620 0.635,8.800 C2.005,6.980 2.855,5.550 3.185,4.500 L7.085,-10.450 C2.725,-8.890 -0.825,-8.110 -3.555,-8.110 C-5.895,-8.110 -7.915,-8.860 -9.615,-10.360 C-11.375,-11.780 -12.255,-13.670 -12.255,-16.010 C-12.255,-18.030 -11.535,-19.720 -10.105,-21.090 C-8.675,-22.530 -6.955,-23.250 -4.925,-23.250 C-2.975,-23.250 -1.565,-22.720 -0.725,-21.680 C0.185,-20.570 0.735,-19.460 0.935,-18.360 C1.125,-17.050 1.455,-15.950 1.915,-15.040 C2.365,-14.000 3.075,-13.480 4.055,-13.480 C4.775,-13.480 5.815,-14.390 7.185,-16.210 C8.545,-17.840 9.395,-19.170 9.725,-20.210 L13.725,-35.360 C9.625,-33.860 6.165,-33.110 3.365,-33.110 C1.095,-33.110 -0.955,-33.860 -2.775,-35.360 C-4.475,-36.840 -5.315,-38.730 -5.315,-41.010 C-5.315,-43.030 -4.605,-44.720 -3.165,-46.090 C-1.795,-47.530 -0.105,-48.250 1.915,-48.250',
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

    note_type = note_signs.get(note.type, note_signs['partial_note'])
    image_orientation = ['centred', 'upper', 'lower'][note_orientation]
    return getattr(note_type, image_orientation)


def get_rest_sign(note: Note):
    if note.type not in rest_signs:
        return rest_signs['whole']
    else:
        return rest_signs[note.type]


def markup_note_body(sign, note_position: Point):
    return Path(d=moved_path(sign, note_position.x, note_position.y))


def markup_note(staff_prop: StaffProperties, staff_start_position, staff_octave, horizontal_note_position, chord_offset,
                chord_stepout, note, chords_notes):
    not_chord_note = note.id not in chords_notes
    chord_note = note.id in chords_notes
    last_chord_note = chord_note and chords_notes.get(note.id, {}).last

    objects = []

    note_offset = get_note_position(staff_prop, staff_octave, note.pitch)

    vertical_note_position = staff_start_position + note_offset

    note_sign = get_note_sign(note)
    objects += [markup_note_body(
        note_sign,
        Point(
            horizontal_note_position + chord_offset,
            vertical_note_position
        )
    )]

    if note.dot:
        addition = note_offset % staff_prop.staff_line_offset - staff_prop.staff_line_offset / 2
        objects += [
            Circle(
                center=(
                    horizontal_note_position + 35 + chord_offset,
                    vertical_note_position + addition
                ),
                r=4)
        ]

    if note.time_modification:
        objects += [Text(
            str(note.time_modification['actual-notes']),
            insert=(
                horizontal_note_position,
                staff_start_position - staff_prop.staff_offset // 2),
            fill="rgb(110,110,110)",
            style="font-size:15px; font-family:Arial",
        )]

    objects += []
    flag = {
        'whole': (0, 0),
        'half': (1, 0),
        'quarter': (1, 0),
        'eighth': (1, 1),
        '16th': (1, 2),
        '32nd': (1, 3),
    }
    stem, beams = flag[note.type]
    if stem:
        half_note_offset = 17.5
        stem_lenght = 80
        objects += [
            Polyline(
                points=[(horizontal_note_position + half_note_offset, vertical_note_position),
                        (horizontal_note_position + half_note_offset,
                         vertical_note_position - stem_lenght)]
            ).stroke(
                color=svgwrite.rgb(0, 0, 0),
                width=3,
                linejoin='bevel',
            )
        ]

        # TODO extract beam|stemm drawing into note groups drawing
        # print(f'{not_chord_note=} {last_chord_note=} {first_chord_note=}')
        if not_chord_note or last_chord_note:
            for idx in range(beams):
                half_note_offset = 17.5
                beam_length = 13
                beam_offset = idx * 15
                objects += [
                    Polyline(
                        points=[(horizontal_note_position + half_note_offset,
                                 vertical_note_position - stem_lenght + beam_offset + 10),
                                (horizontal_note_position + half_note_offset + beam_length,
                                 vertical_note_position - stem_lenght + beam_offset + 10 + 30)]
                    ).stroke(
                        color=svgwrite.rgb(0, 0, 0),
                        width=3,
                        linejoin='bevel',
                    )
                ]

    return objects


def calc_note_length(measure, time, note):
    note_lenght = (measure.end - measure.start - measure.left_offset - measure.right_offset) \
                  / (notes_times[note.type] if note.type else notes_times['whole'])

    note_lenght *= (time.beat_type / time.beats)

    if note.dot:
        note_lenght += note_lenght / 2

    if note.time_modification:
        print(f'{note.time_modification=}')
        actual = note.time_modification['actual-notes']
        normal = note.time_modification['normal-notes']
        note_lenght_multiplier = int(normal) / int(actual)
        print(f'{note.time_modification} {note_lenght_multiplier}')
        note_lenght = note_lenght * note_lenght_multiplier

    return note_lenght
