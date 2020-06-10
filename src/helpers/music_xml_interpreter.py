from ..types import ScoreSheet


def get_staffs_count(sheet: ScoreSheet):
    return sum([part.measures[0].staves for part in sheet.parts])
