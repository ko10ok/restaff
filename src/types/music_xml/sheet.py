from typing import NamedTuple, List, Any

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
        return ScoreSheet(
            # scaling=music_xml_sheet['score-partwise']['defaults']['scaling'],
            title=music_xml_sheet['score-partwise']['work']['work-title'],
            author=music_xml_sheet['score-partwise']['identification']['creator']['#text'],
            parts=[Part.from_music_xml_part(part_info, part) for part_info, part in parts]
        )
