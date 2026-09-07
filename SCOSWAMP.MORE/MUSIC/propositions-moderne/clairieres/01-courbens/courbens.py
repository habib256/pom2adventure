#!/usr/bin/env python3
"""« La Route des Trois Auberges » — clairiere 1, Route de Courbensaule.

Variation de la couleur `village` : mode majeur a septieme mineure, arpege de
croches en guise de tambourin, basse balancee. On n'est pas SUR la place du
village, on y ARRIVE — d'ou le re mixolydien, le tempo de 176 et la forme
batie sur une seule idee, la marche qui s'elargit.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `re fa# la re' do' / la sol fa#`, la montee
  d'arpege puis la retombee par degres. Il est enonce **quatre fois** (A deux
  fois, A' deux fois) et il ouvre la piece des la premiere mesure ;
- **une reponse** : aux mesures 8, 12, 20 et 28 le chant tient une ronde et
  c'est le tambourin — la voix 3, a droite — qui repond par une figure ecrite.
  La question est a gauche, la reponse est a droite, litteralement ;
- **le rythme harmonique varie** : la grille est ecrite a la demi-mesure. Les
  mesures d'exposition tiennent un accord, celles de marche en ont deux ;
- **la surprise** : la troisieme auberge, le Cheval Volant (mesures 17-18),
  est en **fa majeur** — le fa becarre n'appartient pas au mode. C'est la seule
  fois du morceau ou la route ment. Et juste avant la reprise, la mesure 20
  s'arrete net : **un demi-temps de silence general**, la batterie seule ;
- **la batterie** : un tambourin de marche. Rien dans l'intro, grosse caisse et
  caisse claire des le A, charleston ouvert dans le B, et la cellule complete
  au A'. Elle prend la voix 5 : le bourdon de re a donc cede la place, la
  grosse caisse en tient lieu.

28 mesures a 4/4, 38,2 s. Forme intro(4) - A(8) - B(8) - A'(8).

    python3 courbens.py && python3 ../../../midi_to_mb.py courbens.mid \\
        BENTBEAKS.MB.BIN --bpm 176 --max 2304 --wav COURBENS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 176, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0                           # la grille harmonique est au demi-temps
SILENCE = (BAR * 19 + 3.5, BAR * 20)       # le demi-temps ou tout se tait

# deux accords par mesure : quand ils sont egaux, l'accord tient la mesure
GRID = [
    ("D", "D"), ("D", "D"), ("G", "G"), ("C", "C"),            # intro — la route
    ("D", "D"), ("C", "G"), ("D", "D"), ("Am", "C"),           # A — le crochet
    ("D", "D"), ("C", "G"), ("Bm", "Em"), ("C", "D"),
    ("G", "G"), ("Em", "Em"), ("C", "C"), ("G", "D"),          # B — les auberges
    ("F", "F"), ("C", "C"), ("Am", "Am"), ("C", "C"),
    ("D", "D"), ("C", "G"), ("D", "D"), ("Bm", "Em"),          # A' — la boutique
    ("G", "G"), ("Am", "C"), ("C", "G"), ("D", "D"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "D5:.5 F#5:.5 A5:1 D6:1.5 C6:.5"      # le crochet, premiere mesure
H2 = "A5:2 G5:1 F#5:1"                     # le crochet, seconde mesure

MEL = [
    H1,                               H2,                      # l'intro dit deja tout
    "G5:1 B5:1 D6:2",                 "A5:1 B5:1 C6:2",
    H1,                               H2,
    "B5:1 D6:1 C6:1 A5:1",            "D6:4",                  # ← la reponse
    H1,                               H2,
    "G5:1 B5:1 D6:1.5 C6:.5",         "A5:4",                  # ← la reponse
    "B5:1 G5:1 D6:2",                 "E6:1 B5:1 G5:2",
    "C6:1 E6:1 G6:2",                 "D6:1.5 B5:.5 G5:2",
    "F6:1 A6:1 F6:1 C6:1",            "E6:1 C6:1 G5:2",        # ← fa becarre
    "A5:1 C6:1 E6:2",                 "D6:4",                  # ← la reponse
    H1,                               H2,
    H1,                               "F#6:1 D6:1 B5:2",
    "G6:1 D6:1 B5:2",                 "C6:1 E6:1 A5:2",
    "B5:1 A5:1 G5:1 F#5:1",           "D6:4",                  # ← la reponse
]
assert len(MEL) == BARS

# le contre-chant : deux blanches par mesure, detachees, jamais sur le temps 3
CTR = [
    "F#4:4",                          "A4:4",
    "G4:4",                           "E4:4",
    "F#4:2 A4:2",                     "E4:2 B3:2",
    "F#4:2 D4:2",                     "A4:2 F#4:2",
    "F#4:2 A4:2",                     "E4:2 G4:2",
    "D4:2 B3:2",                      "E4:2 F#4:2",
    "B3:2 D4:2",                      "G4:2 B3:2",
    "E4:2 G4:2",                      "D4:2 B3:2",
    "A4:2 C4:2",                      "G4:2 E4:2",
    "E4:2 A3:2",                      "G4:2 E4:2",
    "F#4:2 A4:2",                     "E4:2 B3:2",
    "F#4:2 A4:2",                     "D4:2 B3:2",
    "B3:2 D4:2",                      "C4:2 E4:2",
    "E4:2 B3:2",                      "F#4:2 A4:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

# les quatre reponses du tambourin, dans la bande juste sous le chant
REPONSE = {7:  "A4:1 D5:1 C5:1 A4:1",
           11: "G4:1 B4:1 D5:1.5 C5:.5",
           19: "G4:1 C5:1 E5:1 C5:1",
           27: "A4:1 F#4:1 D4:1 A4:1"}


def tenue(chords, per, lo, which=1, t0=0.0):
    """Le lit d'accords : une note tenue par accord, **fusionnee** quand la
    grille repete le meme accord. C'est ce qui rend le rythme harmonique
    variable gratuit : une mesure qui tient un accord coute une note, une
    mesure qui en a deux en coute deux."""
    out = []
    for i, c in enumerate(chords):
        n = pick(voicing(c, lo), which)
        if out and out[-1][0] == n:
            out[-1][2] += per
        else:
            out.append([n, t0 + i * per, per])
    return [tuple(e) for e in out]


def sec(part, coupe=0.30):
    """Detache : la note lache avant la suivante. Fait de la place a la
    batterie et allege le cote gauche, ou se trouvent trois voix sur cinq."""
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
    p = Piece("D", "mixolydien", BPM, BAR, "La Route des Trois Auberges")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # le tambourin du village : fondamentale - quinte - tierce - quinte, sauf
    # dans les quatre mesures de reponse, ou il chante a la place du chant
    tamb = []
    for i in range(BARS):
        if i in REPONSE:
            tamb += line(REPONSE[i], i * BAR)
        else:                       # l'intro tourne en noires, le reste en croches
            tamb += arpeggio(CH[2 * i:2 * i + 2], i * BAR, HALF,
                             1.0 if i < 4 else 0.5, (0, 2, 1, 2), lo=57)
    p.add("tambourin", taire(tamb, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # basse de danse, croche pointee - croche, detachee : elle laisse la place
    # a la grosse caisse au lieu de la doubler
    # la basse suit l'arc de densite : une appui par demi-mesure jusqu'au B,
    # le balancement croche pointee - croche ensuite
    bas = (progression(CH[:24], 0, HALF, [(0, 1.5), (None, .5)], lo=45)
           + progression(CH[24:], BAR * 12, HALF, [(0, 1.5), (0, .5)], lo=45))
    p.add("basse", taire(sec(bas, 0.35), a, b))

    # la batterie : rien sur la route, la marche des le A, la cellule pleine au A'
    p.add_drums([(0, "C", 7), (BAR * 3, "S"), (BAR * 3 + 3, "S")])
    p.add_drums("K.H. S.H.", t0=BAR * 4, length=BAR * 8)        # A
    p.add_drums("K.H. S..O", t0=BAR * 12, length=BAR * 8)       # B — le charleston ouvre
    p.add_drums([(a - BAR * 19, "T"), (a - BAR * 19 + .5, "T")], t0=BAR * 19)
    p.add_drums("K.H. S.H. K.H. S.S.", t0=BAR * 20, length=BAR * 8)   # A'
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("courbens.mid"))
