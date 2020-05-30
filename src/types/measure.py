from typing import NamedTuple, List

from .note import Note


class TimeMeasure(NamedTuple):
    beats: int
    beat_type: int

    @classmethod
    def from_xml_time(cls, xml_time):
        return TimeMeasure(
            beats=int(xml_time.get('beats')),
            beat_type=int(xml_time.get('beat-type'))
        )


class MeasureDisplayParams(NamedTuple):
    width: float


class Measure(NamedTuple):
    number: int
    time: TimeMeasure
    display: MeasureDisplayParams
    staves: int
    notes: List[Note]

    @classmethod
    def from_xml_measure(self, xml_measure, last_measure_attributes):
        notes = [Note.from_music_xml_note(note) for note in xml_measure.get('note')]
        return Measure(
            number=int(xml_measure.get('@number')),
            time=TimeMeasure.from_xml_time(last_measure_attributes.get('time')),
            staves=int(last_measure_attributes.get('staves') or 1),
            display=MeasureDisplayParams(width=xml_measure.get('@width')),
            notes=notes
        )
