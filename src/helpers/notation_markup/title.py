from svgwrite.text import Text

from ...types import PageProperties, ScoreSheet, StaffProperties


def markup_title(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    center_x = page_prop.width // 2

    # TODO calc real text width and heights
    title_width = 600
    title_height = 100
    title_offset = title_width // 2

    # TODO calc real text width and heights
    author_width = 400
    author_offset = author_width
    author_title_offset = 100

    return [
        Text(
            sheet.title,
            insert=(center_x - title_offset, staff_prop.top_offset),
            fill="rgb(110,110,110)",
            style="font-size:150px; font-family:Arial; font-weight: bold",
        ),
        Text(
            sheet.author,
            insert=(page_prop.width - staff_prop.right_offset - author_offset,
                    staff_prop.top_offset + author_title_offset + title_height + author_title_offset),
            fill="rgb(110,110,110)",
            style="font-size:100px; font-family:Arial; font-weight: bold",
        )
    ]


# TODO calc real first page offsets for staffs with title and author height
def title_place_heigh(page_prop: PageProperties, staff_prop: StaffProperties):
    return staff_prop.top_offset + 500
