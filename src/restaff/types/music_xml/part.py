from collections import OrderedDict
from typing import NamedTuple, List

from .measure import Measure


class PartInfo(NamedTuple):
    id: int
    part_name: str

    @classmethod
    def from_part_list(cls, score_part):
        return PartInfo(
            id=score_part['@id'],
            part_name=score_part['part-name'],
        )


class Part(NamedTuple):
    info: PartInfo
    staff_count: int
    measures: List[Measure]

    @classmethod
    def from_music_xml_part(cls, part_info, part):
        last_attrs = {}
        measures = [
            Measure.from_xml_measure(
                measure,
                last_attrs := OrderedDict({**last_attrs, **(measure.get('attributes', {}))})
            ) for measure in part.get('measure')]
        return Part(
            info=PartInfo.from_part_list(part_info),
            staff_count=measures[0].staves,
            measures=measures
        )
