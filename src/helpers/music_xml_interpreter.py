from typing import List, Dict

from ..types import ScoreSheet, Part, Measure


def get_staffs_count(sheet: ScoreSheet):
    return sum([part.measures[0].staves for part in sheet.parts])


def get_parted_measures(parts: List[Part], measure_index) -> Dict[int, Measure]:
    return {part.info.id: part.measures[measure_index] for part in parts}
