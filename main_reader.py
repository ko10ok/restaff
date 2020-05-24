from pprint import pprint

from xmltodict import parse as xml_parse

result: str = ''
with open('examples/musicxml/His Theme with keys.musicxml') as music_xml_file:
    result = music_xml_file.read()

dict_res = xml_parse(result)

# https://github.com/w3c/musicxml/blob/v3.1/schema/musicxml.xsd
pprint(dict_res)

# print(dict_res.keys())
# print(dict_res['score-partwise'].keys())
# print(dict_res['score-partwise']['part'].keys())

partitures = dict_res['score-partwise']['part-list']['score-part']
# pprint(partitures['@id']) # may be multiple parts, should pe parsed always as array?

target_part = partitures['@id']

partitures = dict_res['score-partwise']['part']  # should be many? should be parsed as array?

# target_partitura = list(filter(lambda x: x['@id'] == target_part, partitures))
# assert len(target_partitura) == 1, print(f'no partitura {target_part} in {partitures}')
target_partitura = partitures

target_partitura_measures = target_partitura['measure']
pprint(target_partitura_measures)
for measure in target_partitura_measures:
    # print(measure)
    print(measure.get('attributes', {}).get('key'))
    # exit()
    for note in measure['note']:
        pitch = note.get('pitch', {})
        note_name = '{}{}{}'.format(
            pitch.get('step'),
            pitch.get('octave'),
            ['', '#', 'b'][int(pitch.get('alter', 0))]
        ) if pitch else None
        print(measure['@number'], note.get('staff'), note.get('pitch'), note.get('type'), note_name)

