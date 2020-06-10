def moved_to_zero_path(d):
    str_points = d.split(' ')
    points = [
        (action := b[0], start_from := action.isalpha(), pair := b.split(','), float(pair[0][start_from:]),
         float(pair[1]))
        for b in str_points
    ]
    min_x = min([point[3] for point in points])
    min_y = min([point[4] for point in points])

    centred_path = ' '.join([
        f'{action if start_from else ""}{(x - min_x):.3f},{(y - min_y):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


def scaled_path(d, scale=1):
    str_points = d.split(' ')
    points = [
        (action := b[0], start_from := action.isalpha(), pair := b.split(','), float(pair[0][start_from:]),
         float(pair[1]))
        for b in str_points
    ]

    centred_path = ' '.join([
        f'{action if start_from else ""}{(x * scale):.3f},{(y * scale):.3f}'
        for action, start_from, pair, x, y in points
    ])
    return centred_path


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
