from xmltodict import parse as xml_parse

from src import Part

result: str = ''
with open('examples/musicxml/His Theme experiments multi instruments.musicxml') as music_xml_file:
    result = music_xml_file.read()

dict_res = xml_parse(result, force_list=['score-part', 'part', 'note', 'measure'])


# https://github.com/w3c/musicxml/blob/v3.1/schema/musicxml.xsd
# pprint(dict_res)


def split_into_parts(music_xml_partitura):
    partitures_info = dict_res['score-partwise']['part-list']['score-part']
    partitures = dict_res['score-partwise']['part']

    parts = zip(partitures_info, partitures)

    return [Part.from_music_xml_part(part_info, part) for part_info, part in parts]


partitures = split_into_parts(dict_res)
print(partitures)
