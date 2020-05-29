from collections import OrderedDict
from pprint import pprint

from xmltodict import parse as xml_parse

from src import Measure

result: str = ''
# with open('examples/musicxml/His Theme experiments.musicxml') as music_xml_file:
with open('examples/musicxml/His Theme experiments multi instruments.musicxml') as music_xml_file:
    result = music_xml_file.read()

dict_res = xml_parse(result, force_list=['score-part', 'part', 'note'])

# https://github.com/w3c/musicxml/blob/v3.1/schema/musicxml.xsd
# pprint(dict_res)

# print(dict_res.keys())
# print(dict_res['score-partwise'].keys())
# print(dict_res['score-partwise']['part'].keys())

partitures_info = dict_res['score-partwise']['part-list']['score-part']
# pprint(partitures_info)
# pprint(partitures['@id']) # may be multiple parts, should pe parsed always as array?

# target_part = partitures[0]['@id']

partitures = dict_res['score-partwise']['part']  # should be many? should be parsed as array?
# pprint(partitures)
# target_partitura = list(filter(lambda x: x['@id'] == target_part, partitures))
# assert len(target_partitura) == 1, print(f'no partitura {target_part} in {partitures}')
target_partitura = partitures[0]

target_partitura_measures = target_partitura['measure']
# pprint(target_partitura_measures)

last_attrs = {}

for measure in target_partitura_measures:
    # print('measure #{} raw'.format(measure.get('@number')))
    # print('Original measure:')
    # pprint(measure)

    last_attrs = OrderedDict({**last_attrs, **(measure.get('attributes', {}))})

    measure = Measure.from_xml_measure(measure, last_attrs)
    print(measure)

    # for note in measure.notes:
    # print(note)
