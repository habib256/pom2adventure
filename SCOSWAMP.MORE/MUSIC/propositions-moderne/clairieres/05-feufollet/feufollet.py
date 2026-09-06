#!/usr/bin/env python3
"""« La Lumiere qui Recule » — clairiere 5, le Feu Follet a l'oree.

Variation de la couleur `nord`. L'ostinato de la zone tombe toujours au meme
endroit de la mesure ; celui-ci est fixe **en notes** et jamais au meme
endroit, parce que sa cellule fait **cinq croches** dans une mesure a quatre
temps. A chaque tour la figure recule d'une croche, comme le Feu Follet
« recule de quelques metres » chaque fois qu'on avance, et elle ne retombe
d'aplomb qu'une fois toutes les cinq mesures.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `sol sib re' do' sib / la sol re` : il monte
  a la quinte et redescend sans jamais toucher la tonique en haut. Enonce
  trois fois ;
- **une reponse** : aux mesures 10, 18 et 26 le chant tient et la lueur —
  voix 3, a droite — repond a sa place. On appelle a gauche, ca repond a
  droite, et c'est toujours plus loin ;
- **la surprise** : mesures 15-16, la cellule est jouee **a l'envers**, note
  pour note. La lueur revient sur ses pas, une fois, et c'est la seule fois du
  morceau. Puis, mesure 18, un temps et demi de **silence general** — elle
  s'eteint — avant que tout reparte ensemble ;
- **la lueur s'immobilise** aux six dernieres mesures : la cellule passe a
  quatre croches, elle retombe d'aplomb, on sait enfin ou elle est. C'est le
  piege ;
- **le rythme harmonique varie** : grille a la demi-mesure ; l'oree tient un
  accord par mesure, le sentier en prend deux ;
- **la batterie** : elle recule aussi. Le charleston ouvert et la grosse
  caisse battent **toutes les cinq croches**, sur la meme grille que la
  cellule, donc jamais sur le temps ; ils ne tombent d'aplomb avec la caisse
  claire qu'une mesure sur cinq. Rien dans l'intro. La voix 5 lui revient, le
  bourdon de re a cede la place.

Sol mineur eolien, 154 a la noire, 26 mesures a 4/4, 40,5 s.
Forme intro(4) - A(8) - B(8) - A'(6).

    python3 feufollet.py && python3 ../../../midi_to_mb.py feufollet.mid \\
        WILLOWISP.MB.BIN --bpm 154 --max 2304 --wav FEUFOLLET.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 154, 4, 26
LEN = BAR * BARS
HALF = BAR / 2.0
STOP = BAR * 20                            # la lueur s'immobilise, mesure 21
SILENCE = (BAR * 17 + 2.5, BAR * 18)       # elle s'eteint un temps et demi

GRID = [
    ("Gm", "Gm"), ("Eb", "Eb"), ("Cm", "Cm"), ("Dm", "Dm"),    # intro — l'oree
    ("Gm", "Gm"), ("Bb", "F"), ("Eb", "Eb"), ("Dm", "Gm"),     # A — la lueur
    ("Gm", "Gm"), ("Bb", "F"), ("Cm", "Eb"), ("Dm", "Dm"),
    ("Cm", "Cm"), ("Gm", "Gm"), ("Eb", "Bb"), ("F", "F"),      # B — le sentier
    ("Bb", "Bb"), ("Eb", "Eb"), ("Cm", "D"), ("Dm", "Dm"),     # ← re majeur
    ("Gm", "Gm"), ("Eb", "Bb"), ("Cm", "Cm"), ("F", "Dm"),     # A' — le piege
    ("Eb", "Dm"), ("Gm", "Gm"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "G5:.5 Bb5:.5 D6:1 C6:1 Bb5:1"        # le crochet
H2 = "A5:2 G5:1 D5:1"

MEL = [
    "G5:2 Bb5:2",                     "D6:1 Bb5:1 G5:2",       # intro
    "Eb6:1 C6:1 G5:2",                "A5:1 D6:1 F6:2",
    H1,                               H2,                      # A
    "Bb5:1 Eb6:1 G6:2",               "F6:1 D6:1 A5:2",
    H1,                               H2,
    "Bb5:1 G6:1 Eb6:2",               "D6:4",                  # ← la reponse
    "C6:1 Eb6:1 G6:2",                "F6:1 D6:1 Bb5:2",       # B — le sentier
    "G6:1 Eb6:1 Bb5:2",               "D6:1 F6:1 Bb6:2",       # ← la cellule a l'envers
    "A6:1 F6:1 C6:2",                 "F#6:1 A6:1 D6:2",       # ← fa diese
    "Bb5:1 Eb6:1 G6:1.5 F6:.5",       "D6:4",                  # ← la reponse
    "G6:1 D6:1 Bb5:2",                "Eb6:1 Bb5:1 G5:2",      # A' — le piege
    "C6:1 Eb6:1 G6:2",                "F6:1 C6:1 A5:2",
    "Eb6:1 D6:1 Bb5:1 D6:1",          "G5:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "Bb3:4",                          "G4:4",
    "C4:4",                           "A3:4",
    "D4:2 Bb3:2",                     "F4:2 D4:2",
    "Eb4:2 G4:2",                     "F4:2 A3:2",
    "Bb3:2 G4:2",                     "Eb4:2 C4:2",
    "G4:2 Bb3:2",                     "A3:2 F4:2",
    "C4:2 G4:2",                      "D4:2 Bb3:2",
    "Eb4:2 G4:2",                     "D4:2 F4:2",
    "F4:2 Bb3:2",                     "G4:2 Eb4:2",
    "C4:2 F#4:2",                     "A3:2 D4:2",
    "Bb3:2 D4:2",                     "G4:2 Eb4:2",
    "C4:2 Eb4:2",                     "A3:2 C4:2",
    "G4:2 F4:2",                      "Bb3:2 D4:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

# cinq croches : la lueur ne retombe jamais deux fois sur le meme temps
LUEUR = [midi("D4"), midi("G4"), midi("Bb4"), midi("A4"), midi("F4")]
ARRIERE = LUEUR[::-1]                      # elle revient sur ses pas
ATTENTE = [midi("D4"), midi("G4"), midi("Bb4"), midi("G4")]

REPONSE = {9:  "D4:1 G4:1 Bb4:1.5 A4:.5",
           17: "F4:1 Bb4:1 D5:1 Bb4:1",
           25: "D5:1 Bb4:1 G4:1 D4:1"}


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
    p = Piece("G", "eolien", BPM, BAR, "La Lumiere qui Recule")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # la lueur : cinq croches, deux mesures a l'envers, puis quatre croches
    lueur = []
    for i in range(BARS):
        if i in REPONSE:
            lueur += line(REPONSE[i], i * BAR)
            continue
        if i < 4:
            cell, pas = LUEUR, 1.0
        elif 14 <= i <= 15:
            cell, pas = ARRIERE, 0.5
        elif i * BAR >= STOP:
            cell, pas = ATTENTE, 0.5
        else:
            cell, pas = LUEUR, 0.5
        lueur += ostinato(cell, pas, i * BAR, BAR, gap=0.10)
    p.add("lueur", taire(lueur, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # le sol est mou : la basse pose et lache, elle ne marche jamais
    bas = (progression(CH[:24], 0, HALF, [(0, 1.5), (None, .5)], lo=45)
           + progression(CH[24:40], BAR * 12, HALF, [(0, 1.2), (-1, .8)], lo=45)
           + progression(CH[40:], BAR * 20, HALF, [(0, 1.5), (None, .5)], lo=45))
    p.add("basse", taire(sec(bas, 0.30), a, b))

    # la batterie recule elle aussi : cinq croches, jamais sur le temps
    p.add_drums("O....", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K...S...", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K....", t0=BAR * 12, length=BAR * 5 + 2.5)
    p.add_drums("O....", t0=BAR * 12, length=BAR * 5 + 2.5)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K.H.S.H.", t0=BAR * 18, length=BAR * 8)        # d'aplomb : le piege
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("feufollet.mid"))
