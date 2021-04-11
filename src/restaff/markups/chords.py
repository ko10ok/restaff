from typing import List, Dict

from restaff.helpers import analyze_chord_followed_notes
from restaff.types import ChordNote
from restaff.types import Note


def note_rank(note: Note):
    note_pitch = note.pitch
    note_line = {'C': 11, 'D': 22, 'E': 33, 'F': 39, 'G': 50, 'A': 61, 'B': 72}
    return note_pitch.octave * 72 + note_line[note_pitch.step] + note_pitch.alter * 5


def alternater():
    state = False
    prev_note = None

    def f(note):
        nonlocal prev_note, state

        if prev_note is None:
            prev_note = note
            return state

        if abs(note_rank(note) - note_rank(prev_note)) <= 15:
            state = not state
        else:
            state = False

        prev_note = note
        return state

    return f


def markup_chords(notes: List[Note]) -> Dict:
    chord_followed_notes = analyze_chord_followed_notes(notes)

    chords = {}
    chord_number = 0
    for note in notes:
        not_chord_note = not note.chord and note not in chord_followed_notes
        chord_note = note.chord or note in chord_followed_notes
        last_chord_note = note.chord and note not in chord_followed_notes
        first_chord_note = not note.chord and note in chord_followed_notes

        if first_chord_note:
            chords[chord_number] = []

        if chord_note:
            chords[chord_number] += [note]

        if last_chord_note:
            chord_number += 1
    logger.debug(f'{chords=}')

    result_chord = {}
    for idx, chord_notes in chords.items():
        logger.debug(f'{chord_notes=}')
        ordered_chord = sorted(chord_notes, key=note_rank)

        make_offset = alternater()
        result_chord.update({
            note.id: ChordNote(idx, position == 0, position == len(ordered_chord) - 1, make_offset(note))
            for position, note in enumerate(ordered_chord)
        })

    logger.debug(f'{result_chord=}')
    return result_chord
