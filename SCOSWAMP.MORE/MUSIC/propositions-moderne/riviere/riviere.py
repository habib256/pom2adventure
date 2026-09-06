#!/usr/bin/env python3
"""« Le Pont sur la Croupie » — la riviere et son passage. La dorien, 125.

**Sans batterie** : l'eau ne frappe pas. Six voix de hauteur, dont le bourdon,
et c'est ce bourdon qui porte la SURPRISE — il **change de note**. Mi pendant
tout le A (la quinte, rien ne se pose), il descend sur **re** aux mesures 13 a
20 et l'harmonie entiere bascule d'un cran, puis il remonte sur mi mesure 21
comme si de rien n'etait. C'est le seul endroit du dossier ou la pedale bouge,
et c'est la traversee du pont.

Le CROCHET (la-do-mi qui monte, re-si-sol qui redescend) est enonce **deux
fois**, mesures 5-6 puis 9-10, la seconde fois sur do majeur : la meme montee,
eclairee. QUESTION ET REPONSE mesures 7, 12 et 24 : la melodie tient une ronde
en haut, le contre-chant repond en croches.

Le re majeur du mode dorien (mesures 8, 12, 24) reste la seule lumiere franche.
L'ARC est fait par l'arpege : croches, puis doubles a la mesure 15 quand le
courant se resserre, puis croches a nouveau.

28 mesures a 4/4, 53,8 s — la plus longue boucle du dossier.

    python3 riviere.py && python3 ../../midi_to_mb.py riviere.mid \\
        RIVER.MB.BIN --bpm 125 --max 2304 --wav RIVIERE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 125, 4, 28
LEN = BAR * BARS

CH = (["Am", "Am", "G"] + ["Am", "Em", "G", "D"] + ["Am", "C", "G", "D", "Am"]
      + ["C", "G", "Bm", "Em", "C", "D", "Am"]
      + ["Am", "Em", "G", "D", "Am", "C", "G", "Am"])
DU = ([8, 4, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 4, 4, 8]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "E5:4",                           "E5:2 A5:2",
    "G5:2 B5:2",                      "A5:2 E5:2",
    "A5:1 C6:1 E6:2",                 "D6:1.5 B5:.5 G5:2",     # le crochet
    "A5:4",                           "F#5:1 A5:1 D5:2",       # 7 : la melodie tient
    "A5:1 C6:1 E6:2",                 "E6:1.5 C6:.5 A5:2",     # le crochet, 2e fois
    "B5:2 D6:2",                      "A5:4",                  # 12 : la melodie tient
    "E6:1 C6:1 G5:2",                 "B5:1 D6:1 B5:2",        # le bourdon est sur re
    "F#6:2 D6:2",                     "E6:1 B5:1 G5:2",
    "C6:1 E6:1 G6:2",                 "F#6:1 A6:1 D6:2",
    "E6:1.5 C6:.5 A5:2",              "B5:2 E5:2",
    "A5:1 C6:1 E6:2",                 "B5:2 G5:2",             # le bourdon revient sur mi
    "D6:2 F#6:2",                     "E6:4",                  # 24 : la melodie tient
    "G6:1 E6:1 C6:2",                 "D6:1.5 B5:.5 G5:2",
    "E5:1 G5:1 A5:2",                 "A5:4",
]
assert len(MEL) == BARS

CTR = [
    "A4:2 C5:2",                      "E4:2 A4:2",
    "B4:2 D4:2",                      "G4:2 B4:2",
    "C5:2 E4:2",                      "B4:2 G4:2",
    "A4:.5 B4:.5 C5:1 E4:1 A4:1",     "A4:2 F#4:2",            # 7 : la reponse
    "A4:2 C5:2",                      "G4:2 E4:2",
    "D4:2 B4:2",                      "A4:.5 B4:.5 C5:1 E4:1 C5:1",  # 12 : la reponse
    "E4:2 G4:2",                      "D4:2 B4:2",
    "F#4:2 D4:2",                     "E4:2 B4:2",
    "G4:2 C5:2",                      "A4:2 D4:2",
    "C5:2 E4:2",                      "A4:2 E4:2",
    "A4:2 C5:2",                      "B4:2 G4:2",
    "D4:2 F#4:2",                     "A4:.5 B4:.5 C5:1 E4:1 G4:1",  # 24 : la reponse
    "C5:2 E4:2",                      "G4:2 E4:2",
    "B4:2 D4:2",                      "A4:2 E4:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("A", "dorien", BPM, BAR, "Le Pont sur la Croupie")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # le courant : croches, doubles au plus fort du B, croches a nouveau
    arp = arpeggio(CH[0:14], 0, DU[0:14], 0.5, (0, 1, 2, 1), lo=57)
    arp += arpeggio(CH[14:16], BAR * 14, DU[14:16], 0.25, (0, 1, 2, 1), lo=57)
    arp += arpeggio(CH[16:], BAR * 16, DU[16:], 0.5, (0, 1, 2, 1), lo=57)
    p.add("arpege", arp)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    p.add("basse", progression(CH, 0, DU, [(0, 2), (-1, 1), (0, 1)], lo=48))

    # LA PEDALE QUI BOUGE : mi, puis re pendant tout le B, puis mi
    p.add("bourdon", pedal(midi("E2"), 0, BAR * 12, retrig=BAR * 4)
                     + pedal(midi("D2"), BAR * 12, BAR * 8, retrig=BAR * 4)
                     + pedal(midi("E2"), BAR * 20, BAR * 8, retrig=BAR * 4))
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("riviere.mid"))
