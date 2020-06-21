import os
import zipfile

from xmltodict import parse as xml_parse


def read_music_xml(file_path):
    with open(file_path) as music_xml_file:
        result = music_xml_file.read()
        return xml_parse(result, force_list=['score-part', 'part', 'note', 'measure', 'creator'])


def read_compressed_music_xml(file_path):
    file = zipfile.ZipFile(file_path, 'r')

    name = os.path.basename(file_path)
    music_xml_file = file.open(name.replace('.mxl', '.xml'), 'r')

    result = music_xml_file.read()
    return xml_parse(result, force_list=['score-part', 'part', 'note', 'measure', 'creator'])
