from collections import namedtuple
from typing import List, Dict

from .notation_markup.measures import guess_measure_octave
from ..types import ScoreSheet, Part, Measure


def get_staffs_count(sheet: ScoreSheet):
    return sum([part.measures[0].staves for part in sheet.parts])


def get_parted_measures(parts: List[Part], measure_index) -> Dict[int, Measure]:
    return {part.info.id: part.measures[measure_index] for part in parts}


# TODO move here guess_measure_octave(measure: Measure) (?)

MeasureOctave = namedtuple('MeasureOctave', ['staff_octaves', 'is_changed'])
MeasureTime = namedtuple('MeasureTime', ['staff_time', 'is_changed'])


def analyze_octaves(parts: List[Part]) -> Dict[int, Dict[int, MeasureOctave]]:
    parted_measure_octaves = {}
    for part in parts:
        last_measure_guessed_staff_octave = None
        for measure in part.measures:
            if measure.number not in parted_measure_octaves:
                parted_measure_octaves[measure.number] = {}

            guessed_staff_octave = guess_measure_octave(measure)
            octave_changed = last_measure_guessed_staff_octave != guessed_staff_octave
            parted_measure_octaves[measure.number][part.info.id] = MeasureOctave(guessed_staff_octave, octave_changed)
            last_measure_guessed_staff_octave = guessed_staff_octave
    print(parted_measure_octaves)
    return parted_measure_octaves


def analyze_times(parts: List[Part]) -> Dict[int, Dict[int, MeasureTime]]:
    parted_measure_time = {}
    for part in parts:
        last_measure_time = None
        for measure in part.measures:
            if measure.number not in parted_measure_time:
                parted_measure_time[measure.number] = {}

            measure_time = measure.time
            octave_changed = last_measure_time != measure_time
            parted_measure_time[measure.number][part.info.id] = MeasureTime(measure_time, octave_changed)
            last_measure_time = measure_time
    print(parted_measure_time)
    return parted_measure_time
