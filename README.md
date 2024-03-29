# D-based half-step music staff
## Short intro
* 12 - notes notation
* hand-writting staff markup possibility
* acceptable compaction (3 lines per octave)
* note pitch and note height-on-staff correlation ("half-sign" note looks higher then "whole-sign" 'cause visual mass center and means higher note)
* using same visual style for all notes (without pitch-based filling on "#" "b")
* no pitch extra signs "#" "b", alliteration keys, staff keys which moves staff unexpectedly
* explicit octave hook, octaves marks as octave number (0, 1 - ...)
* stable note position (example: "E" note always lay between the solid and firts dotted line in any octave, "A" always half note under 2nd dotted line)
* each note have staff near (no floating in middle notes) to easily note differentiation
* equidistant intervals over all notes (interval visually have same distance starting from any note)
* 5-7 staff dividing for symmetric visual hooks in D (solid line) and F#/Gb, A#/Bb (dotted lines) (sub symmetry in 7 group)


Used as basis [Klavar, Dekker Version (2015)](http://musicnotation.org/system/klavar-dekker-version-by-antoon-dekker/) 
with staf lines inversion and half-note modification instead of filling notes. 

3 lines score per octave (1 bold & 2 dotted as centers D F# A#): 

## Schematic illustration
```
                                          ◠  ⃝
C     |-------⃝--|--|--|--|--|------|-----|------     <- solid line
                             ◠   ⃝  ◡     |
G# Ab |...................⃝..|......|.....|......     <- dotted line
              ◠  ⃝  ◡  |  |      |     |
E     |-------⃝--|--|--|--|--|------|-----|------     <- solid line
              ⃝  ◡  |  |  |  |  |  |      |     |
C     |-------⃝--|--|--|--|--|------|-----|------     <- solid line


        C  C# D  D# E  F  F# G  G#  A  A# B 

```

## Example results
* [Intervals](./examples/results/v2/Intervals.pdf)
* [Blondie Readhat - For the damaged Coda (Part)](./examples/results/v2/ForTheDammagedCoda.pdf)
* [Toby Fox - Waterfall (part)](./examples/results/v2/Waterfall.pdf)

# Converter usage
## Supported input formats
MusicXML

## Software requirements
```python
# global install
python3.8 -m pip install -r requirements.txt
```

## Print help
```python
python3.8 converter.py --help
```

## Usage example
```python 
python3.8 converter.py -i "examples/musicxml/notmania_ru-Ballade_pour_Adeline_.xml" --pdf "exhaust/Ballade_pour_Adeline.pdf" --keep-tmp -o "exhaust"
```

# Alternative notations
Inspired by [Alternative Notations Project](http://musicnotation.org/)
