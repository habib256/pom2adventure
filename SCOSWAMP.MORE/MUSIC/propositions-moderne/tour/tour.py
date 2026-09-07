#!/usr/bin/env python3
"""« La Tour de Stratagus » — les quatorze pages de la tour. Sol mineur
harmonique, 125 a la noire.

Presque pas de batterie : une grosse caisse toutes les deux mesures, rien
d'autre — un pas dans un escalier de pierre, pas un rythme. Une cymbale ouvre
chaque partie, et trois toms montent avant la coda. C'est la voix d'accords
tenus qui a cede sa place ; le bourdon reste, parce que c'est lui qui fait le
morceau.

La SURPRISE est la pedale : **re** pendant tout le A — la dominante, la tour
n'est jamais posee — puis **mi bemol** aux mesures 13 a 20, un demi-ton plus
haut, sous une harmonie qui ne bouge pas. Rien n'a change et tout a change.
Elle redescend sur re mesure 21 et la coda peut cadencer.

La seconde augmentee mi bemol-fa diese du mineur harmonique est la seule
sensible du dossier : c'est la magie, et elle est ecrite, pas suggeree.

Le CROCHET (sol-re qui monte d'une quinte, mi bemol-re-do qui redescend) est
enonce mesures 5-6 puis **repris mesures 9-10** sur mi bemol au lieu de do
mineur. QUESTION ET REPONSE mesures 7, 12 et 23.

24 mesures a 4/4, 46,5 s.

    python3 tour.py && python3 ../../midi_to_mb.py tour.mid \\
        TOWER.MB.BIN --bpm 125 --max 2304 --wav TOUR.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 125, 4, 24
LEN = BAR * BARS

CH = (["Gm", "Eb", "D"] + ["Gm", "Cm", "D", "Gm"] + ["Gm", "Eb", "Cm", "D", "Gm"]
      + ["Eb", "Bb", "Cm", "D", "Eb", "Cm", "D"]
      + ["Gm", "Eb", "D", "Gm"])
DU = ([8, 4, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [8, 4, 4, 4, 4, 4, 4]
      + [4, 4, 4, 4])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "D5:4",                           "D5:2 G5:2",
    "Bb5:2 G5:2",                     "F#5:2 A5:2",
    "G5:2 D6:2",                      "Eb6:1.5 D6:.5 C6:2",    # le crochet
    "A5:4",                           "G5:1 Bb5:1 D6:2",       # 7 : la melodie tient
    "G5:2 D6:2",                      "Eb6:1.5 D6:.5 Bb5:2",   # le crochet, 2e fois
    "C6:2 A5:2",                      "D6:4",                  # 12 : la melodie tient
    "Bb5:1 Eb6:1 G6:2",               "F6:2 D6:2",             # la pedale est sur mi bemol
    "D6:2 F6:2",                      "Eb6:1.5 D6:.5 C6:2",
    "A5:1 D6:1 F#6:2",                "G6:2 Eb6:2",
    "C6:1 Eb6:1 G6:2",                "F#6:1 A6:1 D6:2",
    "G6:2 D6:2",                      "Bb5:1 Eb6:1 G6:2",      # la pedale redescend
    "F#6:1.5 A6:.5 D6:2",             "G5:4",
]
assert len(MEL) == BARS

CTR = [
    "G4:2 Bb4:2",                     "D4:2 Bb4:2",
    "G4:2 Eb4:2",                     "F#4:2 A4:2",
    "D4:2 G4:2",                      "Eb4:2 C5:2",
    "A4:.5 G4:.5 F#4:1 D4:1 A4:1",    "G4:2 D4:2",             # 7 : la reponse
    "Bb4:2 G4:2",                     "Eb4:2 Bb4:2",
    "C5:2 G4:2",                      "D4:.5 Eb4:.5 D4:1 Bb4:1 G4:1",  # 12
    "Eb4:2 G4:2",                     "Bb4:2 D4:2",
    "D4:2 F4:2",                      "Eb4:2 C5:2",
    "A4:2 F#4:2",                     "G4:2 Eb4:2",
    "C5:2 G4:2",                      "F#4:2 A4:2",
    "G4:2 D4:2",                      "Bb4:2 Eb4:2",
    "A4:.5 G4:.5 F#4:1 A4:1 D4:1",    "G4:2 D4:2",             # 23 : la reponse
]
assert len(CTR) == BARS


def build():
    p = Piece("G", "mineur_h", BPM, BAR, "La Tour de Stratagus")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    # la marche : blanches a l'intro, noires ensuite — rien ne court jamais
    arp = arpeggio(CH[0:3], 0, DU[0:3], 2.0, (0, 1, 2, 1), lo=50)
    arp += arpeggio(CH[3:], BAR * 4, DU[3:], 1.0, (0, 1, 2, 1), lo=50)
    p.add("arpege", arp)
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", progression(CH, 0, DU, [(0, 2), (-1, 2)], lo=45))

    # LA PEDALE QUI MONTE D'UN DEMI-TON : re, mi bemol, re
    p.add("bourdon", pedal(midi("D2"), 0, BAR * 12, retrig=BAR * 4)
                     + pedal(midi("Eb2"), BAR * 12, BAR * 8, retrig=BAR * 4)
                     + pedal(midi("D2"), BAR * 20, BAR * 4, retrig=BAR * 4))

    # un pas toutes les deux mesures, et rien de plus
    p.add_drums("K.......", step=1.0, t0=0, length=LEN)
    p.add_drums([(0, "C")], t0=BAR * 4)
    p.add_drums([(0, "C")], t0=BAR * 12)
    p.add_drums([(0, "T"), (1, "T"), (1.5, "T"), (2, "C")], t0=BAR * 19)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("tour.mid"))
