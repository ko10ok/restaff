import zipfile

from xmltodict import parse as xml_parse


def read_music_xml(file_path):
    with open(file_path) as music_xml_file:
        result = music_xml_file.read()
        return xml_parse(result, force_list=['score-part', 'part', 'note', 'measure', 'creator'])


def read_compressed_music_xml(file_path):
    file = zipfile.ZipFile(file_path, 'r')

    file_name = [file for file in file.filelist if 'META-INF' not in file.filename]
    assert len(file_name) == 1, file_name
    music_xml_file = file.open(file_name.pop(), 'r')

    result = music_xml_file.read()
    return xml_parse(result, force_list=['score-part', 'part', 'note', 'measure', 'creator'])
