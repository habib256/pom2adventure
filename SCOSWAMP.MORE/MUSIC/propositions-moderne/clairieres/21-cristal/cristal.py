#!/usr/bin/env python3
"""« Le Bassin de Cristal » — clairiere 21. Do dorien, 156.

Variation dans la couleur `sud` : **bourdon de tonique immobile**, marche modale
large, mais le mode est dorien et la **sixte majeure** (le la naturel) revient a
chaque phrase. C'est elle qui fait la difference entre une eau croupie et « une
eau pure comme du cristal » : la meme famille modale que la zone, eclairee d'un
seul degre.

Ce que la revision ajoute :

- un **crochet** de deux mesures bati **sur la sixte** : do - sol - **la** . sol
  | fa . mi bemol. Fondamentale, quinte, la sixte majeure effleuree, et la chute.
  Enonce mesure 5, redit **une octave plus haut** mesure 9, et repris mesure 21
  avec sa tete portee au **mi naturel** — trois fois, chaque fois plus haut ;
- une **reponse** : mesures 8, 11 et 16, le chant tient sa ronde et l'arpege — la
  voix 3, a droite — repond le meme dessin, sixte comprise, une octave plus bas.
  C'est le reflet qui repond a la chose ;
- un **rythme harmonique** varie : dix mesures changent d'accord au milieu, les
  deux mesures de l'eclat n'en changent plus du tout ;
- la **surprise**, et elle est la raison d'etre de la piece : mesures 21-22, le
  mode **bascule en majeur**. Le mi bemol devient **mi naturel**, l'accord de do
  majeur s'installe deux mesures pleines, et l'arpege passe seul en doubles
  croches. Ce n'est plus une variation de couleur, c'est le jour qui tombe dans
  l'eau. Deux mesures, pas une de plus : mesure 23 le mi bemol est revenu, et le
  bassin redevient ce qu'il etait ;
- une **cadence** : mesure 20, un **sol majeur** avec son si naturel, la seule
  sensible du morceau, qui prepare l'eclat au lieu de le subir ;
- le **Lezard** de la page 394, section B : le chant se pose en blanches et la
  batterie prend sa demarche chaloupee — grosse caisse sur le temps et sur la
  croche d'apres, caisse claire au quatrieme. Il s'en retourne, et la piece se
  rouvre ;
- un **arc de densite** : intro sans batterie, A un charleston seul toutes les
  deux croches, B la demarche du Lezard, A' l'eclat plein et le charleston
  ouvert ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le sol,
  la quinte, d'ou le do du debut repart naturellement.

**La batterie** est une eau, pas une marche : rien en A qu'un charleston, la
demarche du Lezard en B, le charleston ouvert dans l'eclat. Elle prend la voix 5
a droite ; il ne reste que cinq parties de hauteur, et c'est la voix d'accords
tenus qui a cede la place — le bourdon de tonique est le procede de la zone.

26 mesures a 4/4, 40,0 s. Forme intro(4) - A(8) l'eau pure - B(8) le Lezard -
A'(6) l'eclat.

    python3 cristal.py && python3 ../../../midi_to_mb.py cristal.mid \\
        CRYSTAL.MB.BIN --bpm 156 --max 2304 --wav CRISTAL.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 156, 4, 26
LEN = BAR * BARS
ECLAT = 20                                 # la mesure ou le mode bascule

# une entree par mesure ; « Eb|Bb » change d'accord au milieu de la mesure
CHORDS = (["Cm", "Cm", "Bb", "Bb"]
          + ["Cm", "Eb|Bb", "F", "Gm", "Cm", "Bb|F", "F|Gm", "Cm"]
          + ["Eb", "Bb|F", "Dm|Gm", "Eb", "Gm", "F|Eb", "Bb|Cm", "G"]
          + ["C", "C", "F|Bb", "Gm|Eb", "F|G", "Cm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "C5:4",                           "C5:2 G5:2",
    "Bb4:2 D5:2",                     "F5:4",
    "C5:1 G5:1 A5:1.5 G5:.5",         "F5:2 Eb5:2",             # le crochet, sur la sixte
    "A5:1 C6:1 F6:2",                 "D6:4",                   # 8 : la reponse
    "C6:1 G6:1 A6:1.5 G6:.5",         "F6:2 D6:2",              # le crochet a l'octave
    "C6:4",                           "G5:1 Eb5:1 C5:2",        # 11 : la reponse
    "Bb5:2 G5:2",                     "F5:2 D5:2",              # B : le Lezard, en blanches
    "A5:2 C6:2",                      "G5:4",                   # 16 : la reponse
    "D6:2 Bb5:2",                     "C6:1 A5:1 F5:2",
    "D6:1 F6:1 Bb5:2",                "B5:1 D6:1 G5:2",         # 20 : la cadence
    "E6:1 G6:1 A6:1.5 G6:.5",         "C6:2 E6:2",              # 21-22 : le mi naturel, l'eclat
    "A5:1 C6:1 F6:2",                 "D6:1 Bb5:1 G5:2",
    "A5:1 C6:1 D6:2",                 "Eb6:1 D6:1 C6:1 G5:1",   # 26 : le sol de la boucle
]
assert len(MEL) == BARS

CTR = [
    "C4:2 Eb4:2",                     "G3:2 C4:2",
    "Bb3:2 D4:2",                     "F4:2 Bb3:2",
    "C4:2 G3:2",                      "Eb4:2 D4:2",
    "A3:2 C4:2",                      "D4:2 Bb3:2",
    "Eb4:2 C4:2",                     "F4:2 C4:2",
    "A3:2 Bb3:2",                     "G3:2 Eb4:2",
    "Bb3:2 G3:2",                     "D4:2 C4:2",
    "F4:2 D4:2",                      "G3:2 Bb3:2",
    "D4:2 Bb3:2",                     "C4:2 Bb3:2",
    "F4:2 Eb4:2",                     "B3:2 D4:2",
    "E4:2 G4:2",                      "C4:2 E4:2",
    "A3:2 D4:2",                      "Bb3:2 G3:2",
    "C4:2 B3:2",                      "Eb4:2 C4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le meme dessin, sixte comprise, une octave plus bas
REPONSES = {
    7:  "G4:1 D5:1 Eb5:1.5 D5:.5",
    10: "F4:1 C5:1 D5:1.5 C5:.5",
    15: "Eb4:1 Bb4:1 C5:1.5 Bb4:.5",
}


def accompagnement():
    """L'arpege bondit a la quinte jusqu'a l'eclat, puis passe en doubles
    croches — sauf aux mesures ou il repond au chant."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in REPONSES:
            out += line(REPONSES[i], t)
        elif i < 4:                    # l'intro : deux sons par demi-mesure
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 1.0, (0, 2), lo=54)
        elif i < ECLAT:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.5,
                            (0, 2, 1, 2), lo=54)
        else:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.25,
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
    p = Piece("C", "dorien", BPM, BAR, "Le Bassin de Cristal")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("C2"), 0, LEN, retrig=BAR * 4))

    # l'eau : un charleston seul, la demarche du Lezard, puis l'eclat
    p.add_drums("..H...H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K..K..S.", t0=BAR * 12, length=BAR * 8)
    p.add_drums("K.H.O.H.", t0=BAR * 20, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("cristal.mid"))
