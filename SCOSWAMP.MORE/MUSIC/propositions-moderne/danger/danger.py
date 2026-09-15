#!/usr/bin/env python3
"""« Ce qui Attend Sous l'Eau » — les dix clairieres mortelles. Do phrygien, 136,4.

Ici la batterie n'est pas un rythme : c'est un **coeur**. Une grosse caisse
seule, deux coups par mesure, sourde, sans charleston ni caisse claire — et
elle accelere. Deux coups par mesure jusqu'a la mesure 12, trois a partir de la
13, quatre a partir de la 21 : la piece ne monte pas, elle **s'affole**.

Le bourdon de do reste (c'est la voix d'accords tenus qui a cede la sienne) :
sous une batterie, il ne reste que cinq voix de hauteur, et entre un accord tenu
et ce bourdon-la, le choix n'a pas ete long.

Le mode phrygien pose un re bemol un demi-ton au-dessus de la tonique. Le
CROCHET est ce demi-ton : do-re bemol-do, enonce mesure 5, puis **repris a
l'identique** mesure 9 sur une autre basse. QUESTION ET REPONSE mesures 7, 12 et
24 : la melodie tient, le contre-chant repond par le meme demi-ton, plus bas.

La SURPRISE est mesure 20 : **tout s'arrete pendant deux temps**, coeur compris,
et le fa mineur qui suit tombe dans le vide. C'est le seul silence complet du
dossier avec celui de l'accueil, et il ne dure pas assez pour qu'on croie a une
panne — juste assez pour qu'on retienne son souffle.

28 mesures a 4/4, 49,3 s.

    python3 danger.py && python3 ../../midi_to_mb.py danger.mid \\
        DANGER.MB.BIN --bpm 136.364 --max 2304 --wav DANGER.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 3000 / 22, 4, 28
LEN = BAR * BARS

CH = (["Cm", "Db"] + ["Cm", "Db", "Cm", "Bbm"] + ["Cm", "Db", "Ab", "Bbm", "Cm"]
      + ["Fm", "Db", "Ab", "Eb", "Fm", "Bbm", "Db"]
      + ["Cm", "Db", "Cm", "Bbm", "Ab", "Db", "Fm", "Cm"])
DU = ([8, 8] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 4, 4, 8]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "G5:4",                           "G5:2 Ab5:2",
    "Ab5:2 G5:2",                     "G5:2 F5:2",
    "C6:.5 Db6:.5 C6:1 G5:2",         "Db6:2 C6:2",            # le crochet : le demi-ton
    "G5:4",                           "Db6:2 Bb5:2",           # 7 : la melodie tient
    "C6:.5 Db6:.5 C6:1 G5:2",         "Db6:2 Ab5:2",           # le crochet, 2e fois
    "Eb6:2 F6:2",                     "G5:4",                  # 12 : la melodie tient
    "Ab5:1 C6:1 F6:2",                "Db6:1 Ab5:1 F5:2",
    "Eb6:1 C6:1 Ab5:2",               "G5:1 Bb5:1 Eb6:2",
    "F6:1 Ab6:1 C6:2",                "Db6:1 F6:1 Bb6:2",
    "Ab6:1 F6:1 Db6:1 Ab5:1",         "G5:2 -:2",              # 20 : le silence
    "C6:.5 Db6:.5 C6:1 G5:2",         "Db6:.5 C6:.5 Ab5:1 F6:2",
    "Eb6:.5 Db6:.5 C6:1 G5:2",        "Bb5:4",                 # 24 : la melodie tient
    "Eb6:1 C6:1 Ab5:2",               "F6:1 Db6:1 Ab5:2",
    "C6:1 Ab5:1 F5:2",                "G5:2 C6:2",
]
assert len(MEL) == BARS

CTR = [                       # au-dessus de l'arpege : c'est la voix qui repond
    "C5:4",                           "C5:2 Eb5:2",
    "Db5:2 C5:2",                     "Bb4:2 C5:2",
    "G4:2 Eb5:2",                     "Ab4:2 F4:2",
    "C5:.5 Db5:.5 C5:1 G4:1 Eb5:1",   "Bb4:2 Db5:2",           # 7 : la reponse
    "Ab4:2 C5:2",                     "Db5:2 Ab4:2",
    "G4:2 Eb5:2",                     "C5:.5 Db5:.5 C5:1 Ab4:1 Eb5:1",  # 12
    "Ab4:2 C5:2",                     "F4:2 Db5:2",
    "Eb5:2 C5:2",                     "Bb4:2 G4:2",
    "Ab4:2 C5:2",                     "Db5:2 F4:2",
    "Ab4:2 Db5:2",                    "G4:2 -:2",              # 20 : le silence
    "Eb5:2 C5:2",                     "F4:2 Db5:2",
    "Eb5:2 G4:2",                     "C5:.5 Db5:.5 C5:1 Ab4:1 F4:1",   # 24
    "C5:2 Ab4:2",                     "F4:2 Db5:2",
    "Ab4:2 C5:2",                     "G4:2 C5:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("C", "phrygien", BPM, BAR, "Ce qui Attend Sous l'Eau")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # l'arpege se resserre : blanches, noires, croches
    arp = arpeggio(CH[0:2], 0, DU[0:2], 2.0, (0, 1, 2, 1), lo=50)
    arp += arpeggio(CH[2:6], BAR * 4, DU[2:6], 1.0, (0, 1, 2, 1), lo=50)
    arp += arpeggio(CH[6:], BAR * 8, DU[6:], 0.5, (0, 1, 2, 1), lo=50)
    p.add("arpege", arp)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", progression(CH[0:6], 0, DU[0:6], [(0, 2), (-1, 2)], lo=45)
                   + progression(CH[6:], BAR * 8, DU[6:],
                                 [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=45))
    p.add("bourdon", pedal(midi("C2"), 0, LEN, retrig=BAR * 4))

    # LE COEUR : grosse caisse seule, et il accelere
    p.add_drums("K.....K.", t0=0, length=BAR * 12)              # deux coups
    p.add_drums("K...K.K.", t0=BAR * 12, length=BAR * 8)        # trois
    p.add_drums("K.K.K.K.", t0=BAR * 20, length=BAR * 8)        # quatre

    p.hush(BAR * 19 + 2, BAR * 20)                              # deux temps de rien
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("danger.mid"))
