from typing import NamedTuple, List

from .part import Part


class ScoreSheet(NamedTuple):
    # scaling: Any
    title: str
    author: str
    parts: List[Part]

    @classmethod
    def from_music_xml_sheet(cls, music_xml_sheet):
        partitures_info = music_xml_sheet['score-partwise']['part-list']['score-part']
        partitures = music_xml_sheet['score-partwise']['part']
        parts = zip(partitures_info, partitures)

        if 'creator' in music_xml_sheet['score-partwise']['identification']:
            author = music_xml_sheet['score-partwise']['identification']['creator'][0].get('#text')
        else:
            author = 'Undefined'
        return ScoreSheet(
            # scaling=music_xml_sheet['score-partwise']['defaults']['scaling'],
            title=music_xml_sheet['score-partwise'].get('work', {}).get('work-title', 'Undefined'),
            # TODO choose one or concat creators 'couse
            #  multiple type of creators can present on document
            author=author,
            parts=[Part.from_music_xml_part(part_info, part) for part_info, part in parts]
        )
