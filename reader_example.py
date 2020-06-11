from src.types import ScoreSheet
from src.helpers import read_music_xml

# https://github.com/w3c/musicxml/blob/v3.1/schema/musicxml.xsd

music_xml_sheet = read_music_xml('examples/musicxml/His Theme experiments multi instruments.musicxml')
# pprint(music_xml_sheet)
sheet = ScoreSheet.from_music_xml_sheet(music_xml_sheet)

print(sheet)
