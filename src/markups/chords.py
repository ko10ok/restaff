from typing import List, Dict

from src.helpers import analyze_chord_followed_notes
from src.types import Note
from src.types.notation_markup.note import ChordNote


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
    print(f'{chords=}')

    def note_rank(note):
        note_pitch = note.pitch
        note_line = {'C': 10, 'D': 20, 'E': 30, 'F': 40, 'G': 50, 'A': 60, 'B': 70}
        return note_pitch.octave * 100 + note_line[note_pitch.step] + note_pitch.alter

    result_chord = {}
    for idx, chord_notes in chords.items():
        print(f'{chord_notes=}')
        ordered_chord = sorted(chord_notes, key=note_rank)
        offset = True
        result_chord.update({
            note.id: ChordNote(idx, position == 0, position == len(ordered_chord) - 1, offset := not offset)
            for position, note in enumerate(ordered_chord)
        })

    print(f'{result_chord=}')
    return result_chord
