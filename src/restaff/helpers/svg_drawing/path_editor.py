import re

from svg.path import parse_path
from svgwrite.shapes import Circle
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

    # center alignment
    min_x = (min([point[3] for point in points]) + max([point[3] for point in points])) / 2
    min_y = (min([point[4] for point in points]) + max([point[4] for point in points])) / 2

    # left up alignment
    min_x = min([point[3] for point in points])
    min_y = min([point[4] for point in points])

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
    return Circle(center=(x, y), r=10)


def debug_text(point, text, font_size=40):
    return Text(
        f'.{str(text)}',
        insert=(point.x, point.y),
        fill="rgb(0,0,0)",
        style=f"font-size:{font_size}; font-family:Arial",
    )
