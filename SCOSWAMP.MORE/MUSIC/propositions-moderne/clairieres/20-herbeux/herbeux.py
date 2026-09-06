#!/usr/bin/env python3
"""« Trois Chemins Herbeux » — clairiere 20. Re dorien, 150.

Variation dans la couleur `sud` : **bourdon de tonique immobile** sur le meme re
que `SOUTHSWAMP.MB`, mais en dorien — le si naturel a la place du si bemol. C'est
la seule difference de mode, et elle suffit : la page 047 dit « rien
d'interessant n'y apparait a premiere vue ; l'air est lourd et calme ». Une
clairiere ou il n'arrive rien doit sonner comme la zone, en plus clair et en
plus vide.

La forme n'est pas intro-A-B-A' mais **intro et trois phrases de six mesures**,
une par sentier, dans l'ordre du texte. La revision en fait trois **variations
d'un meme crochet**, et donne a chaque sentier sa propre basse et sa propre
batterie :

- le **sud** (mes. 5-10), « plus humide » : le crochet tel quel, la basse en
  blanches, une grosse caisse seule au premier temps. Cadence sur re mineur ;
- l'**est** (mes. 11-16), « une lueur d'horizon » : le crochet **transpose sur
  sol majeur** — le quatrieme degre majeur du dorien, le seul endroit clair de
  la piece — la basse en breve-longue, la batterie complete avec charleston et
  caisse claire. Cadence sur sol ;
- l'**ouest** (mes. 17-22), « etroit et borde d'arbres serres » : le crochet
  redit **tel quel**, la basse en quatre noires, le chemin se resserre. Cadence
  sur re mineur.

Ce que la revision ajoute encore :

- une **reponse** : mesures 10, 16 et 20, a chaque cadence, le chant tient sa
  ronde et l'arpege — la voix 3, a droite — repond le crochet une octave plus
  bas. Trois questions a gauche, trois reponses a droite : les trois sentiers se
  repondent, et aucun ne s'impose ;
- un **rythme harmonique** varie : neuf mesures changent d'accord au milieu, et
  la basse y marche en deux pas quelle que soit la phrase ;
- la **surprise** : mesure 18, un **si bemol majeur**. Le si **naturel** est
  precisement ce qui fait le dorien de cette piece et la difference d'avec la
  zone ; l'abaisser d'un demi-ton ferme le troisieme sentier d'un coup — « borde
  d'arbres serres ». La batterie s'y **tait** deux mesures durant ;
- une **cadence** franche a la fin : mesure 21, un **la majeur** avec son do
  diese, la seule sensible du morceau, qui ramene au re mineur ;
- un **arc de densite** qui suit les trois sentiers : rien, puis la caisse
  seule, puis la batterie complete, puis le silence, puis le plein ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le **la** du
  debut, la note meme par laquelle la piece recommence.

**La batterie** est une marche legere, presque un pas dans l'herbe : elle change
a chaque sentier et disparait au troisieme. Elle prend la voix 5 a droite ; il
ne reste que cinq parties de hauteur, et c'est la voix d'accords tenus qui a
cede la place — le bourdon de tonique est le procede de la zone.

22 mesures a 4/4, 35,2 s.

    python3 herbeux.py && python3 ../../../midi_to_mb.py herbeux.mid \\
        GRASSLAND.MB.BIN --bpm 150 --max 2304 --wav HERBEUX.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 22
LEN = BAR * BARS

# une entree par mesure ; « F|C » change d'accord au milieu de la mesure
CHORDS = (["Dm", "Dm", "C", "C"]
          + ["Dm", "F|C", "C|Am", "Am", "Dm|Am", "Dm"]
          + ["G", "C|G", "G|Am", "C|G", "Am|C", "G"]
          + ["Dm", "Bb", "Am|Dm", "Bb|C", "A", "Dm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "A4:4",                           "A4:2 D5:2",
    "C5:2 E5:2",                      "G4:2 A4:2",
    "D5:1 F5:1 A5:1.5 G5:.5",         "F5:2 E5:2",              # le sud : le crochet
    "E5:1 C5:1 A5:2",                 "C5:2 A4:2",
    "D5:1 A4:1 F5:2",                 "D5:4",                   # 10 : cadence + reponse
    "B4:1 D5:1 G5:1.5 A5:.5",         "C6:2 G5:2",              # l'est : le crochet sur sol
    "B5:1 G5:1 D6:2",                 "C6:1 A5:1 E5:2",
    "A5:1 C6:1 E6:2",                 "G5:4",                   # 16 : cadence + reponse
    "D5:1 F5:1 A5:1.5 G5:.5",         "F5:1 D5:1 Bb5:2",        # l'ouest : le crochet, 18 : le si bemol
    "A5:1 F5:1 D5:2",                 "D5:4",                   # 20 : la reponse
    "C#5:1 E5:1 A5:2",                "F5:1 E5:1 D5:1 A4:1",    # 21 : la cadence, 22 : le la de la boucle
]
assert len(MEL) == BARS

CTR = [
    "D4:2 F4:2",                      "A3:2 D4:2",
    "C4:2 E4:2",                      "G3:2 C4:2",
    "D4:2 A3:2",                      "F4:2 E4:2",
    "G3:2 A3:2",                      "E4:2 C4:2",
    "F4:2 E4:2",                      "D4:2 A3:2",
    "B3:2 D4:2",                      "E4:2 D4:2",
    "G3:2 A3:2",                      "C4:2 B3:2",
    "E4:2 G3:2",                      "D4:2 B3:2",
    "F4:2 A3:2",                      "Bb3:2 D4:2",
    "C4:2 D4:2",                      "F4:2 E4:2",
    "C#4:2 E4:2",                     "A3:2 D4:2",
]
assert len(CTR) == BARS

# la voix 3 repond a chaque cadence : le crochet, une octave plus bas
REPONSES = {
    9:  "D4:1 F4:1 A4:1.5 G4:.5",
    15: "B3:1 D4:1 G4:1.5 A4:.5",
    19: "D4:1 F4:1 Bb4:1.5 A4:.5",
}


def accompagnement():
    """L'arpege qui bondit a la quinte — sauf quand il repond au chant."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in REPONSES:
            out += line(REPONSES[i], t)
        elif i < 4:                    # l'intro : deux sons par demi-mesure
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 1.0, (0, 2), lo=54)
        else:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.5,
                            (0, 2, 1, 2), lo=54)
    return out


def basse():
    """Une basse par sentier : blanches au sud, breve-longue a l'est, quatre
    noires a l'ouest. Deux pas partout ou l'accord change au milieu."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        elif i < 10:
            out += progression([b], t, BAR, [(0, 2), (-1, 2)], lo=48)
        elif i < 16:
            out += progression([b], t, BAR, [(0, 2), (-1, 1), (0, 1)], lo=48)
        else:
            out += progression([b], t, BAR,
                               [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("D", "dorien", BPM, BAR, "Trois Chemins Herbeux")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("D2"), 0, LEN, retrig=BAR * 4))

    # un pas par sentier : la caisse seule au sud, tout a l'est, rien a l'ouest
    p.add_drums("K.......", t0=BAR * 4, length=BAR * 6)
    p.add_drums("K.H.S.H.", t0=BAR * 10, length=BAR * 6)
    # mesures 17-18 : rien. Les arbres se resserrent.
    p.add_drums([(3, "T"), (3.5, "T")], t0=BAR * 18)
    p.add_drums("K.HKS.H.", t0=BAR * 19, length=BAR * 3)
    p.add_drums([(0, "C", 7)], t0=BAR * 19)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("herbeux.mid"))
