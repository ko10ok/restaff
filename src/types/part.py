from collections import OrderedDict
from typing import NamedTuple, Any, List

from .measure import Measure


class Part(NamedTuple):
    info: Any
    measures: List[Any]

    @classmethod
    def from_music_xml_part(cls, part_info, part):
        last_attrs = {}
        measures = [
            Measure.from_xml_measure(
                measure,
                last_attrs := OrderedDict({**last_attrs, **(measure.get('attributes', {}))})
            ) for measure in part.get('measure')]
        return Part(
            info=part_info,
            measures=measures
        )
