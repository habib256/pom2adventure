#!/usr/bin/env python3
"""« Le Bois des Guetteurs » — le Marais nord. Mi eolien, 150 a la noire.

L'OSTINATO fixe de quatre croches — mi, si, sol, si — ne change jamais pendant
que les accords bougent dessous : c'est le regard qui suit le joueur d'une
clairiere a l'autre. Il est le crochet, et il est enonce d'un bout a l'autre.

La SURPRISE est aux mesures 17-18 : l'accord passe en **mi majeur** et le sol de
l'ostinato devient sol diese. Le motif n'a pas bouge d'un pouce et il a change de
nature — les guetteurs se montrent. La batterie s'arrete pendant ces deux
mesures, ce qui rend le glissement plus net encore.

Le THEME chante est enonce **deux fois**, mesures 5-6 puis 9-10, la seconde fois
avec un la mineur et un si mineur passants (mesure 11) qui le poussent plus haut.
QUESTION ET REPONSE mesures 7, 12 et 24 : la melodie tient une ronde, le
contre-chant repond en croches.

Cinq voix de hauteur et une batterie ; le bourdon de mi a cede sa voix a la
grosse caisse, qui frappe les temps qu'il tenait.

28 mesures a 4/4, 44,8 s.

    python3 nord.py && python3 ../../midi_to_mb.py nord.mid \\
        NORTHSWAMP.MB.BIN --bpm 150 --max 2304 --wav MARAISNO.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS

CH = (["Em", "Em", "D"] + ["Em", "C", "G", "D"] + ["Em", "C", "Am", "Bm", "Em"]
      + ["C", "G", "D", "Em", "E", "Am", "Bm"]
      + ["Em", "C", "G", "D", "Em", "Am", "C", "Em"])
DU = ([8, 4, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 8, 4, 4]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "B5:2 E6:2",                      "D6:2 B5:2",
    "A5:1.5 F#5:.5 A5:2",             "F#5:2 D5:2",
    "E5:1 G5:1 B5:2",                 "C6:1.5 B5:.5 G5:2",     # le theme
    "D6:4",                           "F#5:1 A5:1 D6:2",       # 7 : la melodie tient
    "E5:1 G5:1 B5:2",                 "C6:1.5 B5:.5 G5:2",     # le theme, 2e fois
    "A5:2 B5:2",                      "E6:4",                  # 12 : la melodie tient
    "G5:1 C6:1 E6:2",                 "D6:1.5 B5:.5 G5:2",
    "A5:1 D6:1 F#6:2",                "E6:2 B5:2",
    "G#5:2 B5:2",                     "E6:1 B5:1 G#5:2",       # 17-18 : mi majeur
    "A5:1 C6:1 E6:2",                 "F#6:2 D6:2",
    "E6:1 G6:1 B6:2",                 "A6:1.5 G6:.5 E6:2",     # le theme a l'octave
    "D6:2 F#6:2",                     "B6:4",                  # 24 : la melodie tient
    "A6:1 E6:1 C6:2",                 "G6:1 E6:1 C6:2",
    "B5:1 A5:1 G5:2",                 "E5:4",
]
assert len(MEL) == BARS

CTR = [
    "E4:2 B4:2",                      "G4:2 B4:2",
    "F#4:2 A4:2",                     "D4:2 F#4:2",
    "G4:2 E4:2",                      "E4:2 G4:2",
    "B4:.5 A4:.5 G4:1 E4:1 B4:1",     "A4:2 F#4:2",            # 7 : la reponse
    "G4:2 B4:2",                      "E4:2 G4:2",
    "A4:2 F#4:2",                     "E4:.5 F#4:.5 G4:1 B4:1 G4:1",  # 12
    "E4:2 G4:2",                      "D4:2 B4:2",
    "A4:2 F#4:2",                     "G4:2 E4:2",
    "G#4:2 B4:2",                     "E4:2 G#4:2",            # le sol diese
    "A4:2 C5:2",                      "F#4:2 D4:2",
    "G4:2 B4:2",                      "E4:2 G4:2",
    "D4:2 F#4:2",                     "E4:.5 F#4:.5 G4:1 B4:1 A4:1",  # 24
    "A4:2 E4:2",                      "G4:2 C5:2",
    "B4:2 G4:2",                      "E4:2 B4:2",
]
assert len(CTR) == BARS

WATCH = [midi("E4"), midi("B4"), midi("G4"), midi("B4")]        # les guetteurs
SEEN = [midi("E4"), midi("B4"), midi("G#4"), midi("B4")]        # ils se montrent


def build():
    p = Piece("E", "eolien", BPM, BAR, "Le Bois des Guetteurs")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    # l'ostinato se revele : deux mesures a la noire, puis il ne lache plus
    p.add("ostinato", ostinato(WATCH, 1.0, 0, BAR * 2)
                      + ostinato(WATCH, 0.5, BAR * 2, BAR * 14)
                      + ostinato(SEEN, 0.5, BAR * 16, BAR * 2)
                      + ostinato(WATCH, 0.5, BAR * 18, BAR * 10))
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    # la basse marche en noires, mais retient son pas pendant tout le B
    march = [(0, 1), (0, 1), (-1, 1), (0, 1)]
    p.add("basse", progression(CH[0:12], 0, DU[0:12], march, lo=45)
                   + progression(CH[12:19], BAR * 12, DU[12:19], [(0, 2), (-1, 2)], lo=45)
                   + progression(CH[19:], BAR * 20, DU[19:], march, lo=45))

    p.add_drums("K...K...", t0=0, length=BAR * 4)
    p.add_drums("K..HS..H", t0=BAR * 4, length=BAR * 12)
    #      mesures 17-18 : rien, le temps du glissement en majeur
    p.add_drums("K.H.S.H.", t0=BAR * 18, length=BAR * 10)
    p.add_drums([(0, "C")], t0=BAR * 4)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 18)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("nord.mid"))
