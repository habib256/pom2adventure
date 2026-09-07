#!/usr/bin/env python3
"""« Le Cor du Maitre » — clairiere 32, le Maitre des Loups. Mi eolien, 150.

Pages 398, 239, 314. « Une petite maison en rondins. Un grognement qui ressemble
a celui d'un chien : ce n'est pas un chien, cependant, mais un Loup. Un homme
robuste, vetu comme un Garde Forestier, l'Amulette d'Argent en forme de loup sur
la poitrine. Il vous repond avec mauvaise humeur en vous ordonnant de passer
votre chemin. »

Le procede de la zone `sud` est garde : marche i-VI-III-VII (Em-C-G-D) sur un
bourdon de mi immobile. Le caractere aussi : **le cor**. La melodie est faite de
quintes et de quartes a vide, l'arpege sonne fondamentale-quinte et n'a pas une
seule tierce — un pavillon de cuivre n'en donne pas. Le tempo passe de 143 a
**150** : la meute part.

Ce que la revision ajoute :

* **le galop** a la batterie : trois coups groupes, `ta-ta-TAM`, ecrits au quart
  de temps. Il entre a la mesure 5 au trot, passe au galop plein en B, et c'est
  lui — pas le volume — qui fait monter la chasse ;
* **le crochet** — l'appel `mi · si · mi'`, quinte puis quarte, tout ouvert — est
  enonce quatre fois : mesures 5, 9 (sur la), 21 (a l'octave) et 24 ;
* **une vraie partie B** (mesures 13-19) : le chant monte au sol 6 et l'harmonie
  passe par si mineur et re, les deux degres que A n'a jamais ;
* **la reponse** : mesures 8, 12 et 16, le chant tient une ronde et l'arpege lui
  renvoie l'appel — c'est le second cor, de l'autre cote du bois, a droite ;
* **le rythme harmonique varie** : deux accords par mesure des la mesure 6, un
  seul tenu quatre mesures a l'intro ;
* **la surprise** : la **mesure 20 a six temps**. Le Maitre leve la main, le cor
  tient, la batterie s'arrete net et la meute attend deux temps de trop avant que
  la reprise ne parte ;
* **l'arc** : intro sans batterie, A au trot, B au galop, A' au galop double, et
  une derniere mesure ou il ne reste qu'un coup.

28 mesures a 4/4 plus deux temps, 45,6 s. Forme intro(4) - A(8) - B(7) -
mesure longue(1) - A'(8).

    python3 maitreloups.py && python3 ../../../midi_to_mb.py maitreloups.mid \\
        WOLFMASTER.MB.BIN --bpm 150 --max 2304 --wav MAITRELOUPS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LONGUE = 19                             # la mesure ou le cor tient : six temps
BEATS = [6 if i == LONGUE else 4 for i in range(BARS)]
T = [sum(BEATS[:i]) for i in range(BARS + 1)]
LEN = T[-1]

GRILLE = [
    ("Em",), ("Em",), ("C",), ("D",),                            # intro
    ("Em",), ("C", "G"), ("Am", "D"), ("Em",),                   # A
    ("Am",), ("C", "G"), ("Bm", "D"), ("Em",),
    ("C", "G"), ("D",), ("Am", "Em"), ("C",),                    # B
    ("G", "D"), ("Am", "Bm"), ("C", "D"), ("Em",),
    ("Em",), ("C", "G"), ("Am", "D"), ("Bm",),                   # A'
    ("C", "G"), ("Am", "D"), ("C", "Bm"), ("Em",),
]
assert len(GRILLE) == BARS

HOOK = "E5:1 B5:1 E6:2"                 # l'appel : quinte, puis quarte
HOOKA = "A5:1 E6:1 A6:2"
HOOK8 = "B5:1 E6:1 B6:2"

MEL = [
    "B5:4",                           "B5:2 E6:2",               # intro
    "G5:2 E5:2",                      "A5:2 B5:2",
    HOOK,                             "G5:1 C6:1 G5:2",          # A
    "A5:1 E6:1 A5:2",                 "B5:4",
    HOOKA,                            "E6:1 C6:1 G5:2",
    "D6:1 A5:1 F#6:2",                "E6:4",
    "G5:1 C6:1 E6:2",                 "F#6:1 D6:1 A5:2",         # B
    "E6:1 A5:1 C6:2",                 "G6:4",
    "D6:1 G6:1 B5:2",                 "C6:1 A5:1 F#6:2",
    "E6:1 C6:1 D6:2",                 "B5:6",                    # mesure longue
    HOOK8,                            "G6:1 C6:1 G6:2",          # A'
    "A5:1 E6:1 A6:2",                 HOOK,
    "E6:1 G6:1 C6:2",                 "A5:1 D6:1 F#6:2",
    "G6:1 E6:1 B5:2",                 "E6:2 B5:2",
]
assert len(MEL) == BARS

CTR = [
    "E4:4",                           "B3:4",                    # intro
    "G3:4",                           "A3:4",
    "B3:2 E4:2",                      "G3:2 C4:2",               # A
    "A3:2 F#4:2",                     "E4:2 B3:2",
    "A3:2 C4:2",                      "E4:2 G3:2",
    "B3:2 D4:2",                      "G3:2 E4:2",
    "C4:2 G3:2",                      "A3:2 F#4:2",              # B
    "E4:2 A3:2",                      "G3:2 C4:2",
    "B3:2 D4:2",                      "C4:2 F#4:2",
    "G3:2 A3:2",                      "B3:6",                    # mesure longue
    "B3:2 E4:2",                      "G3:2 C4:2",               # A'
    "A3:2 F#4:2",                     "D4:2 B3:2",
    "E4:2 G3:2",                      "A3:2 D4:2",
    "C4:2 B3:2",                      "E4:2 B3:2",
]
assert len(CTR) == BARS

REPONSES = {                            # le second cor, de l'autre cote du bois
    7:  "E4:1 B4:1 E5:2",
    11: "A4:1 E5:1 A4:2",
    15: "G4:1 C5:1 G4:2",
}


def arp(b0, b1, step, shape, lo=57):
    """L'arpege du cor : fondamentale-quinte, jamais de tierce."""
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        ch = (GRILLE[b] * 2)[:2]
        out += arpeggio(list(ch), T[b], BEATS[b] / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=45):
    out = []
    for b in range(b0, b1):
        ch = (GRILLE[b] * 2)[:2]
        out += progression(list(ch), T[b], BEATS[b] / 2, pattern, lo)
    return out


def build():
    p = Piece("E", "eolien", BPM, BAR, "Le Cor du Maitre")

    mel = []
    for i, s in enumerate(MEL):
        mel += line(s, T[i])
    p.add("melodie", mel)

    a = arp(0, 4, 2.0, (0,))
    a += arp(4, 12, 1.0, (0, 2))
    a += arp(12, 19, 0.5, (0, 2, 0, 2))
    a += arpeggio(["Em"], T[LONGUE], BEATS[LONGUE], 3.0, (0, 2), lo=57)
    a += arp(20, 28, 0.5, (0, 2, 0, 2))
    for b, spec in REPONSES.items():
        a += line(spec, T[b])
    p.add("arpege", a)

    ctr = []
    for i, s in enumerate(CTR):
        ctr += line(s, T[i])
    p.add("contre-chant", ctr)

    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 19, [(0, 0.75), (0, 0.25), (-1, 1)])
    b += bas(LONGUE, LONGUE + 1, [(0, 2), (-1, 1)])
    b += bas(20, 28, [(0, 0.75), (0, 0.25), (-1, 0.5), (0, 0.5)])
    p.add("basse", b)

    # le bourdon migre a gauche : la voix 5 est au galop
    p.add("bourdon", pedal(midi("E2"), 0, LEN))

    # Le galop, ecrit au quart de temps : ta-ta-TAM, trois coups groupes.
    # Rien a l'intro, le trot en A, le galop en B, rien du tout mesure 20.
    p.add_drums("K..K.......S....", step=0.25, t0=T[4], length=T[12] - T[4])
    p.add_drums([(0, "C", 7)], t0=T[12])
    p.add_drums("K..KK...S..KK...", step=0.25, t0=T[12], length=T[19] - T[12])
    p.add_drums([(0, "C", 7)], t0=T[20])
    p.add_drums("K..KK...S..KK..S", step=0.25, t0=T[20], length=T[27] - T[20])
    p.add_drums([(0, "K"), (2, "S")], t0=T[27])
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("maitreloups.mid"))
