#!/usr/bin/env python3
"""« Par la Trouee de Ciel » — les pages 158 et 175. Re mixolydien, 150.

La seule piece en majeur du dossier, et la seule dont la batterie soit une
fanfare : caisse claire sur les temps faibles, cymbale a chaque depart de
phrase, charleston ouvert sur la derniere mesure. Le bourdon de re a cede sa
voix a la frappe — une victoire ne bourdonne pas.

Le CROCHET (re-fa diese-la qui monte d'une tierce, puis re a l'octave) est
enonce mesure 1, **repris mesure 5** une quarte plus haut sur sol, et une
troisieme fois mesure 13 tout en haut : la piece monte trois fois, chaque fois
d'un cran, et ne redescend qu'a la cadence.

La SURPRISE est mesure 9 : un **si mineur** la ou l'oreille attend un sol. La
victoire est amere trois secondes — on sort du Marais, on n'en revient pas
indemne — puis do majeur la releve.

Le do becarre du mixolydien supprime la sensible : la cadence finale est do-re,
pas la-re. C'est ce qui empeche la victoire de sonner comme un generique et ce
qui la rattache au monde modal du reste du jeu.

QUESTION ET REPONSE mesures 4 et 12. 16 mesures a 4/4, 25,6 s.
**Sans boucle** (`--no-loop`).

    python3 victoire.py && python3 ../../midi_to_mb.py victoire.mid \\
        VICTORY.MB.BIN --bpm 150 --no-loop --max 1280 --wav VICTOIRE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 16
LEN = BAR * BARS

CH = (["D", "D", "C", "G"] + ["G", "D", "C", "D"]
      + ["Bm", "G", "C", "D"] + ["D", "C", "G", "D"])
DU = ([4, 4, 4, 4] + [4, 4, 4, 4]
      + [4, 4, 4, 4] + [4, 4, 4, 4])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "D5:1 F#5:1 A5:2",                "D6:2 A5:2",             # le crochet
    "C6:1 E6:1 G6:2",                 "D6:4",                  # 4 : la melodie tient
    "G5:1 B5:1 D6:2",                 "A5:1 D6:1 F#6:2",       # le crochet, une quarte plus haut
    "E6:1 C6:1 G5:2",                 "A5:1 D6:1 F#6:2",
    "B5:1 D6:1 F#6:2",                "G6:1 D6:1 B5:2",        # 9 : le si mineur
    "C6:1 E6:1 G6:2",                 "A6:4",                  # 12 : la melodie tient
    "D6:1 F#6:1 A6:2",                "G6:1 E6:1 C6:2",        # le crochet tout en haut
    "B5:1 D6:1 G6:2",                 "D6:4",
]
assert len(MEL) == BARS

CTR = [
    "A4:2 D4:2",                      "F#4:2 A4:2",
    "C5:2 E4:2",                      "D4:.5 E4:.5 F#4:1 A4:1 D4:1",   # 4 : la reponse
    "B4:2 G4:2",                      "A4:2 F#4:2",
    "E4:2 C5:2",                      "D4:2 A4:2",
    "F#4:2 B4:2",                     "D4:2 G4:2",
    "E4:2 C5:2",                      "A4:.5 B4:.5 C5:1 A4:1 F#4:1",   # 12 : la reponse
    "A4:2 D4:2",                      "C5:2 E4:2",
    "G4:2 D4:2",                      "A4:2 D4:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("D", "mixolydien", BPM, BAR, "Par la Trouee de Ciel")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    # l'arc : noires aux quatre premieres mesures, croches ensuite
    arp = arpeggio(CH[0:4], 0, DU[0:4], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[4:], BAR * 4, DU[4:], 0.5, (0, 1, 2, 1), lo=53)
    p.add("arpege", arp)
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    p.add("basse", progression(CH, 0, DU, [(0, 2), (-1, 1), (0, 1)], lo=45))

    p.add_drums("K...S...", t0=0, length=BAR * 4)
    p.add_drums("K..HS.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.H.S.HO", t0=BAR * 12, length=BAR * 4)
    p.add_drums([(0, "C")], t0=0)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 4)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 12)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("victoire.mid"))
