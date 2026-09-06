#!/usr/bin/env python3
"""« L'Amulette de Fleur » — clairiere 3, le Maitre des Jardins.

Variation de la couleur `nord` : meme ostinato fixe de quatre croches. Mais
c'est le seul endroit amical du Marais nord, et le mode passe de l'eolien au
**re dorien** : une seule note change, la sixte majeure, le si becarre, et
c'est elle la fleur. L'ostinato la touche a chaque tour — la - fa - **si** -
sol — et l'accord de sol majeur revient a chaque fois qu'on parle de l'amulette.

Ce qui a change a la revision :

- **un crochet** de deux mesures qui pose la fleur au sommet : `re fa la **si**
  la / sol la fa`. Enonce trois fois, deux au A, une au A' ;
- **une reponse** : aux mesures 10, 18 et 26 le chant tient une ronde et le
  secateur — voix 3, a droite — repond a sa place. Le jardinier taille pendant
  qu'on se tait ;
- **le rythme harmonique varie** : grille ecrite a la demi-mesure ; les mesures
  de repos tiennent un accord, celles de mouvement en ont deux ;
- **la surprise** : mesure 14, un **si bemol**. Le mode bascule du dorien a
  l'eolien pour quatre mesures, la fleur se referme, et le sol majeur ne
  revient qu'a la mesure 18 — juste avant **deux temps de silence general**
  d'ou tout repart ensemble pour le A' ;
- **la batterie** : la plus discrete des douze. Rien dans l'allee, deux
  charlestons par mesure au A, un tom sourd et une cymbale au B, une grosse
  caisse tres legere au A'. Une clairiere paisible n'a pas besoin d'etre
  battue ; elle a besoin d'etre mesuree. La voix 5 lui revient, le bourdon de
  re a cede la place.

26 mesures a 4/4, 43,3 s. Forme intro(2) - A(8) - B(8) - A'(8).

    python3 jardins.py && python3 ../../../midi_to_mb.py jardins.mid \\
        GARDENS.MB.BIN --bpm 144 --max 2304 --wav JARDINS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 144, 4, 26
LEN = BAR * BARS
HALF = BAR / 2.0
SILENCE = (BAR * 17 + 2.0, BAR * 18)       # les deux temps ou le jardin se tait

GRID = [
    ("Dm", "Dm"), ("G", "G"),                                  # intro — l'allee
    ("Dm", "Dm"), ("G", "G"), ("Dm", "Am"), ("F", "C"),        # A — le jardin
    ("Dm", "Dm"), ("G", "G"), ("Am", "C"), ("Dm", "Dm"),
    ("F", "F"), ("C", "C"), ("Dm", "Am"), ("Bb", "Bb"),        # B — l'amulette
    ("Gm", "Gm"), ("Bb", "F"), ("C", "C"), ("G", "G"),
    ("Dm", "Dm"), ("G", "G"), ("F", "C"), ("Am", "Dm"),        # A' — l'adieu
    ("Bb", "C"), ("G", "G"), ("Am", "C"), ("Dm", "Dm"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "D5:.5 F5:.5 A5:1 B5:1.5 A5:.5"       # le crochet : la fleur au sommet
H2 = "G5:1 A5:1 F5:2"

MEL = [
    "D5:2 F5:2",                      "A5:1 B5:1 A5:2",        # intro
    H1,                               H2,                      # A
    "A5:1 D6:1 C6:2",                 "B5:1.5 A5:.5 G5:2",
    H1,                               H2,
    "E6:1 C6:1 A5:2",                 "D6:4",                  # ← la reponse
    "F6:1 A6:1 F6:2",                 "E6:1 G6:1 C6:2",        # B — plus haut
    "D6:1 A5:1 F6:2",                 "Bb5:1 D6:1 F6:2",       # ← si bemol
    "Bb5:1 G5:1 D6:2",                "F6:1 D6:1 Bb5:2",
    "C6:1 E6:1 G6:2",                 "B5:4",                  # ← la reponse
    H1,                               H2,                      # A'
    "A5:1 C6:1 F6:2",                 "E6:1 A5:1 D6:2",
    "Bb5:1 D6:1 F6:2",                "B5:1 G5:1 D6:2",
    "E6:1 C6:1 A5:2",                 "D6:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "F4:4",                           "B3:4",
    "A3:2 D4:2",                      "G4:2 B3:2",
    "F4:2 D4:2",                      "E4:2 C4:2",
    "A3:2 F4:2",                      "B3:2 G4:2",
    "E4:2 C4:2",                      "F4:2 A3:2",
    "C4:2 A3:2",                      "E4:2 G4:2",
    "F4:2 D4:2",                      "D4:2 Bb3:2",
    "Bb3:2 G4:2",                     "D4:2 A3:2",
    "E4:2 G4:2",                      "D4:2 B3:2",
    "A3:2 D4:2",                      "G4:2 B3:2",
    "C4:2 A3:2",                      "E4:2 F4:2",
    "D4:2 Bb3:2",                     "B3:2 G4:2",
    "C4:2 E4:2",                      "F4:2 A3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

# la - fa - si - sol : le si becarre est la sixte majeure du mode, la fleur
GARDEN = [midi("A4"), midi("F4"), midi("B4"), midi("G4")]
FANEE = [midi("A4"), midi("F4"), midi("Bb4"), midi("G4")]      # la fleur refermee

REPONSE = {9:  "A4:1 D5:1 B4:1.5 A4:.5",
           17: "B4:1 G4:1 D5:1 B4:1",
           25: "A4:1 F4:1 D4:1 A4:1"}


def tenue(chords, per, lo, which=1, t0=0.0):
    """Le lit d'accords : une note tenue, fusionnee quand l'accord se repete —
    ce qui rend le rythme harmonique variable gratuit."""
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
    p = Piece("D", "dorien", BPM, BAR, "L'Amulette de Fleur")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # le secateur : quatre croches detachees, en noires dans l'allee, et le si
    # qui tombe en bemol pendant les quatre mesures ou la fleur se referme
    sect = []
    for i in range(BARS):
        if i in REPONSE:
            sect += line(REPONSE[i], i * BAR)
        else:
            cell = FANEE if 13 <= i <= 16 else GARDEN
            sect += ostinato(cell, 1.0 if i < 2 else 0.5, i * BAR, BAR, gap=0.12)
    p.add("secateur", taire(sect, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # ici on ne fuit pas : la basse tient, elle ne marche pas
    bas = (progression(CH[:20], 0, HALF, [(0, 1.5), (None, .5)], lo=45)
           + progression(CH[20:36], BAR * 10, HALF, [(0, 1.2), (None, .8)], lo=45)
           + progression(CH[36:], BAR * 18, HALF, [(0, 1.5), (-1, .5)], lo=45))
    p.add("basse", taire(sec(bas, 0.30), a, b))

    # la plus discrete des douze : deux charlestons, un tom, une cymbale
    p.add_drums("..H...H.", t0=BAR * 2, length=BAR * 8)
    p.add_drums("T...H...", t0=BAR * 10, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 10)
    p.add_drums([(2, "T"), (3, "T")], t0=BAR * 17)
    p.add_drums("K.H...H.", t0=BAR * 18, length=BAR * 8)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("jardins.mid"))
