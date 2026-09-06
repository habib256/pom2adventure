#!/usr/bin/env python3
"""« Il Est Interdit de Passer » — clairiere 7, le Geant.

Variation de la couleur `nord`. L'ostinato de la zone court en croches ;
celui-ci **marche en noires** — quatre pas par mesure, do - sol - mi bemol -
sol, l'empreinte de cinquante centimetres de la page 275. Il ne double en
croches que dans le B, quand la massue tourne, et il retombe en noires pour le
A'. C'est tout le crescendo du morceau : le lecteur n'a pas de volume par note,
on ne peut serrer que la densite.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `do mib sol lab sol / sol mib do` : la montee
  du geant, le lab qui bute, la retombee. Enonce trois fois, et c'est le seul
  motif du morceau que le chant repete tel quel ;
- **une reponse** : aux mesures 8, 12 et 24 le chant tient et l'empreinte —
  voix 3, a droite — repond a sa place. Une question a hauteur d'homme, une
  reponse a hauteur de geant ;
- **la surprise** : mesure 16, l'accord de **re bemol majeur**, le napolitain.
  Un demi-ton au-dessus de la tonique, en majeur, la ou tout le morceau est
  mineur : l'ombre tombe sur la clairiere. Puis mesure 18, **un temps et demi
  de silence general** — il s'arrete — et le A' repart sur un tutti ;
- **le rythme harmonique varie** : grille a la demi-mesure. Le geant tient un
  accord par mesure, la massue en prend deux ;
- **la batterie** : le pas. Grosse caisse au premier temps, tom au troisieme,
  et c'est tout — jusqu'au B, ou la massue tourne en croches et la caisse
  claire s'ajoute. Elle prend la voix 5 : le bourdon de do a cede la place, et
  la grosse caisse en tient lieu, ce qui est exactement son emploi ici.

Do mineur eolien, 138 a la noire — un geant ne court pas, mais quatre noires a
138 restent une marche. 24 mesures a 4/4, 41,7 s.
Forme intro(4) - A(8) - B(6) - A'(6).

    python3 geant.py && python3 ../../../midi_to_mb.py geant.mid \\
        GIANT.MB.BIN --bpm 138 --max 2304 --wav GEANT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 138, 4, 24
LEN = BAR * BARS
HALF = BAR / 2.0
MASSUE = (BAR * 12, BAR * 18)              # les six mesures ou la massue tourne
SILENCE = (BAR * 17 + 2.5, BAR * 18)       # il s'arrete

GRID = [
    ("Cm", "Cm"), ("Cm", "Cm"), ("Ab", "Ab"), ("Gm", "Gm"),    # intro — l'empreinte
    ("Cm", "Cm"), ("Ab", "Eb"), ("Cm", "Cm"), ("Fm", "Gm"),    # A — le Geant
    ("Cm", "Cm"), ("Ab", "Eb"), ("Fm", "Fm"), ("Gm", "Gm"),
    ("Eb", "Eb"), ("Bb", "Bb"), ("Fm", "Cm"), ("Db", "Db"),    # B — la massue
    ("Ab", "Ab"), ("Gm", "Gm"),
    ("Cm", "Cm"), ("Ab", "Eb"), ("Cm", "Cm"), ("Fm", "Gm"),    # A' — le passage
    ("Ab", "Gm"), ("Cm", "Cm"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "C5:1 Eb5:1 G5:1.5 Ab5:.5"            # le crochet : le lab qui bute
H2 = "G5:2 Eb5:1 C5:1"

MEL = [
    "C5:2 G5:2",                      "Eb5:1 C5:1 G5:2",       # intro
    "Ab5:2 Eb5:2",                    "G5:1 D5:1 Bb4:2",
    H1,                               H2,                      # A
    "Ab5:1 C6:1 Eb6:2",               "G5:4",                  # ← la reponse
    H1,                               H2,
    "F5:1 Ab5:1 C6:2",                "D6:4",                  # ← la reponse
    "Eb6:1 G6:1 Bb6:2",               "F6:1 D6:1 Bb5:2",       # B — la massue
    "Ab6:1 F6:1 C6:2",                "Db6:1 F6:1 Ab6:2",      # ← le napolitain
    "C6:1 Ab5:1 Eb6:2",               "D6:1 Bb5:1 G5:2",
    H1,                               H2,                      # A' — le passage
    "Eb6:1 C6:1 Ab5:2",               "F5:1 Ab5:1 D6:2",
    "Eb5:1 G5:1 Bb5:1 Ab5:1",         "C5:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "Eb4:4",                          "C4:4",
    "Ab3:4",                          "Bb3:4",
    "G3:2 Eb4:2",                     "C4:2 Ab3:2",
    "Eb4:2 G3:2",                     "Ab3:2 Bb3:2",
    "G3:2 Eb4:2",                     "C4:2 G3:2",
    "Ab3:2 F4:2",                     "D4:2 Bb3:2",
    "G3:2 Bb3:2",                     "F4:2 D4:2",
    "C4:2 Ab3:2",                     "F4:2 Ab3:2",
    "Eb4:2 C4:2",                     "D4:2 Bb3:2",
    "G3:2 Eb4:2",                     "C4:2 Ab3:2",
    "Eb4:2 G3:2",                     "Ab3:2 Bb3:2",
    "C4:2 D4:2",                      "G3:2 Eb4:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

PAS = [midi("C4"), midi("G4"), midi("Eb4"), midi("G4")]        # l'empreinte
OMBRE = [midi("Db4"), midi("Ab4"), midi("F4"), midi("Ab4")]    # le napolitain

REPONSE = {7:  "C4:1 Eb4:1 G4:1.5 Ab4:.5",
           11: "Bb4:1 G4:1 D4:1 G4:1",
           23: "G4:1 Eb4:1 C4:2"}


def tenue(chords, per, lo, which=1, t0=0.0):
    """Le lit d'accords : une note tenue, fusionnee quand l'accord se repete."""
    out = []
    for i, c in enumerate(chords):
        n = pick(voicing(c, lo), which)
        if out and out[-1][0] == n:
            out[-1][2] += per
        else:
            out.append([n, t0 + i * per, per])
    return [tuple(e) for e in out]


def sec(part, coupe=0.30):
    """Detache : la note lache avant la suivante."""
    return [(n, t, max(d - coupe, 0.2)) for n, t, d in part]


def taire(part, a, b):
    """Le silence general : rien ne sonne entre `a` et `b`, tout repart ensemble."""
    out = []
    for n, t, d in part:
        if a - 1e-6 <= t < b - 1e-6:
            continue
        if t < a - 1e-6 < t + d:
            d = a - t
        out.append((n, t, d))
    return out


def build():
    p = Piece("C", "eolien", BPM, BAR, "Il Est Interdit de Passer")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    pas = []
    for i in range(BARS):
        if i in REPONSE:
            pas += line(REPONSE[i], i * BAR)
        else:
            cell = OMBRE if i == 15 else PAS
            vite = MASSUE[0] <= i * BAR < MASSUE[1]
            pas += ostinato(cell, 0.5 if vite else 1.0, i * BAR, BAR)
    p.add("empreinte", taire(pas, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # basse pesante : elle pose la fondamentale et la lache, elle ne marche pas
    bas = (progression(CH[:24], 0, HALF, [(0, 1.5), (None, .5)], lo=45)
           + progression(CH[24:36], BAR * 12, HALF, [(0, 1.2), (-1, .8)], lo=45)
           + progression(CH[36:], BAR * 18, HALF, [(0, 1.5), (None, .5)], lo=45))
    p.add("basse", taire(sec(bas, 0.30), a, b))

    # le pas : grosse caisse au premier temps, tom au troisieme
    p.add_drums([(0, "K", 6), (BAR * 2, "K", 6)])
    p.add_drums("K.T.", step=1.0, t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.T.K.TS", t0=BAR * 12, length=BAR * 5 + 2.5)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("....H...", t0=BAR * 4, length=BAR * 8)         # un souffle par mesure
    p.add_drums("K.TS", step=1.0, t0=BAR * 18, length=BAR * 4)
    p.add_drums("K.T.K.TS", t0=BAR * 22, length=BAR * 2)        # le dernier pas
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("geant.mid"))
