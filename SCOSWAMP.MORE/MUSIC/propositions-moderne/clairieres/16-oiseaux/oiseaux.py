#!/usr/bin/env python3
"""« La Maitresse des Oiseaux » — clairiere 16. Mi dorien, 168.

Variation dans la couleur `sud` : le **bourdon de tonique qui ne bouge jamais**
et la large marche modale de la zone, mais en dorien au lieu d'eolien — le do
diese eclaircit tout, et c'est exactement ce que dit la page 304 : « le Marais
devient moins lugubre et ressemble de plus en plus a une jungle tropicale ».

Le procede propre a la clairiere est l'**arpege en sauts** : au lieu de monter
son accord degre par degre, il bondit de la fondamentale a la quinte et retombe
— des oiseaux, pas de l'eau.

Ce que la revision ajoute :

- un **crochet** de deux mesures, et c'est le cri du Perroquet : deux croches
  accolees, un saut, une note tenue — `mi sol si . la | fa diese la re . si`.
  Enonce mesure 5, redit tel quel mesure 9, repris mesure 21 puis transpose
  mesure 26. Quatre fois : c'est le babil qu'on emporte ;
- une **reponse**, et elle est litteralement un second oiseau : mesures 8, 11 et
  15, le chant tient sa note et l'arpege — la voix 3, a **droite** — repond le
  meme cri, plus bas. Le premier appelle a gauche, le second repond a droite ;
- un **rythme harmonique** varie : dix mesures changent d'accord au milieu, et
  les mesures 17-18 n'en changent plus du tout ;
- la **surprise** : mesures 17-18, un **do majeur** — le do naturel, alors que
  tout le mode repose sur le do diese. C'est la page 149 : la clairiere ou la
  Maitresse n'est pas, les plumes eparses au sol. La couleur tourne au gris en
  une seconde, et la batterie s'y reduit a un seul charleston ouvert : « un
  silence leger » ;
- une **cadence** : mesure 20, un **si majeur** avec son re diese, la seule
  sensible du morceau, qui rejette dans le mi mineur de la reprise ;
- un **arc de densite** : intro sans batterie, A le babil, B en blanches presque
  nu, A' plein et double de charleston ;
- une **fin qui prepare la boucle** : la derniere mesure redescend sur le si du
  debut, la note meme par laquelle la piece recommence.

**La batterie** est un tambourin, pas une marche : charleston et grosse caisse
legers en A, un seul charleston ouvert toutes les deux mesures en B, la frappe
pleine en A'. Elle prend la voix 5 a droite ; il ne reste que cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cede la place — le bourdon de
tonique est le procede de la zone.

28 mesures a 4/4, 40,0 s. Forme intro(4) - A(8) - B(8) - A'(8).

    python3 oiseaux.py && python3 ../../../midi_to_mb.py oiseaux.mid \\
        BIRDS.MB.BIN --bpm 168 --max 2304 --wav OISEAUX.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 168, 4, 28
LEN = BAR * BARS

# une entree par mesure ; « A|Bm » change d'accord au milieu de la mesure
CHORDS = (["Em", "Em", "D", "D"]
          + ["Em", "G", "A|Bm", "Bm", "Em", "D|A", "A|Bm", "Em"]
          + ["G", "D", "Bm|A", "G", "C", "C", "Am|D", "B"]
          + ["Em", "G|D", "A|Bm", "Em", "D|A", "G|A", "Bm|A", "Em"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "B4:4",                           "B4:2 E5:2",
    "D5:2 F#5:2",                     "A4:2 B4:2",
    "E5:.5 G5:.5 B5:1 A5:2",          "F#5:.5 A5:.5 D6:1 B5:2",  # le crochet
    "C#6:1 E6:1 A5:2",                "B5:4",                    # 8 : la reponse
    "E5:.5 G5:.5 B5:1 A5:2",          "F#5:.5 A5:.5 D6:1 A5:2",  # le crochet, redit
    "C#6:4",                          "B5:1 A5:1 G5:1 E5:1",     # 11 : la reponse
    "D6:2 B5:2",                      "A5:2 F#5:2",              # B : tout s'allonge
    "B5:4",                           "G5:2 D6:2",               # 15 : la reponse
    "E6:2 C6:2",                      "G6:2 E6:2",               # 17-18 : le do naturel
    "C6:1 A5:1 F#5:2",                "D#6:1 F#6:1 B5:2",        # 20 : la cadence
    "E5:.5 G5:.5 B5:1 A5:2",          "F#5:.5 A5:.5 D6:1 B5:2",  # le crochet, une derniere fois
    "C#6:1 E6:1 A5:2",                "B5:1 G5:1 E5:2",
    "F#5:.5 A5:.5 D6:1 A5:2",         "G5:.5 B5:.5 E6:1 C#6:2",  # le crochet, transpose
    "D6:1 B5:1 A5:2",                 "G5:1 E5:1 B4:2",          # 28 : le si de la boucle
]
assert len(MEL) == BARS

CTR = [
    "B3:2 E4:2",                      "G3:2 B3:2",
    "D4:2 F#4:2",                     "A3:2 D4:2",
    "E4:2 B3:2",                      "G3:2 D4:2",
    "A3:2 F#4:2",                     "F#4:2 B3:2",
    "E4:2 G3:2",                      "D4:2 A3:2",
    "C#4:2 D4:2",                     "B3:2 G3:2",
    "G3:2 D4:2",                      "F#4:2 A3:2",
    "B3:2 A3:2",                      "D4:2 B3:2",
    "C4:2 G3:2",                      "E4:2 C4:2",
    "A3:2 F#4:2",                     "D#4:2 B3:2",
    "B3:2 E4:2",                      "G3:2 A3:2",
    "E4:2 D4:2",                      "G3:2 B3:2",
    "F#4:2 E4:2",                     "D4:2 C#4:2",
    "F#4:2 A3:2",                     "E4:2 B3:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le second oiseau, a droite, plus bas
REPONSES = {
    7:  "B4:.5 D5:.5 F#5:1 D5:2",
    10: "A4:.5 C#5:.5 E5:1 D5:2",
    14: "F#4:.5 A4:.5 D5:1 C#5:2",
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
    p = Piece("E", "dorien", BPM, BAR, "La Maitresse des Oiseaux")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("E2"), 0, LEN, retrig=BAR * 4))

    # un tambourin : leger en A, presque rien en B, plein a la reprise
    p.add_drums("K.H...H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums([(0, "O", 4)], t0=BAR * 12)
    p.add_drums([(0, "O", 4)], t0=BAR * 14)
    p.add_drums([(0, "O", 4)], t0=BAR * 16)
    p.add_drums([(0, "O", 4)], t0=BAR * 18)
    p.add_drums([(2, "T"), (2.5, "T"), (3, "S"), (3.5, "S")], t0=BAR * 19)
    p.add_drums("K.H.S.HH", t0=BAR * 20, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("oiseaux.mid"))
