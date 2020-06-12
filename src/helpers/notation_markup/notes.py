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

rest_signs = {
    'whole': "M622.095,1407.36 L586.548,1407.36 C585.892,1407.36 585.564,1407.04 585.564,1406.39 L585.564,1392.72 C585.564,1392.06 585.892,1391.73 586.548,1391.73 L622.095,1391.73 C622.741,1391.73 623.064,1392.06 623.064,1392.72 L623.064,1406.39 C623.064,1407.04 622.741,1407.36 622.095,1407.36",
    'half': "M1073.2,1049.38 C1073.2,1048.2 1073.86,1046.9 1075.17,1045.47 C1076.14,1044.43 1077.57,1043.19 1079.47,1041.75 C1080.9,1040.78 1082.29,1039.32 1083.66,1037.36 C1084.96,1035.48 1085.61,1033.42 1085.61,1031.21 C1085.61,1028.6 1084.77,1026.29 1083.08,1024.28 L1079.56,1020.08 C1079.3,1019.82 1079.17,1019.49 1079.17,1019.1 C1079.17,1018.71 1079.36,1018.36 1079.75,1018.03 C1080.21,1017.7 1080.6,1017.53 1080.92,1017.53 C1081.38,1017.53 1081.74,1017.73 1082,1018.13 L1097.14,1036.1 C1097.79,1036.94 1098.11,1037.78 1098.11,1038.63 C1098.11,1039.8 1097.46,1041.11 1096.16,1042.53 C1095.31,1043.45 1093.92,1044.69 1091.97,1046.25 C1090.47,1047.16 1089.04,1048.62 1087.67,1050.64 C1086.37,1052.53 1085.72,1054.58 1085.72,1056.8 C1085.72,1059.54 1086.5,1061.85 1088.06,1063.74 L1096.45,1073.6 C1096.65,1073.79 1096.81,1074.12 1096.94,1074.58 C1096.94,1075.03 1096.78,1075.42 1096.45,1075.75 C1096,1076.08 1095.6,1076.24 1095.28,1076.24 C1095.16,1076.24 1094.64,1075.88 1093.72,1075.16 C1092.74,1074.38 1091.44,1073.63 1089.81,1072.91 C1087.99,1072.2 1086.2,1071.85 1084.44,1071.85 C1082.81,1071.85 1081.48,1072.3 1080.44,1073.21 C1079.53,1074.12 1079.08,1075.88 1079.08,1078.49 C1079.08,1082.46 1080.02,1085.58 1081.91,1087.86 C1082.1,1088.12 1082.14,1088.45 1082,1088.83 C1081.88,1089.09 1081.65,1089.22 1081.31,1089.22 C1080.86,1089.22 1079.86,1088.05 1078.3,1085.71 C1076.66,1083.24 1075.13,1080.4 1073.7,1077.21 C1072.2,1073.82 1071.45,1071.02 1071.45,1068.81 C1071.45,1066.01 1072.79,1064.61 1075.45,1064.61 C1078.52,1064.61 1082.49,1065.65 1087.38,1067.74 L1074.19,1051.91 C1073.53,1051.06 1073.2,1050.22 1073.2,1049.38",
    'quarter': "M1263.47,1036.67 C1265.36,1036.67 1266.79,1037.2 1267.77,1038.24 C1268.75,1039.41 1269.27,1040.52 1269.33,1041.56 C1269.47,1042.54 1269.8,1043.65 1270.32,1044.88 C1270.9,1045.92 1271.65,1046.44 1272.55,1046.44 C1273.27,1046.44 1274.35,1045.63 1275.79,1044 C1277.09,1042.58 1278.03,1041.3 1278.62,1040.19 C1278.94,1039.54 1279.39,1039.22 1279.97,1039.22 L1280.08,1039.22 C1280.73,1039.28 1281.18,1039.61 1281.44,1040.19 L1269.15,1082.19 C1268.49,1082.85 1267.58,1083.17 1266.4,1083.17 C1265.23,1083.17 1264.32,1082.85 1263.68,1082.19 L1275.4,1049.56 C1271.23,1051.06 1267.71,1051.81 1264.85,1051.81 C1262.51,1051.81 1260.49,1051.06 1258.79,1049.56 C1257.03,1048.14 1256.15,1046.25 1256.15,1043.91 C1256.15,1041.89 1256.87,1040.2 1258.3,1038.83 C1259.73,1037.39 1261.45,1036.67 1263.47,1036.67",
    'eighth': "M1412.45,1036.67 C1414.41,1036.67 1415.81,1037.2 1416.65,1038.24 C1417.56,1039.35 1418.11,1040.46 1418.31,1041.56 C1418.37,1042.67 1418.7,1043.77 1419.3,1044.88 C1419.68,1045.92 1420.39,1046.44 1421.44,1046.44 C1422.09,1046.44 1423.07,1045.66 1424.37,1044.1 C1425.86,1042.27 1426.81,1040.97 1427.2,1040.19 C1427.52,1039.54 1427.98,1039.22 1428.56,1039.22 C1428.56,1039.22 1428.6,1039.22 1428.67,1039.22 C1429.25,1039.28 1429.68,1039.61 1429.94,1040.19 L1412.06,1107.19 C1411.42,1107.85 1410.51,1108.17 1409.33,1108.17 C1408.16,1108.17 1407.25,1107.85 1406.59,1107.19 L1416.65,1074.47 C1412.29,1076.03 1408.74,1076.81 1406.01,1076.81 C1403.67,1076.81 1401.65,1076.07 1399.95,1074.58 C1398.19,1073.14 1397.31,1071.25 1397.31,1068.91 C1397.31,1066.89 1397.99,1065.2 1399.36,1063.83 C1400.8,1062.4 1402.52,1061.69 1404.55,1061.69 C1406.49,1061.69 1407.89,1062.21 1408.75,1063.25 C1409.72,1064.36 1410.3,1065.46 1410.5,1066.56 C1410.7,1067.87 1411.02,1068.98 1411.48,1069.89 C1411.93,1070.93 1412.64,1071.46 1413.62,1071.46 C1414.4,1071.46 1415.51,1070.54 1416.95,1068.72 C1418.44,1067.02 1419.35,1065.68 1419.69,1064.71 L1424.26,1049.56 C1420.1,1051.06 1416.62,1051.81 1413.83,1051.81 C1411.48,1051.81 1409.46,1051.06 1407.76,1049.56 C1406,1048.14 1405.12,1046.25 1405.12,1043.91 C1405.12,1041.89 1405.84,1040.2 1407.28,1038.83 C1408.71,1037.39 1410.43,1036.67 1412.45,1036.67",
    '16th': "M1519.76,1011.67 C1521.64,1011.67 1523.08,1012.2 1524.06,1013.24 C1525.02,1014.41 1525.55,1015.52 1525.62,1016.56 C1525.74,1017.54 1526.07,1018.65 1526.59,1019.88 C1527.17,1020.92 1527.92,1021.44 1528.84,1021.44 C1529.42,1021.44 1530.36,1020.66 1531.66,1019.1 C1532.84,1017.41 1533.62,1016.11 1534.01,1015.19 C1534.33,1014.54 1534.79,1014.22 1535.38,1014.22 L1535.48,1014.22 C1536.12,1014.28 1536.58,1014.61 1536.84,1015.19 L1515.26,1107.19 C1514.61,1107.85 1513.67,1108.17 1512.43,1108.17 C1511.33,1108.17 1510.41,1107.85 1509.7,1107.19 L1518.29,1074.47 C1514.19,1076.03 1510.6,1076.81 1507.54,1076.81 C1505.26,1076.81 1503.21,1076.07 1501.38,1074.58 C1499.7,1073.08 1498.85,1071.19 1498.85,1068.91 C1498.85,1066.89 1499.57,1065.2 1500.99,1063.83 C1502.37,1062.4 1504.03,1061.69 1505.98,1061.69 C1507.87,1061.69 1509.31,1062.21 1510.27,1063.25 C1511.32,1064.36 1511.87,1065.46 1511.95,1066.56 C1512.13,1067.87 1512.46,1068.98 1512.91,1069.89 C1513.37,1070.93 1514.12,1071.46 1515.16,1071.46 C1515.88,1071.46 1516.99,1070.54 1518.48,1068.72 C1519.85,1066.9 1520.7,1065.47 1521.02,1064.42 L1524.93,1049.47 C1520.57,1051.03 1517.02,1051.81 1514.29,1051.81 C1511.95,1051.81 1509.93,1051.06 1508.23,1049.56 C1506.47,1048.14 1505.59,1046.25 1505.59,1043.91 C1505.59,1041.89 1506.31,1040.2 1507.74,1038.83 C1509.17,1037.39 1510.89,1036.67 1512.91,1036.67 C1514.87,1036.67 1516.27,1037.2 1517.12,1038.24 C1518.02,1039.35 1518.58,1040.46 1518.77,1041.56 C1518.97,1042.87 1519.3,1043.97 1519.76,1044.88 C1520.21,1045.92 1520.92,1046.44 1521.9,1046.44 C1522.62,1046.44 1523.66,1045.53 1525.02,1043.71 C1526.39,1042.08 1527.24,1040.75 1527.57,1039.71 L1531.57,1024.56 C1527.47,1026.06 1524.01,1026.81 1521.21,1026.81 C1518.94,1026.81 1516.89,1026.06 1515.07,1024.56 C1513.37,1023.08 1512.52,1021.19 1512.52,1018.91 C1512.52,1016.89 1513.24,1015.2 1514.68,1013.83 C1516.05,1012.39 1517.74,1011.67 1519.76,1011.67",
    '32nd': "M1584.99,1011.67 C1586.87,1011.67 1588.31,1012.2 1589.29,1013.24 C1590.26,1014.41 1590.78,1015.52 1590.85,1016.56 C1590.97,1017.54 1591.3,1018.65 1591.82,1019.88 C1592.4,1020.92 1593.15,1021.44 1594.07,1021.44 C1594.65,1021.44 1595.59,1020.66 1596.9,1019.1 C1598.07,1017.41 1598.85,1016.11 1599.24,1015.19 C1599.56,1014.54 1600.02,1014.22 1600.61,1014.22 L1600.71,1014.22 C1601.35,1014.28 1601.81,1014.61 1602.07,1015.19 L1580.49,1107.19 C1579.84,1107.85 1578.9,1108.17 1577.66,1108.17 C1576.56,1108.17 1575.65,1107.85 1574.93,1107.19 L1583.52,1074.47 C1579.42,1076.03 1575.83,1076.81 1572.77,1076.81 C1570.49,1076.81 1568.44,1076.07 1566.61,1074.58 C1564.93,1073.08 1564.08,1071.19 1564.08,1068.91 C1564.08,1066.89 1564.8,1065.2 1566.22,1063.83 C1567.6,1062.4 1569.26,1061.69 1571.21,1061.69 C1573.1,1061.69 1574.54,1062.21 1575.51,1063.25 C1576.55,1064.36 1577.1,1065.46 1577.18,1066.56 C1577.36,1067.87 1577.69,1068.98 1578.15,1069.89 C1578.6,1070.93 1579.35,1071.46 1580.4,1071.46 C1581.11,1071.46 1582.22,1070.54 1583.71,1068.72 C1585.08,1066.9 1585.93,1065.47 1586.26,1064.42 L1590.16,1049.47 C1585.8,1051.03 1582.25,1051.81 1579.52,1051.81 C1577.18,1051.81 1575.16,1051.06 1573.46,1049.56 C1571.7,1048.14 1570.82,1046.25 1570.82,1043.91 C1570.82,1041.89 1571.54,1040.2 1572.97,1038.83 C1574.4,1037.39 1576.12,1036.67 1578.15,1036.67 C1580.1,1036.67 1581.51,1037.2 1582.35,1038.24 C1583.26,1039.35 1583.81,1040.46 1584.01,1041.56 C1584.2,1042.87 1584.53,1043.97 1584.99,1044.88 C1585.44,1045.92 1586.15,1046.44 1587.13,1046.44 C1587.85,1046.44 1588.89,1045.53 1590.26,1043.71 C1591.62,1042.08 1592.47,1040.75 1592.8,1039.71 L1596.8,1024.56 C1592.7,1026.06 1589.24,1026.81 1586.44,1026.81 C1584.17,1026.81 1582.12,1026.06 1580.3,1024.56 C1578.6,1023.08 1577.76,1021.19 1577.76,1018.91 C1577.76,1016.89 1578.47,1015.2 1579.91,1013.83 C1581.28,1012.39 1582.97,1011.67 1584.99,1011.67",
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


def get_rest_sign(note: Note):
    if note.type not in rest_signs:
        return rest_signs['whole']
    else:
        return rest_signs[note.type]


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
