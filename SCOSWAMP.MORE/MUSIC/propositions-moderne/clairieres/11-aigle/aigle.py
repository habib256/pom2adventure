#!/usr/bin/env python3
"""« Le Grand Nid » — clairiere 11, le nid de l'Aigle.

Variation de la couleur `nord`. L'ostinato de la zone bat des croches egales ;
celui-ci a un rythme, et c'est tout le sujet : **noire - croche - blanche -
croche**, fa diese - la - do diese - la. Un coup d'aile, un second, puis le vol
plane sur la note du haut pendant deux temps, et l'on retombe. L'Aigle
« vole au-dessus de la clairiere en vous observant attentivement », et il
tourne au meme rythme quoi qu'il arrive dessous.

Ce qui a change a la revision :

- **un crochet** qui chante le rythme du vol : `fa# la do#' si / la fa# mi`,
  noire - croche - blanche - croche, exactement la cellule, mais melodique.
  Enonce trois fois. Le chant et l'ostinato battent alors de la meme aile ;
- **une reponse** : aux mesures 8, 20 et 28 le chant tient une ronde et l'aile
  — voix 3, a droite — repond a sa place. C'est la seule facon d'entendre
  l'oiseau quand on ne le regarde pas ;
- **la surprise** : au B, mesures 17 a 20, **la cellule se retourne** — do
  diese, la, fa diese, la : il ne monte plus, il plonge. Et l'harmonie prend un
  **re diese**, la sixte majeure que le mode eolien n'a pas, sur un accord de
  si majeur. Puis mesure 20, **un temps et demi de silence general** : on perd
  l'oiseau de vue, et tout repart ensemble ;
- **le rythme harmonique varie** : grille a la demi-mesure ; l'arbre tient un
  accord par mesure, le nid en prend deux ;
- **la batterie** : la plus aeree des douze avec celle des Jardins. **Aucune
  caisse claire.** Une cymbale a chaque entree, un charleston ouvert tous les
  deux temps pour le vol plane, et trois grosses caisses seulement, celles du
  plongeon. La voix 5 lui revient, le bourdon de do diese a cede la place :
  entre la cellule tres haute et la basse tres grave, il ne manque rien.

Fa diese mineur eolien, 156 a la noire, 28 mesures a 4/4, 43,1 s.
Forme intro(4) - A(8) - B(8) - A'(8).

    python3 aigle.py && python3 ../../../midi_to_mb.py aigle.mid \\
        EAGLE.MB.BIN --bpm 156 --max 2304 --wav AIGLE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 156, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0
PLONGEON = (16, 20)                        # les mesures ou la cellule se retourne
SILENCE = (BAR * 19 + 2.5, BAR * 20)       # on perd l'oiseau de vue

GRID = [
    ("F#m", "F#m"), ("D", "D"), ("A", "A"), ("E", "E"),        # intro — l'arbre
    ("F#m", "F#m"), ("D", "A"), ("F#m", "F#m"), ("Bm", "E"),   # A — l'Aigle
    ("F#m", "F#m"), ("D", "A"), ("Bm", "C#m"), ("D", "E"),
    ("A", "A"), ("E", "E"), ("D", "A"), ("Bm", "Bm"),          # B — le nid
    ("D", "D"), ("B", "B"), ("E", "E"), ("C#m", "C#m"),        # ← si majeur, re diese
    ("F#m", "F#m"), ("D", "A"), ("F#m", "F#m"), ("Bm", "E"),   # A' — il s'eloigne
    ("D", "D"), ("Bm", "C#m"), ("D", "E"), ("F#m", "F#m"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "F#5:1 A5:.5 C#6:2 B5:.5"             # le crochet : le rythme du vol
H2 = "A5:2 F#5:1 E5:1"

MEL = [
    "F#5:2 C#6:2",                    "D6:2 A5:2",             # intro
    "C#6:2 E6:2",                     "B5:2 F#5:2",
    H1,                               H2,                      # A
    "D6:1 F#6:1 A6:2",                "B5:4",                  # ← la reponse
    H1,                               H2,
    "B5:1 D6:1 F#6:2",                "E6:1 A5:1 C#6:2",
    "A5:1 E6:1 C#6:2",                "B5:1 G#5:1 E5:2",       # B — le nid
    "D6:1 F#6:1 A6:2",                "E6:1 C#6:1 A5:2",
    "D6:1 A5:1 F#6:2",                "D#6:1 F#6:1 B5:2",      # ← re diese
    "E6:1 B5:1 G#5:2",                "C#6:4",                 # ← la reponse
    H1,                               H2,                      # A' — il s'eloigne
    "D6:1 F#6:1 A6:2",                "E6:1 B5:1 G#5:2",
    "A6:1 F#6:1 D6:2",                "B5:1 D6:1 F#6:2",
    "E6:1 A5:1 C#6:2",                "F#6:4",                 # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "C#4:4",                          "F#4:4",
    "E4:4",                           "B3:4",
    "A3:2 C#4:2",                     "F#4:2 D4:2",
    "C#4:2 E4:2",                     "G#3:2 B3:2",
    "C#4:2 A3:2",                     "D4:2 F#4:2",
    "A3:2 D4:2",                      "E4:2 C#4:2",
    "C#4:2 E4:2",                     "B3:2 G#3:2",
    "D4:2 A3:2",                      "F#4:2 D4:2",
    "F#4:2 A3:2",                     "D#4:2 F#4:2",
    "B3:2 E4:2",                      "C#4:2 G#3:2",
    "C#4:2 A3:2",                     "F#4:2 D4:2",
    "C#4:2 E4:2",                     "G#3:2 B3:2",
    "D4:2 F#4:2",                     "A3:2 D4:2",
    "B3:2 G#3:2",                     "A3:2 C#4:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

VOL = [midi("F#4"), midi("A4"), midi("C#5"), midi("A4")]       # deux ailes, un plane
CHUTE = [midi("C#5"), midi("A4"), midi("F#4"), midi("A4")]     # il plonge

REPONSE = {7:  "F#4:1 A4:.5 C#5:2 B4:.5",
           19: "D#4:1 F#4:.5 B4:2 A4:.5",
           27: "C#5:1 A4:1 F#4:2"}


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
    p = Piece("F#", "eolien", BPM, BAR, "Le Grand Nid")
    a, b = SILENCE
    i, j = PLONGEON

    # noire - croche - blanche - croche : le battement puis le vol plane
    aile = []
    for k in range(BARS):
        if k in REPONSE:
            aile += line(REPONSE[k], k * BAR)
        else:
            aile += ostinato(CHUTE if i <= k < j else VOL,
                             [1, .5, 2, .5], k * BAR, BAR)

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))
    p.add("aile", taire(aile, a, b))
    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # la basse ne marche pas : elle tient, puis se laisse tomber d'une quinte
    bas = (progression(CH[:8], 0, HALF, [(0, 2)], lo=47)
           + progression(CH[8:32], BAR * 4, HALF, [(0, 1.5), (-1, .5)], lo=47)
           + progression(CH[32:40], BAR * 16, HALF, [(0, 1), (-1, 1)], lo=47)
           + progression(CH[40:], BAR * 20, HALF, [(0, 1.5), (-1, .5)], lo=47))
    p.add("basse", taire(sec(bas, 0.30), a, b))

    # aucune caisse claire : une cymbale par entree, le charleston du vol plane
    p.add_drums([(0, "C", 7)], t0=BAR * 4)
    p.add_drums("O...", step=1.0, t0=BAR * 4, length=BAR * 12)
    p.add_drums([(0, "C", 7), (0, "K", 6), (BAR * 2, "K", 6)], t0=BAR * 16)
    p.add_drums("O.O.", step=1.0, t0=BAR * 16, length=BAR * 3 + 2.5)
    p.add_drums([(0, "C", 7), (0, "K", 6)], t0=BAR * 20)
    p.add_drums("O...", step=1.0, t0=BAR * 20, length=BAR * 8)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("aigle.mid"))
