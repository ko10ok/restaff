from collections import namedtuple
from typing import List, Dict, Tuple, Any

from .notation_markup.measures import guess_measure_octave
from ..types import ScoreSheet, Part, Measure, Note


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
    print(f'{parted_measure_octaves}')
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
    print(f'{parted_measure_time}')
    return parted_measure_time


OctaveChanges = namedtuple('OctaveChanges', ['octave', 'is_changed'])


def analyze_parts_staffs_octaves(parts: List[Part]) -> Dict[int, Dict[str, Dict[int, OctaveChanges]]]:
    parted_measure_octaves = {}
    for part in parts:
        last_measure_guessed_staff_octave = {}
        for measure_idx, measure in enumerate(part.measures):
            if measure_idx not in parted_measure_octaves:
                parted_measure_octaves[measure_idx] = {}

            guessed_staff_octave = guess_measure_octave(measure)

            default_octave=5
            for staff, octave in guessed_staff_octave.items():
                if not octave:
                    guessed_staff_octave[staff] = last_measure_guessed_staff_octave.get(staff, default_octave)

            print(f'{measure_idx=} {guessed_staff_octave=} {last_measure_guessed_staff_octave=}')
            octave_changed = last_measure_guessed_staff_octave != guessed_staff_octave
            parted_measure_octaves[measure_idx][part.info.id] = {
                staff: OctaveChanges(octave, octave_changed)
                for staff, octave in guessed_staff_octave.items()
            }

            last_measure_guessed_staff_octave = guessed_staff_octave

    return parted_measure_octaves


TimeChanges = namedtuple('TimeChanges', ['time', 'is_changed'])


def analyze_parts_staffs_times(parts: List[Part]) -> Dict[int, Dict[str, Dict[int, Any]]]:
    parted_measure_time = {}
    for part in parts:
        last_measure_time = None
        for measure_idx, measure in enumerate(part.measures):
            if measure_idx not in parted_measure_time:
                parted_measure_time[measure_idx] = {}

            measure_time = measure.time
            time_changed = last_measure_time != measure_time
            parted_measure_time[measure_idx][part.info.id] = {
                staff: TimeChanges(measure_time, time_changed)
                for staff in range(1, part.staff_count + 1)
            }
            last_measure_time = measure_time
    print(f'{parted_measure_time}')
    return parted_measure_time


def flat_measured_parted_staff(parted_staff_thing: Dict[int, Dict[str, Dict[int, Any]]]):
    return {
        (measure, part, staff): thing
        for measure, parts in parted_staff_thing.items()
        for part, staffs in parts.items()
        for staff, thing in staffs.items()
    }


def analyze_octave_drawing(staff_octave_draws, measure_index, first_on_staff):
    return any([
        octave_draws.draws for k, octave_draws in staff_octave_draws.items() if k[0] == measure_index
    ]) or first_on_staff


def analyze_time_drawing(staff_time_draws, measure_index, first_on_staff):
    return any([
        octave_draws.draws for k, octave_draws in staff_time_draws.items() if k[0] == measure_index
    ]) or first_on_staff


def analyze_chords(notes: List[Note]) -> List[Tuple[Note, Note]]:
    chord_followed_notes = []
    for note_idx in range(len(notes)):
        if note_idx != len(notes) - 1:
            if notes[note_idx + 1].chord:
                chord_followed_notes += [notes[note_idx]]
    return chord_followed_notes
