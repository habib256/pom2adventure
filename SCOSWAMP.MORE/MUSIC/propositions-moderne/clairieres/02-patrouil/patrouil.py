#!/usr/bin/env python3
"""« La Question du Patrouilleur » — clairiere 2, pages 170, 363, 234.

Variation de la couleur `nord` : l'ostinato fixe qui ne change jamais pendant
que les accords bougent dessous. Ici il change de **metrique** au lieu de
changer de notes — la cellule `la - mi - do` fait trois pas dans une mesure qui
en compte quatre, donc elle retombe chaque fois ailleurs. L'homme en vert fait
sa ronde et vous le retrouvez toujours a un autre endroit du chemin.

Ce qui a change a la revision :

- **un crochet** de deux mesures qui cite la ronde elle-meme : `la mi do' /
  si la mi`. Enonce quatre fois, deux au A, deux au A' ;
- **une reponse** : aux mesures 8, 12, 20 et 28 le chant tient et la ronde —
  voix 3, a droite — repond a sa place par une figure ecrite. C'est la question
  du patrouilleur et la reponse qu'on lui donne ;
- **la ronde change de vitesse** : elle tourne en **noires** dans l'intro et
  dans tout le B (trois noires contre quatre temps, la hemiole s'entend), en
  **croches** dans le A et le A'. C'est l'arc de densite du morceau, et la
  raison pour laquelle le B respire ;
- **la surprise** : mesure 19, l'accord de **mi majeur** — un sol diese qui
  n'existe pas dans le mode. La pique se leve. Puis mesure 20, tout s'arrete :
  **un temps de silence general**, la caisse claire seule, et l'on repart
  ensemble sur le A' ;
- **la batterie** : une marche de patrouille. Grosse caisse et caisse claire
  d'aplomb sur les temps, mais le charleston bat toutes les **trois** croches,
  comme la ronde : les deux decalages ne retombent ensemble qu'une mesure sur
  trois. Elle prend la voix 5, le bourdon de mi a cede la place.

La mineur eolien, 162 a la noire, 28 mesures a 4/4, 41,5 s.
Forme intro(4) - A(8) - B(8) - A'(8).

    python3 patrouil.py && python3 ../../../midi_to_mb.py patrouil.mid \\
        PATROLLER.MB.BIN --bpm 162 --max 2304 --wav PATROUIL.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 162, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0
SILENCE = (BAR * 19 + 3.0, BAR * 20)       # le temps ou la ronde s'arrete

GRID = [
    ("Am", "Am"), ("Am", "Am"), ("F", "F"), ("G", "G"),        # intro — la brume
    ("Am", "Am"), ("F", "C"), ("Am", "Am"), ("Dm", "G"),       # A — l'appel
    ("Am", "Am"), ("F", "C"), ("Dm", "Em"), ("Am", "Am"),
    ("C", "C"), ("G", "G"), ("F", "F"), ("C", "G"),            # B — la question
    ("Dm", "Dm"), ("Am", "Am"), ("E", "E"), ("Em", "Em"),
    ("Am", "Am"), ("F", "C"), ("Am", "Am"), ("Dm", "G"),       # A' — la reponse
    ("F", "F"), ("Em", "Em"), ("G", "G"), ("Am", "Am"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "A5:1 E5:1 C6:1.5 B5:.5"              # le crochet cite la ronde
H2 = "A5:2 E5:1 G5:1"

MEL = [
    "A5:2 E5:2",                      "C6:2 B5:2",             # intro — deux notes
    "A5:2 F5:2",                      "G5:1 A5:1 B5:2",
    H1,                               H2,                      # A
    "F5:1 A5:1 C6:1 E6:1",            "D6:4",                  # ← la reponse
    H1,                               H2,
    "D6:1 F6:1 A5:1 C6:1",            "E5:4",                  # ← la reponse
    "C6:1 E6:1 G6:2",                 "B5:1 D6:1 G5:2",        # B — plus haut
    "A5:1 C6:1 F6:2",                 "E6:1 G6:1 C6:2",
    "D6:1 A5:1 F6:2",                 "E6:1 C6:1 A5:2",
    "G#5:1 B5:1 E6:2",                "B5:4",                  # ← sol diese, la pique
    H1,                               H2,                      # A'
    "F5:1 A5:1 C6:1 E6:1",            "D6:1 F6:1 A6:2",
    "F6:1 C6:1 A5:2",                 "B5:1 G5:1 E5:2",
    "G5:1 B5:1 D6:1 B5:1",            "A5:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "C4:4",                           "A3:4",
    "F4:4",                           "B3:4",
    "C4:2 E4:2",                      "A3:2 C4:2",
    "A3:2 F4:2",                      "F4:2 B3:2",
    "C4:2 E4:2",                      "A3:2 G4:2",
    "F4:2 D4:2",                      "E4:2 C4:2",
    "E4:2 G4:2",                      "D4:2 B3:2",
    "C4:2 A3:2",                      "E4:2 G4:2",
    "F4:2 A3:2",                      "C4:2 E4:2",
    "B3:2 G#3:2",                     "B3:2 E4:2",
    "C4:2 E4:2",                      "A3:2 C4:2",
    "A3:2 F4:2",                      "F4:2 B3:2",
    "C4:2 A3:2",                      "B3:2 G4:2",
    "D4:2 B3:2",                      "E4:2 A3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

RONDE = [midi("A4"), midi("E4"), midi("C5")]        # l'appel, trois pas

REPONSE = {7:  "A4:1 E4:1 C5:1.5 B4:.5",
           11: "G4:1 C5:1 E5:1 C5:1",
           19: "E4:1 G#4:1 B4:1.5 A4:.5",
           27: "C5:1 B4:1 A4:1 E4:1"}

CROCHES = (BAR * 4, BAR * 12)              # le A et le A' : la ronde court
CROCHES2 = (BAR * 20, LEN)


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
    """Detache : la note lache avant la suivante, la batterie occupe le trou."""
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
    p = Piece("A", "eolien", BPM, BAR, "La Question du Patrouilleur")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # la ronde : trois pas contre quatre temps, en noires puis en croches
    ronde = []
    for i in range(BARS):
        if i in REPONSE:
            ronde += line(REPONSE[i], i * BAR)
        else:
            vite = (CROCHES[0] <= i * BAR < CROCHES[1]
                    or CROCHES2[0] <= i * BAR < CROCHES2[1])
            ronde += ostinato(RONDE, 0.5 if vite else 1.0, i * BAR, BAR, gap=0.08)
    p.add("ronde", taire(ronde, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # la basse marche, mais elle ne pese pas : elle lache avant chaque temps
    bas = (progression(CH[:8], 0, HALF, [(0, 1.5), (None, .5)], lo=46)
           + progression(CH[8:24], BAR * 4, HALF, [(0, 1), (-1, 1)], lo=46)
           + progression(CH[24:40], BAR * 12, HALF, [(0, 1.5), (None, .5)], lo=46)
           + progression(CH[40:], BAR * 20, HALF, [(0, 1), (-1, 1)], lo=46))
    p.add("basse", taire(sec(bas, 0.35), a, b))

    # la marche : caisse d'aplomb, charleston toutes les trois croches
    p.add_drums("K.S.", step=1.0, t0=BAR * 4, length=BAR * 8)
    p.add_drums("H..", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K..S", step=1.0, t0=BAR * 12, length=BAR * 7)
    p.add_drums([(0, "S"), (1, "S"), (2, "S", 4)], t0=BAR * 19 + 1)
    p.add_drums("K.S.", step=1.0, t0=BAR * 20, length=BAR * 8)
    p.add_drums("H..", t0=BAR * 20, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("patrouil.mid"))
