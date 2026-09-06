#!/usr/bin/env python3
"""« Le Sol qui Cede » — clairiere 12, les Sables Mouvants.

Variation de la couleur `danger` : demi-ton phrygien, bourdon immobile,
crescendo par la densite. Ce qui appartient a cette clairiere-la, c'est le
**sens** : tout descend. L'arpege parcourt l'accord a l'envers — quinte,
tierce, fondamentale, puis la quinte une octave plus bas — et recommence en
haut a chaque changement d'accord, si bien qu'on n'arrete pas de retomber sans
jamais arriver en bas.

Ce qui a change a la revision :

- **un crochet** de deux mesures qui ne fait que tomber : `fa' reb' do' lab /
  solb fa reb`. Quatre chutes puis une cinquieme, plus grave. Enonce trois
  fois ;
- **une reponse** : aux mesures 12, 20 et 26 le chant tient et la chute — voix
  3, a droite — repond a sa place, toujours vers le bas ;
- **la surprise** : mesure 18, l'arpege **remonte**. Une seule mesure, la seule
  du morceau : fondamentale, tierce, quinte, octave, et l'on croit s'en sortir.
  La mesure suivante, mesure 19, retombe deux fois plus vite. Puis mesure 20 :
  **un temps et demi de silence general** — le sol cede pour de bon — un tom
  qui tombe seul, et tout repart ensemble une mesure plus bas ;
- **le sol cede a la mesure 9** : l'arpege passe de la noire a la croche et la
  basse double, exactement comme le `danger` de la zone se resserre a sa
  neuvieme mesure ;
- **la voix des accords a cede la place, pas le bourdon** : c'est la regle du
  `danger`. Le bourdon de **do**, la quinte a vide de fa, est la seule chose
  qui ne bouge pas du morceau — on s'enfonce, mais le Marais, lui, ne
  s'enfonce pas. Cinq parties de hauteur : chant, chute, contre-chant, basse,
  bourdon ;
- **la batterie** : un tom lent qui accelere avec le terrain. Deux frappes par
  mesure tant que le sol tient, quatre des qu'il cede, une grosse caisse en
  dessous, et le tom seul dans le silence. Pas un charleston : rien ne claque
  dans du sable.

Fa mineur phrygien, 144 a la noire, 26 mesures a 4/4, 43,3 s.
Forme intro(4) - A(8) - B(8) - A'(6).

    python3 sables.py && python3 ../../../midi_to_mb.py sables.mid \\
        QUICKSAND.MB.BIN --bpm 144 --max 2304 --wav SABLES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 144, 4, 26
LEN = BAR * BARS
HALF = BAR / 2.0
CEDE = 8                                   # la mesure ou le terrain cede
REMONTE = 17                               # la seule mesure qui monte
SILENCE = (BAR * 19 + 2.5, BAR * 20)       # le sol cede pour de bon

GRID = [
    ("Fm", "Fm"), ("Gb", "Gb"), ("Fm", "Fm"), ("Fm", "Fm"),    # intro — le lierre
    ("Fm", "Fm"), ("Gb", "Fm"), ("Fm", "Ebm"), ("Db", "Gb"),   # A — on s'enfonce
    ("Fm", "Fm"), ("Gb", "Fm"), ("Ebm", "Db"), ("Fm", "Fm"),
    ("Bbm", "Bbm"), ("Db", "Ab"), ("Ebm", "Bbm"), ("Gb", "Db"),  # B — la Chance
    ("Bbm", "Bbm"), ("Ab", "Ab"), ("Gb", "Db"), ("Fm", "Fm"),
    ("Fm", "Fm"), ("Gb", "Fm"), ("Ebm", "Db"), ("Gb", "Gb"),   # A' — on sombre
    ("Fm", "Fm"), ("Fm", "Fm"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "F6:1 Db6:1 C6:1 Ab5:1"               # le crochet : quatre chutes
H2 = "Gb5:1.5 F5:.5 Db5:2"

MEL = [
    "C6:2 Ab5:2",                     "Db6:1 C6:1 Ab5:2",      # intro
    "C6:2 F5:2",                      "Ab5:2 F5:2",
    H1,                               H2,                      # A
    "Ab5:1 F5:1 Db5:2",               "Db6:1 Bb5:1 Gb5:2",
    H1,                               H2,
    "C6:1 Ab5:1 F5:2",                "F5:4",                  # ← la reponse
    "Bb5:1 Db6:1 F6:2",               "Ab6:1 F6:1 Db6:2",      # B — la Chance
    "Eb6:1 C6:1 Ab5:2",               "Bb5:1 Gb5:1 Eb5:2",
    "Db6:1 Bb5:1 F5:2",               "Gb6:1 Db6:1 Bb5:2",     # ← l'arpege remonte
    "F6:1 Db6:1 Ab5:2",               "C6:4",                  # ← la reponse
    H1,                               H2,                      # A' — on sombre
    "Db6:.5 C6:.5 Ab5:1 Gb5:2",       "Bb5:1 Gb5:1 Eb5:2",
    "Db6:.5 C6:.5 Bb5:1 Gb5:2",       "Db6:1 C6:3",            # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "Ab3:4",                          "Bb3:4",
    "C4:4",                           "Ab3:4",
    "Ab3:2 F3:2",                     "Db4:2 Bb3:2",
    "C4:2 Ab3:2",                     "Gb3:2 Eb4:2",
    "F3:2 Db4:2",                     "Bb3:2 Gb3:2",
    "Ab3:2 C4:2",                     "C4:2 F3:2",
    "Db4:2 Bb3:2",                    "F3:2 Ab3:2",
    "C4:2 Eb4:2",                     "Gb3:2 Bb3:2",
    "Db4:2 F3:2",                     "Bb3:2 Db4:2",
    "Ab3:2 F3:2",                     "C4:2 Ab3:2",
    "F3:2 C4:2",                      "Db4:2 Bb3:2",
    "Gb3:2 Eb4:2",                    "F3:2 Db4:2",
    "Bb3:2 Db4:2",                    "C4:2 Ab3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

BAS = (2, 1, 0, -1)                        # quinte, tierce, fondamentale, quinte grave
HAUT = (0, 1, 2, 3)                        # la seule mesure qui remonte

REPONSE = {11: "C5:1 Ab4:1 F4:1 C4:1",
           19: "F4:1 Db4:1 C4:1.5 Ab3:.5",
           25: "Db4:1 C4:1 Ab3:2"}


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
    p = Piece("F", "phrygien", BPM, BAR, "Le Sol qui Cede")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # la chute : en noires tant que le sol tient, en croches ensuite ; une seule
    # mesure remonte, et la suivante retombe deux fois plus vite
    chute = []
    for i in range(BARS):
        if i in REPONSE:
            chute += line(REPONSE[i], i * BAR)
            continue
        forme = HAUT if i == REMONTE else BAS
        pas = 1.0 if i < CEDE else (0.25 if i == REMONTE + 1 else 0.5)
        chute += arpeggio(CH[2 * i:2 * i + 2], i * BAR, HALF, pas, forme, lo=57)
    p.add("chute", taire(chute, a, b))

    p.add("contre-chant", taire(lines(CTR, 0, bar=BAR), a, b))

    # la basse double quand le terrain cede
    bas = (progression(CH[:2 * CEDE], 0, HALF, [(0, 2)], lo=45)
           + progression(CH[2 * CEDE:], BAR * CEDE, HALF, [(0, 1), (-1, 1)], lo=45))
    p.add("basse", taire(bas, a, b))

    # le bourdon de do ne bouge pas : le Marais, lui, ne s'enfonce pas
    p.add("bourdon", pedal(midi("C2"), 0, LEN, retrig=BAR * 4))

    # le tom accelere avec le terrain ; rien qui claque dans du sable
    p.add_drums("T...T...", t0=0, length=BAR * 8)
    p.add_drums("K.T.K.T.", t0=BAR * 8, length=BAR * 11 + 2.5)
    p.add_drums([(0, "T"), (.7, "T"), (1.4, "T", 6)], t0=BAR * 19 + 2.5)
    p.add_drums("K.T.K.TT", t0=BAR * 20, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("sables.mid"))
