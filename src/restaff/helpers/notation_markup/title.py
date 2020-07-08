from svgwrite.text import Text

from ...types import PageProperties, ScoreSheet, StaffProperties


def markup_title(page_prop: PageProperties, staff_prop: StaffProperties, sheet: ScoreSheet):
    # TODO calc real text width and heights
    title_height = 100

    # TODO calc real text width and heights
    author_title_offset = 100

    return [
        Text(
            sheet.title,
            insert=(page_prop.width // 2, staff_prop.top_offset),
            fill="rgb(110,110,110)",
            style="font-size:200px; font-family:Arial; font-weight: bold; text-anchor: middle;",
        ),
        Text(
            sheet.author,
            insert=(page_prop.width - staff_prop.right_offset,
                    staff_prop.top_offset + author_title_offset + title_height + author_title_offset),
            fill="rgb(110,110,110)",
            style="font-size:100px; font-family:Arial; font-weight: bold; text-anchor: end;",
        )
    ]


# TODO calc real first page offsets for staffs with title and author height
def title_place_heigh(page_prop: PageProperties, staff_prop: StaffProperties):
    return staff_prop.top_offset + 500
