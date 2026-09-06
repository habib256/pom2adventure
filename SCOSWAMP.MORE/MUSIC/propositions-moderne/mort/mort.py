#!/usr/bin/env python3
"""« Le Marais Referme » — les onze morts et l'ecran game_over. Do eolien, 125.

**Aucune batterie** : c'est la seule piece du dossier ou l'absence de frappe est
le sujet. Six voix de hauteur, ecrites en blanches et en rondes ; a 125 a la
noire le pouls reel est a 62, mais l'horloge reste celle des autres pieces et
les valeurs tombent juste.

Le CROCHET est une chute : sol-mi bemol, puis la bemol-sol-fa. Il est enonce
mesure 1-2, **repris mesure 9-10** un ton plus bas dans l'harmonie (la bemol au
lieu de do mineur), et la troisieme fois il ne remonte plus.

QUESTION ET REPONSE mesures 4 et 12 : la melodie tient une ronde, le
contre-chant descend seul.

La SURPRISE est double. Mesure 12, **tout se tait pendant deux temps** — le
marais se referme, et il y a un trou. Puis mesure 13 tombe un accord de **re
bemol majeur**, le napolitain : c'est exactement l'accord du theme `danger`,
la chose qui vous a tue, citee une fois, sans commentaire.

16 mesures a 4/4, 30,7 s. **Sans boucle** (`--no-loop`).

    python3 mort.py && python3 ../../midi_to_mb.py mort.mid \\
        DEATH.MB.BIN --bpm 125 --no-loop --max 1280 --wav MORT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 125, 4, 16
LEN = BAR * BARS

CH = (["Cm", "Ab"] + ["Eb", "Bb", "Fm", "Cm"]
      + ["Ab", "Eb", "Fm", "Gm"]
      + ["Db", "Ab", "Fm", "Cm"])
DU = ([8, 8] + [4, 4, 4, 4]
      + [4, 4, 4, 4]
      + [4, 4, 4, 4])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "G5:2 Eb5:2",                     "Ab5:1.5 G5:.5 F5:2",    # le crochet : une chute
    "Eb6:4",                          "D6:2 Bb5:2",            # 3 : la melodie tient
    "C6:2 Ab5:2",                     "G5:4",
    "Ab5:2 C6:2",                     "Bb5:2 G5:2",
    "G5:2 Eb5:2",                     "Ab5:1.5 G5:.5 F5:2",    # le crochet, 2e fois
    "Eb6:2 C6:2",                     "G5:2 -:2",              # 12 : le silence
    "Db6:2 Ab5:2",                    "C6:1.5 Ab5:.5 F5:2",    # 13 : le napolitain
    "Ab5:2 G5:2",                     "C6:4",
]
assert len(MEL) == BARS

CTR = [
    "C4:2 Eb4:2",                     "C4:2 Ab3:2",
    "Bb3:.5 Ab3:.5 G3:1 Eb4:1 G3:1",  "D4:2 Bb3:2",            # 3 : la reponse
    "C4:2 Ab3:2",                     "G3:2 Eb4:2",
    "Ab3:2 C4:2",                     "G3:2 Bb3:2",
    "C4:2 Eb4:2",                     "C4:2 Ab3:2",
    "G3:2 C4:2",                      "G3:2 -:2",              # 12 : le silence
    "F4:2 Db4:2",                     "C4:2 Ab3:2",
    "F4:2 Eb4:2",                     "C4:2 G3:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("C", "eolien", BPM, BAR, "Le Marais Referme")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    # l'arpege descend : quinte, tierce, fondamentale — et il ralentit a la fin
    arp = arpeggio(CH[0:13], 0, DU[0:13], 1.0, (2, 1, 0, 1), lo=57)
    arp += arpeggio(CH[13:], BAR * 15, DU[13:], 2.0, (2, 0), lo=57)
    p.add("arpege", arp)
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    p.add("basse", progression(CH, 0, DU, [(0, 2), (-1, 2)], lo=45))
    p.add("bourdon", pedal(midi("C2"), 0, LEN, retrig=BAR * 4))

    p.hush(BAR * 11 + 2, BAR * 12)                              # le marais se referme
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("mort.mid"))
