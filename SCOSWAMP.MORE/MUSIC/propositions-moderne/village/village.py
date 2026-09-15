#!/usr/bin/env python3
"""« Les Feux de Bourbenville » — le village, le prologue, Courbensaule.

Sol mixolydien, 166,7 a la noire, 28 mesures a 4/4, 40 s. Cinq voix de hauteur et
une batterie de danse : le bourdon a cede sa voix a la grosse caisse, ce qui
convient — un village ne bourdonne pas, il tape du pied.

Le CROCHET (re-sol-si-la, puis la retombee la-fa-la) est enonce **deux fois**,
mesures 5-6 puis 9-10, la seconde fois avec un re mineur passager a la mesure 11
qui le fait respirer autrement. Il revient a l'octave a la mesure 21.

QUESTION ET REPONSE : mesures 7, 12 et 24, la melodie tient une ronde et le
contre-chant repond en croches montantes — voix 0 a gauche, voix 3 a droite.

La PARTIE B (13-20) monte d'une tierce et change d'harmonie. La SURPRISE est
double, mesures 17-18 : un accord de **si bemol**, etranger au mixolydien, et
**la batterie qui s'arrete net** ; elle revient mesure 19 sur un coup de
cymbale. C'est le seul moment du jeu ou le village se tait.

RYTHME HARMONIQUE : huit temps sur sol a l'intro, quatre en A, deux aux mesures
11 et 23, huit sur la cadence finale.

    python3 village.py && python3 ../../midi_to_mb.py village.mid \\
        VILLAGE.MB.BIN --bpm 166.667 --max 2304 --wav VILLAGE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 3000 / 18, 4, 28
LEN = BAR * BARS

CH = (["G", "F", "C"] + ["G", "F", "C", "G"] + ["G", "F", "C", "Dm", "G"]
      + ["Am", "F", "C", "G", "Bb", "F", "C", "G"]
      + ["G", "F", "C", "Dm", "G", "Em", "C", "G"])
DU = ([8, 4, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 4, 4, 4, 4]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "D5:2 G5:2",                      "B5:2 A5:2",
    "A5:1.5 F5:.5 A5:2",              "G5:2 D5:2",
    "D5:1 G5:1 B5:1 A5:1",            "A5:1.5 F5:.5 A5:2",     # crochet
    "G5:4",                           "B5:1 G5:1 D5:2",        # 7 : la melodie tient
    "D5:1 G5:1 B5:1 A5:1",            "A5:1.5 F5:.5 A5:2",     # crochet, 2e fois
    "C6:2 A5:2",                      "B5:4",                  # 12 : la melodie tient
    "C6:1 E6:1 A5:2",                 "F6:1.5 C6:.5 A5:2",     # B : une tierce plus haut
    "G5:1 C6:1 E6:2",                 "D6:1 B5:1 G5:2",
    "Bb5:2 D6:2",                     "C6:1 A5:1 F5:2",        # 17 : si bemol, plus de batterie
    "E5:1 G5:1 C6:2",                 "D6:2 B5:2",
    "D6:1 G6:1 B6:1 A6:1",            "A6:1.5 F6:.5 A6:2",     # A' : le crochet a l'octave
    "G6:2 F6:2",                      "D6:4",                  # 24 : la melodie tient
    "E6:1 B5:1 G6:2",                 "E6:1 C6:1 G5:2",
    "B5:1 A5:1 G5:2",                 "G5:4",
]
assert len(MEL) == BARS

CTR = [
    "D4:2 G4:2",                      "B4:2 A4:2",
    "A4:2 F4:2",                      "G4:2 D4:2",
    "B4:2 D4:2",                      "C5:2 A4:2",
    "G4:.5 A4:.5 B4:1 C5:1 E4:1",     "D4:2 G4:2",             # 7 : la reponse
    "B4:2 G4:2",                      "A4:2 F4:2",
    "E4:2 F4:2",                      "D4:.5 E4:.5 G4:1 B4:1 A4:1",  # 12 : la reponse
    "A4:2 C5:2",                      "A4:2 F4:2",
    "E4:2 G4:2",                      "B4:2 D4:2",
    "F4:2 Bb4:2",                     "A4:2 C5:2",
    "G4:2 E4:2",                      "D4:2 B4:2",
    "B4:2 D4:2",                      "C5:2 A4:2",
    "G4:2 F4:2",                      "D4:.5 E4:.5 G4:1 B4:1 D4:1",  # 24 : la reponse
    "G4:2 B4:2",                      "C5:2 G4:2",
    "D4:2 B4:2",                      "G4:2 D4:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("G", "mixolydien", BPM, BAR, "Les Feux de Bourbenville")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # l'arc : noires a l'intro, croches en A, la moitie du B retombe a la noire
    arp = arpeggio(CH[0:3], 0, DU[0:3], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[3:12], BAR * 4, DU[3:12], 0.5, (0, 2, 1, 2), lo=53)
    arp += arpeggio(CH[12:16], BAR * 12, DU[12:16], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[16:18], BAR * 16, DU[16:18], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[18:], BAR * 18, DU[18:], 0.5, (0, 2, 1, 2), lo=53)
    p.add("arpege", arp)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    p.add("basse", progression(CH, 0, DU,
                               [(0, 1.5), (0, .5), (-1, 1), (0, 1)], lo=43))

    p.add_drums("K..HK.H.", t0=0, length=BAR * 4)
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 12)
    #      mesures 17-18 : rien. Le village se tait.
    p.add_drums("K.H.S.H.", t0=BAR * 18, length=BAR * 2)
    p.add_drums("K.HHS.H.", t0=BAR * 20, length=BAR * 8)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 4)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 18)             # la reprise
    p.add_drums([(0, "C")], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("village.mid"))
