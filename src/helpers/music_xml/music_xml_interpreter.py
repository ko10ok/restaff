from collections import namedtuple
from itertools import groupby
from typing import List, Dict, Tuple, Any

from src.types import ScoreSheet, Part, Measure, Note, StaffProperties


def guess_measure_octave(measure: Measure) -> Dict[int, int]:
    notes = {k: list(v) for k, v in groupby(measure.notes, lambda x: x.staff)}
    from statistics import median
    octaves = {}
    for k, v in notes.items():
        note_pitches = [n.pitch.octave for n in v if n.pitch]
        try:
            octaves[k] = int(median(note_pitches))
        except:
            octaves[k] = None

    return octaves


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

            guessed_staff_octave = guess_measure_octave(measure) or {staff: None for staff in
                                                                     range(1, part.staff_count + 1)}
            print(f'{measure.number=} {part.info.id=} {guessed_staff_octave=}')
            octave_changed = last_measure_guessed_staff_octave != guessed_staff_octave
            parted_measure_octaves[measure.number][part.info.id] = MeasureOctave(guessed_staff_octave, octave_changed)
            last_measure_guessed_staff_octave = guessed_staff_octave
    print(f'{parted_measure_octaves=}')
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

            guessed_staff_octave = guess_measure_octave(measure) or {staff: None for staff in
                                                                     range(1, part.staff_count + 1)}

            default_octave = 5
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


def analyze_chord_followed_notes(notes: List[Note]) -> List[Tuple[Note, Note]]:
    chord_followed_notes = []
    for note_idx in range(len(notes)):
        if note_idx != len(notes) - 1:
            if notes[note_idx + 1].chord:
                chord_followed_notes += [notes[note_idx]]
    return chord_followed_notes


def analyze_parts_height(staff_prop: StaffProperties, parts: List[Part], staff_octave_draws, current_measure_idx,
                         measures_count):
    top_offset = {}
    bottom_offset = {}
    for part in parts:
        for staff in range(1, part.staff_count + 1):
            top_offset[(part.info.id, staff)] = 0
            bottom_offset[(part.info.id, staff)] = 0
            for measure_idx, measure in enumerate(
                    part.measures[current_measure_idx:current_measure_idx + measures_count]):
                for note in measure.notes:
                    if note.staff == staff:
                        if not note.rest:
                            offset = 0
                            top_offset[(part.info.id, staff)] = min(
                                top_offset.get((part.info.id, staff), 0),
                                get_note_position(staff_prop, staff_octave_draws[
                                    (current_measure_idx + measure_idx, part.info.id, staff)].octave, note.pitch)
                            )
                            bottom_offset[(part.info.id, staff)] = max(
                                top_offset.get((part.info.id, staff), 0),
                                get_note_position(staff_prop, staff_octave_draws[
                                    (current_measure_idx + measure_idx, part.info.id, staff)].octave,
                                                  note.pitch) - staff_prop.staff_height,
                            )
    StaffPlacement = namedtuple('StaffPlacement', ['top_offset', 'heigth', 'bottom_offset', 'total_height'])
    return {
        (part.info.id, staff): StaffPlacement(top_offset[(part.info.id, staff)], staff_prop.staff_height,
                                              bottom_offset[(part.info.id, staff)],
                                              top_offset[(part.info.id, staff)] + staff_prop.staff_height +
                                              bottom_offset[(part.info.id, staff)])
        for part in parts
        for staff in range(1, part.staff_count + 1)
    }
