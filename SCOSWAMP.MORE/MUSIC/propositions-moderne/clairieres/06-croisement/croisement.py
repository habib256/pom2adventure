#!/usr/bin/env python3
"""« Quatre Chemins » — clairiere 6, le croisement (page 121, une seule page).

Variation de la couleur `nord`, et la plus litterale : meme mode que la zone —
**mi eolien** — parce que le croisement est le centre du Marais nord et n'avait
aucune raison de changer de couleur. Il avait une raison de changer de forme.

Le procede de la zone est l'ostinato fixe. Ici il est fixe **a l'interieur d'un
panneau** et il change a chaque panneau : quatre cellules de quatre croches,
une par direction, toutes batties sur d'autres degres du meme mode.

Ce qui a change a la revision :

- **le crochet est la tete de panneau** : deux mesures, `mi si re' / si la sol`,
  qui reviennent au debut de **chacune des quatre routes**. C'est la meme
  question posee quatre fois — « laquelle allez-vous choisir ? » — et elle est
  donc enoncee quatre fois, la derniere une octave plus haut ;
- **une reponse par panneau** : a la sixieme mesure de chaque route le chant
  tient une ronde et la cellule — voix 3, a droite — repond a sa place. Quatre
  questions a gauche, quatre reponses a droite ;
- **la surprise** : le quatrieme panneau, l'ouest, passe en **si majeur**. Le
  re diese n'appartient pas au mode : c'est la seule route qui ment, et
  l'ostinato ment avec elle. Juste avant, la fin du panneau est passe :
  **un temps et demi de silence general**, un roulement de tom, et l'ouest
  part sur un tutti ;
- **le rythme harmonique varie** : grille a la demi-mesure. L'arret du
  carrefour tient un accord par mesure ; des qu'une route s'engage, les accords
  vont a la demi-mesure ;
- **la batterie** : une par direction. Marche au nord, contretemps au sud,
  charleston seul a l'est, pression a l'ouest. Rien au carrefour : on est
  arrete. La voix 5 lui revient, le bourdon de mi a cede la place.

28 mesures a 4/4, 44,8 s. Forme intro(4) - nord(6) - sud(6) - est(6) - ouest(6).

    python3 croisement.py && python3 ../../../midi_to_mb.py croisement.mid \\
        CROSSROADS.MB.BIN --bpm 150 --max 2304 --wav CROISEMENT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0
SILENCE = (BAR * 21 + 2.5, BAR * 22)       # le passage manque avant l'ouest

GRID = [
    ("Em", "Em"), ("Em", "Em"), ("C", "C"), ("D", "D"),        # intro — l'arret
    ("Em", "Em"), ("G", "D"), ("Em", "Em"), ("C", "C"),        # nord
    ("Am", "Bm"), ("Em", "Em"),
    ("Am", "Am"), ("Em", "Em"), ("C", "G"), ("Am", "Am"),      # sud
    ("D", "Bm"), ("Em", "Em"),
    ("G", "G"), ("D", "D"), ("Em", "C"), ("G", "G"),           # est
    ("Am", "D"), ("G", "G"),
    ("C", "C"), ("Am", "Am"), ("B", "B"), ("Em", "Em"),        # ouest — si majeur
    ("C", "B"), ("Em", "Em"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

T1 = "E5:1 B5:1 D6:2"                      # la tete de panneau, la question
T2 = "B5:1.5 A5:.5 G5:2"

MEL = [
    "E5:2 B5:2",                      "G5:1 B5:1 E6:2",        # intro — l'arret
    "D6:1 B5:1 G5:2",                 "A5:1 F#5:1 D5:2",
    T1,                               T2,                      # nord
    "D6:1 F#6:1 A6:2",                "G6:1 E6:1 B5:2",
    "C6:1 E6:1 G6:2",                 "B5:4",                  # ← la reponse
    "A5:1 E6:1 G6:2",                 "E6:1.5 D6:.5 C6:2",     # sud — la tete montee
    "A5:1 C6:1 E6:2",                 "D6:1 B5:1 G5:2",
    "F#5:1 A5:1 D6:2",                "E6:4",                  # ← la reponse
    "G5:1 D6:1 B5:2",                 "D6:1.5 C6:.5 B5:2",     # est — la tete au grave
    "E6:1 G6:1 B6:2",                 "A6:1 F#6:1 D6:2",
    "C6:1 E6:1 G6:2",                 "D6:4",                  # ← la reponse
    "E6:1 B5:1 D6:2",                 "B5:1.5 A5:.5 G5:2",     # ouest — la tete
    "D#6:1 F#6:1 B5:2",               "E6:1 B5:1 G5:2",        # ← re diese
    "C6:1 E6:1 D#6:2",                "E6:4",                  # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "G4:4",                           "E4:4",
    "C4:4",                           "F#4:4",
    "B3:2 E4:2",                      "D4:2 B3:2",
    "A3:2 F#4:2",                     "G4:2 E4:2",
    "E4:2 C4:2",                      "D4:2 F#4:2",
    "C4:2 A3:2",                      "E4:2 B3:2",
    "G4:2 E4:2",                      "B3:2 D4:2",
    "A3:2 C4:2",                      "F#4:2 D4:2",
    "B3:2 G4:2",                      "A3:2 D4:2",
    "E4:2 G4:2",                      "C4:2 E4:2",
    "D4:2 B3:2",                      "F#4:2 A3:2",
    "E4:2 G4:2",                      "C4:2 A3:2",
    "D#4:2 F#4:2",                    "B3:2 E4:2",
    "A3:2 D#4:2",                     "E4:2 B3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

# une cellule par direction, toutes dans le meme mode et la meme bande
NORD = [midi("B4"), midi("G4"), midi("A4"), midi("E4")]
SUD = [midi("A4"), midi("E4"), midi("F#4"), midi("D4")]
EST = [midi("D4"), midi("G4"), midi("B4"), midi("G4")]
OUEST = [midi("E4"), midi("A4"), midi("C5"), midi("A4")]
MENSONGE = [midi("D#4"), midi("A4"), midi("B4"), midi("F#4")]  # l'ouest ment

REPONSE = {9:  "B4:1 G4:1 A4:1.5 E4:.5",
           15: "E4:1 A4:1 C5:1 A4:1",
           21: "D4:1 G4:1 B4:1.5 A4:.5",
           27: "E4:1 D#4:1 B4:1 E4:1"}

PANNEAU = [(4, NORD), (10, SUD), (16, EST), (22, OUEST)]


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


def cellule(i):
    """La cellule de la mesure `i` : celle de sa route, et le mensonge a l'ouest."""
    if i < 4:
        return NORD
    if i in (24, 26):
        return MENSONGE
    for start, cell in reversed(PANNEAU):
        if i >= start:
            return cell
    return NORD


def build():
    p = Piece("E", "eolien", BPM, BAR, "Quatre Chemins")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # au carrefour la cellule est en noires : on est arrete. Elle passe en
    # croches des qu'une route s'engage, et ne s'arrete plus.
    aig = []
    for i in range(BARS):
        if i in REPONSE:
            aig += line(REPONSE[i], i * BAR)
        else:
            aig += ostinato(cellule(i), 1.0 if i < 4 else 0.5, i * BAR, BAR)
    p.add("ostinato", taire(aig, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # chaque route a sa basse : elle marche au nord et a l'ouest, elle pose
    # et lache au sud et a l'est
    marche, pose = [(0, 1), (-1, 1)], [(0, 1.5), (None, .5)]
    bas = (progression(CH[:8], 0, HALF, pose, lo=45)
           + progression(CH[8:20], BAR * 4, HALF, marche, lo=45)
           + progression(CH[20:44], BAR * 10, HALF, pose, lo=45)
           + progression(CH[44:], BAR * 22, HALF, marche, lo=45))
    p.add("basse", taire(sec(bas, 0.40), a, b))

    # une batterie par direction ; rien au carrefour
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 6)         # nord — la marche
    p.add_drums("K..H..S.", t0=BAR * 10, length=BAR * 6)        # sud — le contretemps
    p.add_drums("..H...H.", t0=BAR * 16, length=BAR * 6)        # est — presque rien
    p.add_drums([(0, "T"), (.5, "T"), (1, "T", 5)], t0=BAR * 21 + 1)
    p.add_drums("K.S.KKS.", t0=BAR * 22, length=BAR * 6)        # ouest — la pression
    p.add_drums([(0, "C", 7)], t0=BAR * 22)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("croisement.mid"))
