from xmltodict import parse as xml_parse


def read_music_xml(file_path):
    with open(file_path) as music_xml_file:
        result = music_xml_file.read()
        return xml_parse(result, force_list=['score-part', 'part', 'note', 'measure'])
