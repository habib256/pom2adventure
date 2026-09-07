#!/usr/bin/env python3
"""« La Licorne Blessee » — clairiere 23. Fa eolien, 142.

Variation dans la couleur `sud` : c'est la piece des douze qui reprend le plus
franchement le procede de la zone — la marche i-VI-III-VII (Fm-Db-Ab-Eb, celle
de `SOUTHSWAMP.MB` transposee) sur un **bourdon de tonique** qui ne bouge pas. Le
Marais est le meme ; l'animal, non.

Ce qui appartient a la clairiere, c'est la **noblesse** : la section A est en
blanches, sans une croche a la melodie, chose qu'aucune autre des douze ne fait
— l'animal blanc est couche au centre de la clairiere, page 320.

Ce que la revision ajoute :

- un **crochet** de deux mesures en blanches, la quinte montee puis la chute :
  fa - do | si bemol - la bemol. Il est enonce mesure 5, redit mesure 9, repris
  mesure 21 — et surtout **redresse** mesure 13, ou le meme dessin revient au
  **rythme pointe** : c'est le meme chant, debout. « Elle se releve cependant et
  baisse sa corne vers vous en lancant un grognement qui ressemble fort a un
  defi » ;
- une **reponse** : mesures 8, 11 et 16, le chant tient et l'arpege — la voix 3,
  a droite — repond le crochet une octave plus bas, en blanches en A et **pointe**
  en B, comme lui ;
- un **rythme harmonique** varie : onze mesures changent d'accord au milieu, et
  la marche i-VI-III-VII de la zone y garde sa carrure ;
- la **surprise** : mesure 19, un **fa majeur**. Toute la piece est en fa eolien ;
  le la naturel d'une seule mesure montre l'animal en entier, blanc, avant que la
  mesure 20 ne rabatte le mode en mineur. C'est le seul moment ou la Licorne
  n'est pas blessee ;
- une **cadence** : mesure 20, un **do majeur** avec son mi naturel — l'eolien
  n'en a pas, c'est bien pour cela qu'elle conclut. Elle revient mesure 23 ;
- un **arc de densite** qui monte puis redescend, ce qu'aucune autre des douze ne
  fait : la batterie ne joue qu'un tom toutes les deux mesures en A, charge au
  galop pendant tout le defi, puis se retire mesure par mesure jusqu'a un seul
  tom sur la derniere. La Licorne se recouche, ou s'en va (page 265) ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le do du
  debut.

**La batterie** est une charge, et seulement pendant le defi. Elle prend la voix
5 a droite ; il ne reste que cinq parties de hauteur, et c'est la voix d'accords
tenus qui a cede la place — le bourdon de tonique est le procede de la zone.

24 mesures a 4/4, 40,6 s. Forme intro(4) - A(8) l'animal couche - B(8) le defi -
A'(4).

    python3 licorne.py && python3 ../../../midi_to_mb.py licorne.mid \\
        UNICORN.MB.BIN --bpm 142 --max 2304 --wav LICORNE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 142, 4, 24
LEN = BAR * BARS

# une entree par mesure ; « Db|Ab » change d'accord au milieu de la mesure
CHORDS = (["Fm", "Fm", "Db", "Db"]
          + ["Fm", "Db|Ab", "Ab", "Eb|Bbm", "Fm", "Bbm|Cm", "Db|Eb", "Fm"]
          + ["Db", "Ab|Eb", "Bbm", "Db|Eb", "Cm|Fm", "Bbm|Db", "F", "C"]
          + ["Fm", "Db|Ab", "Eb|C", "Fm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "C5:4",                           "C5:2 F5:2",
    "Ab4:2 C5:2",                     "Db5:2 C5:2",
    "F5:2 C6:2",                      "Bb5:2 Ab5:2",            # le crochet, en blanches
    "C6:2 Eb6:2",                     "Bb5:4",                  # 8 : la reponse
    "F5:2 C6:2",                      "Db6:2 Bb5:2",            # le crochet, redit
    "Ab5:4",                          "C6:2 F5:2",              # 11 : la reponse
    "F5:1.5 Ab5:.5 C6:2",             "Bb5:1.5 G5:.5 Ab5:2",    # le crochet redresse : le defi
    "Db6:1.5 Bb5:.5 F5:2",            "C6:4",                   # 16 : la reponse, pointee
    "Eb6:1.5 C6:.5 G5:2",             "F6:1.5 Db6:.5 Bb5:2",
    "A5:1.5 C6:.5 F6:2",              "E5:1 G5:1 C6:2",         # 19 : le fa majeur, 20 : la cadence
    "F5:2 C6:2",                      "Bb5:2 Ab5:2",            # le crochet, une derniere fois
    "G5:2 E5:2",                      "F5:2 C5:2",              # 24 : le do de la boucle
]
assert len(MEL) == BARS

CTR = [
    "C4:2 Ab3:2",                     "F4:2 C4:2",
    "Db4:2 Ab3:2",                    "F4:2 Ab3:2",
    "C4:2 Ab3:2",                     "F4:2 Eb4:2",
    "Eb4:2 C4:2",                     "G3:2 Bb3:2",
    "Ab3:2 C4:2",                     "Db4:2 Eb4:2",
    "Ab3:2 G3:2",                     "C4:2 Ab3:2",
    "F4:2 Db4:2",                     "Eb4:2 Bb3:2",
    "Db4:2 F4:2",                     "Ab3:2 G3:2",
    "Eb4:2 C4:2",                     "Bb3:2 Ab3:2",
    "C4:2 A3:2",                      "E4:2 G3:2",
    "C4:2 Ab3:2",                     "F4:2 Eb4:2",
    "Bb3:2 G3:2",                     "Ab3:2 C4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le crochet une octave plus bas, pointe en B
REPONSES = {
    7:  "Eb4:1 G4:1 Bb4:2",
    10: "F4:1 Ab4:1 C5:2",
    15: "F4:1.5 Ab4:.5 C5:2",
}


def accompagnement():
    """L'arpege de la zone — sauf aux mesures ou il repond au chant."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in REPONSES:
            out += line(REPONSES[i], t)
        elif i < 4:                    # l'intro : deux sons par demi-mesure
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 1.0, (0, 2), lo=54)
        else:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.5,
                            (0, 1, 2, 1), lo=54)
    return out


def basse():
    """Breve-longue tant que l'accord tient la mesure, deux pas quand il change."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR, [(0, 2), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("F", "eolien", BPM, BAR, "La Licorne Blessee")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("F2"), 0, LEN, retrig=BAR * 4))

    # un sabot toutes les deux mesures, la charge pendant le defi, puis plus rien
    p.add_drums("T...............", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.HKS.H.", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K...S...", t0=BAR * 20, length=BAR * 2)
    p.add_drums([(0, "K")], t0=BAR * 22)
    p.add_drums([(0, "T")], t0=BAR * 23)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("licorne.mid"))
