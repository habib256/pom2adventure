#!/usr/bin/env python3
"""« Le Bal des Mares » — clairiere 30, les grenouilles. Sol eolien, 176.

Pages 053, 329, 230. « Le coassement de milliers de grenouilles vous accompagne.
Le sentier debouche sur une clairiere parsemee de mares. D'immenses champignons
se dressent au milieu ; un petit homme est assis sur l'un d'eux, petit et
corpulent, la bouche anormalement large, deux enormes grenouilles le gardent. »

C'est la seule clairiere comique des onze, et la seule ou le Marais fait du
bruit. Le procede de la zone `sud` est garde tel quel — la marche i-VI-III-VII
(Gm-Eb-Bb-F) posee sur un bourdon de sol qui ne bouge pas — et le caractere
aussi : la melodie **saute** l'octave en croches et retombe, la basse alterne
fondamentale et quinte grave. Le tempo passe de 166 a **176** : on danse.

Ce que la revision ajoute :

* **c'est la piece a batterie du lot** : le bal a enfin son tambourin. Charleston
  sur les croches, grosse caisse au premier temps, caisse claire au troisieme,
  charleston ouvert quand ca deborde. Elle est la du debut a la fin — c'est la
  seule des onze dont la batterie ne se retire jamais ;
* **le crochet** — le saut d'octave `sol · sol' | re · si bemol` — est enonce
  quatre fois (mesures 5, 9 renverse vers le bas, 21 a l'octave, et la cadence) ;
* **une vraie partie B** (mesures 13-20) : do mineur et fa, registre haut, et le
  chant qui ne redescend plus sous le do 6 ;
* **la reponse** : mesures 8, 12 et 16, le chant tient une ronde et l'arpege,
  a droite, lui repond par le meme saut d'octave — la grenouille d'en face ;
* **le rythme harmonique varie** : deux accords par mesure des la mesure 6, un
  seul tenu quatre mesures a l'intro ;
* **la surprise** : mesures 13 et 25, **sol majeur**. Le si becarre n'est pas
  dans le mode ; c'est la bouche anormalement large du petit homme, un sourire
  qui ne devrait pas etre la ;
* **l'arc** : intro sans batterie et arpege en noires ; A' avec le charleston
  ouvert sur chaque temps faible.

28 mesures a 4/4, 38,2 s. Forme intro(4) - A(8) - B(8) - A' a l'octave(8).

    python3 grenouilles.py && python3 ../../../midi_to_mb.py grenouilles.mid \\
        FROGS.MB.BIN --bpm 176 --max 2304 --wav GRENOUILLES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 176, 4, 28
LEN = BAR * BARS

GRILLE = [
    ("Gm",), ("Gm",), ("Bb",), ("Gm",),                          # intro
    ("Gm",), ("Eb", "F"), ("Cm", "Bb"), ("Gm",),                 # A
    ("Eb",), ("Bb", "F"), ("Cm", "Dm"), ("Gm",),
    ("G",), ("Cm",), ("Eb", "F"), ("Bb",),                       # B
    ("Cm", "Gm"), ("Eb", "Bb"), ("F", "Dm"), ("Gm",),
    ("Gm",), ("Eb", "F"), ("Cm", "Bb"), ("Gm",),                 # A'
    ("G",), ("Cm", "F"), ("Eb", "Dm"), ("Gm",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

HOOK = "G5:.5 G6:.5 D6:1 Bb5:2"         # le saut d'octave, puis la retombee
HOOKE = "Eb6:.5 Eb5:.5 G5:1 Bb5:2"      # le meme saut, a l'envers
HOOK8 = "G6:.5 G5:.5 D6:1 Bb5:2"

MEL = [
    "D5:4",                           "D5:2 G5:2",               # intro
    "Bb5:4",                          "G5:2 D5:2",
    HOOK,                             "Eb6:.5 Bb5:.5 Eb6:1 C6:2",  # A
    "C6:1 G5:1 Bb5:2",                "D6:4",
    HOOKE,                            "Bb5:.5 F6:.5 D6:1 Bb5:2",
    "C6:1 A5:1 D6:2",                 "G5:4",
    "B5:.5 G6:.5 D6:1 B5:2",          "C6:.5 G6:.5 Eb6:1 C6:2",  # B
    "Eb6:1 Bb5:1 F6:2",               "D6:4",
    "C6:.5 G6:.5 Eb6:1 C6:2",         "Eb6:.5 Bb5:.5 G6:1 Bb5:2",
    "F6:1 D6:1 A5:2",                 "G5:2 D6:2",
    HOOK8,                            "Eb6:.5 Bb5:.5 Eb6:1 C6:2",  # A'
    "C6:1 G6:1 Bb5:2",                "D6:1 G6:1 D6:2",
    "B5:.5 G6:.5 D6:1 B5:2",          "C6:.5 G6:.5 Eb6:1 F6:2",
    "Eb6:1 D6:1 A5:2",                "G6:2 G5:2",
]
assert len(MEL) == BARS

CTR = [
    "G3:4",                           "D4:4",                    # intro
    "Bb3:4",                          "G3:4",
    "D4:2 G3:2",                      "Bb3:2 C4:2",              # A
    "Eb4:2 D4:2",                     "Bb3:2 G3:2",
    "G3:2 Bb3:2",                     "D4:2 C4:2",
    "Eb4:2 F4:2",                     "D4:2 G3:2",
    "B3:2 D4:2",                      "Eb4:2 C4:2",              # B
    "G3:2 C4:2",                      "D4:2 F4:2",
    "Eb4:2 G3:2",                     "Bb3:2 D4:2",
    "C4:2 A3:2",                      "Bb3:2 D4:2",
    "D4:2 G3:2",                      "Bb3:2 C4:2",              # A'
    "Eb4:2 D4:2",                     "Bb3:2 G3:2",
    "B3:2 D4:2",                      "Eb4:2 C4:2",
    "G4:2 F4:2",                      "D4:2 G3:2",
]
assert len(CTR) == BARS

REPONSES = {                            # la grenouille d'en face
    7:  "D4:.5 D5:.5 Bb4:1 G4:2",
    11: "G4:.5 D5:.5 Bb4:1 G4:2",
    15: "D4:.5 D5:.5 F4:1 D4:2",
}


def arp(b0, b1, step, shape, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        out += arpeggio(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=45):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("G", "eolien", BPM, BAR, "Le Bal des Mares")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = arp(0, 4, 2.0, (0,))
    a += arp(4, 28, 0.5, (0, 2, 1, 2))
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    # la basse rebondit : fondamentale, saut a la quinte grave, retour
    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 20, [(0, 1), (-1, 0.5), (0, 0.5)])
    b += bas(20, 28, [(0, 1), (-1, 0.5), (2, 0.5)])
    p.add("basse", b)

    # le bourdon migre a gauche : la voix 5 est au tambourin
    p.add("bourdon", pedal(midi("G2"), 0, LEN))

    # Le bal. Le charleston est le coassement : il ne s'arrete jamais une fois
    # commence, et s'ouvre en A' quand la clairiere entiere danse.
    p.add_drums([(2, "H"), (3, "H"), (3.5, "H")], t0=BAR * 3)
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K.HHS.H.", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K.HOS.H.", t0=BAR * 20, length=BAR * 7)
    p.add_drums([(0, "K"), (2, "K"), (3, "S")], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("grenouilles.mid"))
