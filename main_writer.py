import svgwrite
from svgwrite.shapes import Polyline


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


for part_lne in range(int(list_height // step_parts_y)-1):
    for idx, staff in enumerate([0, 1]):
        add_stan(start_x, lenght, start_y + idx * step_staff_y + part_lne * step_parts_y)

dwg.save(pretty=True)

with open('exhaust/out.svg', 'r') as output:
    print(output.read())
