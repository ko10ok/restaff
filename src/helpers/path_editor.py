import re

from svg.path import parse_path
from svgwrite.path import Path
from svgwrite.text import Text


# TODO mby switch to svg.path lib for moving path


def break_into_point_array(d: str):
    path = parse_path(d)
    despaced = re.sub(r'([A-Z]) ([-\d])', '\\1\\2', path.d())
    str_points = despaced.split(' ')
    points = [
        (action := b[0], start_from := action.isalpha(), pair := b.split(','), float(pair[0][start_from:]),
         float(pair[1]))
        for b in str_points if b[0] != 'Z'
    ]
    return points


def moved_to_zero_path(d):
    points = break_into_point_array(d)
    min_x = (min([point[3] for point in points]) + max([point[3] for point in points])) / 2
    min_y = (min([point[4] for point in points]) + max([point[4] for point in points])) / 2

    centred_path = ' '.join([
        f'{action if start_from else ""}{(x - min_x):.3f},{(y - min_y):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


def scaled_path(d, scale: float = 1):
    points = break_into_point_array(d)
    centred_path = ' '.join([
        f'{action if start_from else ""}{(x * scale):.3f},{(y * scale):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


def moved_path(d, position_x, position_y, offset_x=0, offset_y=0):
    points = break_into_point_array(scaled_path(d, 0.8))
    center_x = 0
    center_y = 0

    target_x, target_y = position_x + offset_x, position_y + offset_y

    centred_path = ' '.join([
        f'{action if start_from else ""}{(x - center_x + target_x):.3f},{(y - center_y + target_y):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


def debug_point(point):
    x, y = point
    return Path(d=moved_path(
        "M574.42,855.498 C572.076,855.498 570.384,856.311 569.342,857.936 C568.175,859.498 567.592,861.618 567.592,864.295 C567.592,867.358 568.404,869.993 570.029,872.201 C571.654,874.347 573.446,875.847 575.404,876.701 C577.154,877.545 579.009,877.967 580.967,877.967 C583.248,877.967 584.972,877.155 586.139,875.53 C587.243,873.894 587.795,871.774 587.795,869.17 C587.795,866.108 586.983,863.472 585.358,861.264 C583.733,859.181 581.977,857.681 580.092,856.764 C578.196,855.92 576.305,855.498 574.42,855.498 M577.748,852.967 C584.779,852.967 590.639,854.332 595.326,857.061 C600.076,859.8 602.451,863.024 602.451,866.733 C602.451,870.701 600.009,873.957 595.123,876.498 C590.238,879.165 584.446,880.498 577.748,880.498 C570.842,880.498 564.983,879.134 560.17,876.405 C555.347,873.665 552.936,870.441 552.936,866.733 C552.936,862.764 555.41,859.509 560.358,856.967 C565.243,854.3 571.04,852.967 577.748,852.967",
        x, y
    ))


def debug_text(point, text, font_size=40):
    return Text(
        f'.{str(text)}',
        insert=(point.x, point.y),
        fill="rgb(0,0,0)",
        style=f"font-size:{font_size}; font-family:Arial",
    )
