#!/usr/bin/env python3
"""« Deux Paires d'Yeux » — clairiere 4, les deux loups.

Variation de la couleur `nord`. Le procede de la zone est l'ostinato fixe ;
ici il y en a **deux**, une cellule haute et une cellule basse, qui se relaient
de mesure en mesure et ne bougent jamais d'une note. Deux betes qui se
repondent d'un bord a l'autre de la clairiere pendant que les accords, eux, se
deplacent.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `si re fa# re si / do# si fa#` : la montee
  d'un trait puis la retombee par le demi-ton. Enonce trois fois ;
- **une reponse** : aux mesures 8, 18 et 28 le chant tient et c'est la bete de
  droite — voix 3 — qui repond. Les deux paires d'yeux ne regardent jamais
  ensemble ;
- **la surprise** : la **mesure 12 n'a que deux temps**. Tout le morceau est a
  4/4 sauf elle : on recule d'un pas, la phrase boite, et le B tombe une demi-
  mesure trop tot. C'est la seule mesure impaire des douze clairieres. Second
  coup, mesure 20 : **fa diese majeur**, un la diese hors du mode — les crocs.
  Puis un temps et demi de silence general avant le A' ;
- **le rythme harmonique varie** : grille a la demi-mesure, un accord par
  mesure a l'affut, deux des que la bete bouge ;
- **la batterie** : le coeur qui bat. Deux toms sourds dans l'intro, une
  grosse caisse a l'affut au A, un galop au B, la marche du recul au A'. La
  voix 5 lui revient : le bourdon de fa diese a cede la place, et c'est mieux
  ainsi — un affut ne bourdonne pas, il bat.

28 mesures dont une a 2/4, 110 temps, 38,4 s a 172 a la noire.
Forme intro(4) - A(8) - B(8) - A'(8).

    python3 loups.py && python3 ../../../midi_to_mb.py loups.mid \\
        WOLVES.MB.BIN --bpm 172 --max 2304 --wav LOUPS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 172, 4, 28
BEATS = [BAR] * BARS
BEATS[11] = 2                              # la mesure boiteuse : on recule d'un pas
T = [sum(BEATS[:i]) for i in range(BARS)]  # le debut de chaque mesure
LEN = sum(BEATS)
HALF = BAR / 2.0
SILENCE = (T[19] + 2.5, T[20])             # le temps et demi ou tout se tait

GRID = [
    ("Bm", "Bm"), ("Bm", "Bm"), ("G", "G"), ("F#m", "F#m"),    # intro — le silence
    ("Bm", "Bm"), ("G", "D"), ("Bm", "Bm"), ("Em", "A"),       # A — les deux betes
    ("Bm", "Bm"), ("G", "D"), ("Em", "F#m"), ("A",),           # ← la mesure boiteuse
    ("Em", "Em"), ("Bm", "Bm"), ("G", "G"), ("D", "A"),        # B — le buisson
    ("F#m", "F#m"), ("D", "D"), ("G", "G"), ("F#", "F#"),      # ← les crocs
    ("Bm", "Bm"), ("G", "D"), ("Bm", "Bm"), ("Em", "A"),       # A' — on recule
    ("G", "G"), ("Em", "F#m"), ("D", "A"), ("Bm", "Bm"),
]
assert len(GRID) == BARS
assert all(2 * len(g) == BEATS[i] for i, g in enumerate(GRID))
CH = [c for pair in GRID for c in pair]
STARTS = []                                # indice du premier accord de la mesure
_k = 0
for _g in GRID:
    STARTS.append(_k)
    _k += len(_g)
STARTS.append(_k)

H1 = "B5:.5 D6:.5 F#6:1 D6:1 B5:1"         # le crochet
H2 = "C#6:2 B5:1 F#5:1"

MEL = [
    "F#5:2 B5:2",                     "D6:1 B5:1 F#5:2",       # intro
    "G5:2 D6:2",                      "C#6:1 A5:1 F#5:2",
    H1,                               H2,                      # A
    "B5:1 D6:1 F#6:1 D6:1",           "E6:4",                  # ← la reponse
    H1,                               H2,
    "G6:1 E6:1 B5:2",                 "F#6:1 D6:1",            # ← 2/4
    "E6:1 B5:1 G5:2",                 "F#6:1 D6:1 B5:2",       # B — le buisson
    "G6:1 D6:1 B5:2",                 "A5:1 D6:1 F#6:2",
    "C#6:1 F#6:1 A6:2",               "A5:4",                  # ← la reponse
    "B5:1 D6:1 G6:2",                 "A#5:1 C#6:1 F#6:2",     # ← la diese
    H1,                               H2,                      # A'
    "D6:1 B5:1 F#6:2",                "E6:1 C#6:1 A5:2",
    "G6:1 D6:1 B5:2",                 "E6:1 G6:1 B5:2",
    "F#6:1 D6:1 A5:2",                "B5:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "D4:4",                           "B3:4",
    "G4:4",                           "A4:4",
    "F#4:2 D4:2",                     "B3:2 G4:2",
    "F#4:2 A4:2",                     "E4:2 C#4:2",
    "D4:2 B3:2",                      "G4:2 E4:2",
    "B3:2 C#4:2",                     "E4:2",
    "E4:2 G4:2",                      "F#4:2 D4:2",
    "B3:2 G4:2",                      "A4:2 F#4:2",
    "A4:2 C#4:2",                     "F#4:2 D4:2",
    "D4:2 B3:2",                      "A#3:2 C#4:2",
    "F#4:2 D4:2",                     "B3:2 G4:2",
    "F#4:2 A4:2",                     "E4:2 C#4:2",
    "G4:2 B3:2",                      "E4:2 C#4:2",
    "A4:2 F#4:2",                     "D4:2 B3:2",
]
assert len(CTR) == BARS

for _i, _s in enumerate(MEL):
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split())
               - BEATS[_i]) < 1e-6, _s
for _i, _s in enumerate(CTR):
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split())
               - BEATS[_i]) < 1e-6, _s

HAUT = [midi("B4"), midi("F#4"), midi("A4"), midi("F#4")]      # le premier loup
BAS = [midi("E4"), midi("B3"), midi("D4"), midi("B3")]         # le second

REPONSE = {7:  "F#4:1 B4:1 D5:1.5 C#5:.5",
           17: "D5:1 A4:1 F#4:1 A4:1",
           27: "B4:1 F#4:1 D4:1 B4:1"}


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


def bars(specs):
    """Les mesures posees sur la carte des temps, la boiteuse comprise."""
    out = []
    for i, s in enumerate(specs):
        out += line(s, T[i])
    return out


def build():
    p = Piece("B", "eolien", BPM, BAR, "Deux Paires d'Yeux")
    a, b = SILENCE

    p.add("melodie", taire(bars(MEL), a, b))

    # les deux betes se relaient une mesure sur deux, sans jamais bouger
    yeux = []
    for i in range(BARS):
        if i in REPONSE:
            yeux += line(REPONSE[i], T[i])
        else:
            yeux += ostinato(HAUT if i % 2 == 0 else BAS,
                             1.0 if i < 4 else 0.5, T[i], BEATS[i], gap=0.08)
    p.add("ostinato", taire(yeux, a, b))

    p.add("contre-chant", taire(sec(bars(CTR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # la basse rode : fondamentale et quinte grave, seches, jamais tenues
    bas = (progression(CH[:STARTS[4]], 0, HALF, [(0, 1.5), (None, .5)], lo=48)
           + progression(CH[STARTS[4]:STARTS[12]], T[4], HALF,
                         [(0, 1), (-1, 1)], lo=48)
           + progression(CH[STARTS[12]:], T[12], HALF, [(0, 1), (-1, 1)], lo=48))
    p.add("basse", taire(sec(bas, 0.40), a, b))

    # le coeur qui bat, puis le galop, puis la marche du recul
    p.add_drums("T.......", t0=0, length=BAR * 4)
    p.add_drums("K...T...", t0=T[4], length=BAR * 8)
    p.add_drums([(0, "K"), (1, "S")], t0=T[11])
    p.add_drums("K.K.S...", t0=T[12], length=BAR * 7 + 2)
    p.add_drums([(0, "C", 7)], t0=T[12])
    p.add_drums("K..T..S.", t0=T[20], length=BAR * 8)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("loups.mid"))
