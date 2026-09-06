#!/usr/bin/env python3
"""« Ce qui Sort du Bassin » — clairiere 9, le bassin de Vase.

Variation de la couleur `danger`. Les deux marques de la zone sont le demi-ton
phrygien pose au-dessus de la tonique et le crescendo obtenu par la densite, la
carte n'ayant pas de volume par note. Ici les deux ne font qu'une chose : la
cellule **re - mi bemol - re - fa** ne change pas une note du morceau, et se
resserre trois fois — blanches, puis noires, puis croches. C'est la fange qui
« parait se contracter, puis se soulever et se repandre sur le sentier ».

Ce qui a change a la revision :

- **un crochet** de deux mesures, `la sib la fa re' / mib' re'` : le demi-ton
  phrygien pris a l'endroit puis a l'envers, deux fois de suite. Enonce trois
  fois. C'est la meme cellule que la fange, chantee ;
- **une reponse** : aux mesures 12, 20 et 26 le chant tient et la fange —
  voix 3, a droite — repond a sa place ;
- **la surprise, et c'est le bourdon** : il ne bouge pas de tout le morceau
  sauf pendant le B, ou il monte **d'un demi-ton, de re a mi bemol**, et y
  reste huit mesures. Le sol lui-meme s'est deplace. Il redescend a la mesure
  21 sans qu'on l'entende arriver. Juste avant le B, mesure 12, **un temps et
  demi de silence general** : le bassin retient son souffle ;
- **la voix des accords a cede la place, pas le bourdon.** C'est la regle du
  `danger` : le bourdon fait le caractere de la piece, on ne le retire pas. Il
  reste donc cinq parties de hauteur — chant, fange, contre-chant, basse,
  bourdon — et l'harmonie est portee par la basse et le contre-chant. La basse
  passe a droite, sous la fange ; le bourdon garde le fond a gauche ;
- **la batterie** : un coeur qui bat sourd. Deux grosses caisses par mesure et
  rien d'autre pendant tout le A ; une cymbale au moment ou la fange se
  souleve ; des toms qui doublent au B ; et le battement seul pour finir. Aucun
  charleston : rien ne brille dans deux metres de vase.

Re phrygien, 138 a la noire, 26 mesures a 4/4, 45,2 s.
Forme intro(4) - A(8) - B(8) - A'(6).

    python3 vase.py && python3 ../../../midi_to_mb.py vase.mid \\
        MUD.MB.BIN --bpm 138 --max 2304 --wav VASE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 138, 4, 26
LEN = BAR * BARS
HALF = BAR / 2.0
SERRE = (BAR * 6, BAR * 16)                # les deux resserrements de la fange
PEDALE = (BAR * 12, BAR * 20)              # le bourdon monte d'un demi-ton
SILENCE = (BAR * 11 + 2.5, BAR * 12)       # le bassin retient son souffle

GRID = [
    ("Dm", "Dm"), ("Dm", "Dm"), ("Eb", "Eb"), ("Dm", "Dm"),    # intro — le bassin
    ("Dm", "Dm"), ("Eb", "Eb"), ("Dm", "Cm"), ("Bb", "Bb"),    # A — la Vase
    ("Dm", "Dm"), ("Eb", "Eb"), ("Cm", "Bb"), ("Dm", "Dm"),
    ("Gm", "Gm"), ("Eb", "Eb"), ("Bb", "F"), ("Gm", "Gm"),     # B — elle se souleve
    ("Cm", "Cm"), ("Eb", "Bb"), ("Eb", "Eb"), ("Dm", "Dm"),
    ("Dm", "Dm"), ("Eb", "Eb"), ("Cm", "Bb"), ("Eb", "Eb"),    # A' — elle rampe
    ("Dm", "Dm"), ("Dm", "Dm"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "A5:1 Bb5:.5 A5:.5 F5:1 D6:1"         # le crochet : le demi-ton chante
H2 = "Eb6:2 D6:2"

MEL = [
    "A5:4",                           "A5:2 F5:2",             # intro
    "Bb5:2 A5:2",                     "A5:2 F5:2",
    H1,                               H2,                      # A
    "A5:1 D6:1 F6:2",                 "Eb6:1 C6:1 G5:2",
    H1,                               H2,
    "F6:1 D6:1 Bb5:2",                "A5:4",                  # ← la reponse
    "G5:1 Bb5:1 D6:2",                "Eb6:1 Bb5:1 G6:2",      # B — elle se souleve
    "F6:1 D6:1 Bb6:2",                "A6:1 F6:1 D6:2",
    "G6:1 Eb6:1 C6:2",                "Bb5:1 Eb6:1 G6:2",
    "Eb6:.5 D6:.5 Bb5:1 G5:2",        "D6:4",                  # ← la reponse
    H1,                               H2,                      # A' — elle rampe
    "Eb6:1 C6:1 G5:2",                "F6:1 D6:1 Bb5:2",
    "Eb6:.5 D6:.5 Bb5:1 F6:2",        "Eb6:1 D6:3",            # ← la reponse
]
assert len(MEL) == BARS

# le contre-chant tient l'harmonie a lui seul : il est donc plein, et grave
CTR = [
    "F3:4",                           "A3:4",
    "G3:4",                           "F3:4",
    "A3:2 F3:2",                      "G3:2 Bb3:2",
    "A3:2 C4:2",                      "D4:2 Bb3:2",
    "A3:2 F3:2",                      "G3:2 Bb3:2",
    "C4:2 D4:2",                      "A3:2 F3:2",
    "Bb3:2 D4:2",                     "G3:2 Bb3:2",
    "F3:2 A3:2",                      "Bb3:2 D4:2",
    "C4:2 Eb4:2",                     "Bb3:2 G3:2",
    "G3:2 Bb3:2",                     "A3:2 F3:2",
    "A3:2 F3:2",                      "G3:2 Bb3:2",
    "C4:2 D4:2",                      "Bb3:2 G3:2",
    "A3:2 F3:2",                      "F3:2 A3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

# re - mi bemol - re - fa : le demi-ton phrygien, et rien d'autre
FANGE = [midi("D4"), midi("Eb4"), midi("D4"), midi("F4")]

REPONSE = {11: "D4:1 Eb4:1 D4:1 F4:1",
           19: "F4:1 Eb4:1 D4:1.5 Eb4:.5",
           25: "Eb4:1 D4:1 F4:1 D4:1"}


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
    p = Piece("D", "phrygien", BPM, BAR, "Ce qui Sort du Bassin")
    a, b = SILENCE
    s1, s2 = SERRE
    q1, q2 = PEDALE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # la fange : elle respire, elle se contracte, elle se repand
    fange = (ostinato(FANGE, 2.0, 0, s1)
             + ostinato(FANGE, 1.0, s1, s2 - s1)
             + ostinato(FANGE, 0.5, s2, LEN - s2))
    fange = [e for e in fange if int(e[1] // BAR) not in REPONSE]
    for i, spec in REPONSE.items():
        fange += line(spec, i * BAR)
    p.add("fange", taire(fange, a, b))

    p.add("contre-chant", taire(lines(CTR, 0, bar=BAR), a, b))

    # la basse tient : deux metres de vase ne marchent pas, ils pesent. Elle se
    # resserre au B en meme temps que la fange — c'est le crescendo par la densite
    bas = (progression(CH[:24], 0, HALF, [(0, 2)], lo=45)
           + progression(CH[24:40], BAR * 12, HALF, [(0, 1), (0, 1)], lo=45)
           + progression(CH[40:], BAR * 20, HALF, [(0, 2)], lo=45))
    p.add("basse", taire(bas, a, b))

    # le bourdon ne bouge pas — sauf le demi-ton du B, qui deplace le sol
    p.add("bourdon", pedal(midi("D2"), 0, q1, retrig=BAR * 4)
                     + pedal(midi("Eb2"), q1, q2 - q1, retrig=BAR * 4)
                     + pedal(midi("D2"), q2, LEN - q2, retrig=BAR * 4))

    # le coeur qui bat sourd : deux grosses caisses par mesure, rien d'autre
    p.add_drums("K..K....", t0=0, length=BAR * 12)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K..K.K..", t0=BAR * 12, length=BAR * 8)
    p.add_drums("....T..T", t0=BAR * 12, length=BAR * 8)
    p.add_drums("K..K..K.", t0=BAR * 20, length=BAR * 6)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("vase.mid"))
