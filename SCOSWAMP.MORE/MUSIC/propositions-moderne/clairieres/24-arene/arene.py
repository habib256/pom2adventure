#!/usr/bin/env python3
"""« Ce qui Reste du Combat » — clairiere 24. Mi eolien, 164.

Variation dans la couleur `sud` : **bourdon de tonique immobile** et la marche
i-VI-III-VII de la zone (Em-C-G-D), mais prise a 164 et jouee **pointee**. Le
rythme long-bref du premier temps est le procede propre a la clairiere : il
revient a chaque mesure de A et de A', et c'est tout ce qui separe cette piece
d'un theme de voyage. On n'est pas dans un combat — la page 010 ne montre que
ses traces : « le sol est foule, l'herbe humide tachee de sang, et deux fleches
sont encore plantees dans un arbre ».

Ce que la revision ajoute :

- un **crochet** de deux mesures, entierement pointe : mi . sol - si | do . si -
  sol. C'est le rythme de la clairiere devenu une phrase. Enonce mesure 5, redit
  mesure 9, repris mesures 21 et 24, et porte **a l'octave** mesure 26. Cinq
  fois : c'est un champ de bataille, on y repasse ;
- une **reponse** : mesures 8, 11 et 17, le chant tient et l'arpege — la voix 3,
  a droite — repond le crochet, pointe lui aussi, une octave plus bas. Deux
  voix qui se cherchent dans une clairiere vide : c'est exactement ce que le
  texte promet a qui s'attarde ;
- un **rythme harmonique** varie : quinze mesures changent d'accord au milieu,
  et les deux mesures de si mineur n'en changent plus du tout — la fouille
  s'arrete sur place ;
- la **surprise**, en deux temps. Mesures 18-19, **la batterie se tait
  completement** et la basse tient une ronde : c'est le moment ou l'on entend
  quelque chose. Puis mesure 19 un **fa majeur** — le second degre abaisse, le
  demi-ton phrygien de la zone `danger`, pose entier sur le bourdon de mi qu'il
  frotte. Les ennemis caches ne sont plus une promesse. Un roulement de toms, et
  la reprise part ;
- une **cadence** : mesure 20, un **si majeur** avec son re diese, la seule
  sensible du morceau, qui rejette dans le mi mineur ; elle revient mesure 27 ;
- un **arc de densite** : grosse caisse seule mesure 3, marche pointee en A,
  charleston en B, deux mesures de rien, puis A' plein sur huit mesures ;
- une **fin qui prepare la boucle** : la derniere mesure redescend sur le **si**
  du debut, et l'on repasse.

**La batterie** est une marche martiale calee sur le pointe du chant : grosse
caisse au premier temps et sur la croche pointee qui suit, caisse claire au
troisieme. Elle prend la voix 5 a droite ; il ne reste que cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cede la place — le bourdon de
tonique est le procede de la zone.

28 mesures a 4/4, 41,0 s. Forme intro(4) - A(8) les traces - B(8) la fouille -
A'(8).

    python3 arene.py && python3 ../../../midi_to_mb.py arene.mid \\
        ARENA.MB.BIN --bpm 164 --max 2304 --wav ARENE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 164, 4, 28
LEN = BAR * BARS

# une entree par mesure ; « C|G » change d'accord au milieu de la mesure
CHORDS = (["Em", "Em", "C", "C"]
          + ["Em", "C|G", "G|D", "D|Am", "Em", "Am|Bm", "C|D", "Em"]
          + ["C", "G|D", "Am|Em", "C|D", "Bm", "Bm", "F", "B"]
          + ["Em", "C|G", "G|D", "Em", "Am|Bm", "C|Em", "Am|B", "Em"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "B4:4",                           "B4:2 E5:2",
    "C5:2 G5:2",                      "D5:2 B4:2",
    "E5:1.5 G5:.5 B5:2",              "C6:1.5 B5:.5 G5:2",      # le crochet, pointe
    "D6:1.5 B5:.5 G5:2",              "A5:4",                   # 8 : la reponse
    "E5:1.5 G5:.5 B5:2",              "C6:1.5 A5:.5 E5:2",      # le crochet, redit
    "G5:4",                           "B5:1.5 G5:.5 E5:2",      # 11 : la reponse
    "G5:1 C6:1 E6:2",                 "D6:1 B5:1 G5:2",         # B : le pointe disparait
    "A5:1 C6:1 E6:2",                 "G6:2 E6:2",
    "F#6:4",                          "D6:1 F#6:1 B5:2",        # 17 : la reponse
    "F5:1 A5:1 C6:2",                 "D#6:1 F#6:1 B5:2",       # 19 : le fa majeur, 20 : la cadence
    "E5:1.5 G5:.5 B5:2",              "C6:1.5 B5:.5 G5:2",      # le crochet, repris
    "D6:1.5 B5:.5 G5:2",              "E6:1.5 B5:.5 G5:2",
    "C6:1.5 A5:.5 E5:2",              "E6:1.5 G6:.5 B6:2",      # le crochet a l'octave
    "A5:1.5 C6:.5 F#6:2",             "G5:1 E5:1 B4:2",         # 28 : le si de la boucle
]
assert len(MEL) == BARS

CTR = [
    "E4:2 B3:2",                      "G3:2 E4:2",
    "C4:2 E4:2",                      "G3:2 C4:2",
    "B3:2 E4:2",                      "C4:2 B3:2",
    "D4:2 A3:2",                      "F#4:2 E4:2",
    "E4:2 G3:2",                      "A3:2 F#4:2",
    "E4:2 D4:2",                      "B3:2 E4:2",
    "C4:2 G3:2",                      "B3:2 A3:2",
    "A3:2 G3:2",                      "E4:2 F#4:2",
    "D4:2 B3:2",                      "F#4:2 D4:2",
    "A3:2 C4:2",                      "D#4:2 F#4:2",
    "E4:2 B3:2",                      "G3:2 D4:2",
    "B3:2 A3:2",                      "E4:2 G3:2",
    "C4:2 D4:2",                      "E4:2 B3:2",
    "A3:2 D#4:2",                     "G3:2 E4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le crochet, pointe lui aussi, une octave plus bas
REPONSES = {
    7:  "D4:1.5 F#4:.5 A4:2",
    10: "E4:1.5 G4:.5 A4:2",
    16: "B4:1.5 D5:.5 F#5:2",
}


def accompagnement():
    """L'arpege de la marche — sauf aux mesures ou il repond au chant."""
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
    """Quatre noires martelees : la marche de ceux qui sont passes par la.
    Une ronde a la mesure 19, la seule ou l'on s'arrete pour ecouter."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if i == 18:
            out += progression([b], t, BAR, [(0, 4)], lo=48)
        elif "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR,
                               [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("E", "eolien", BPM, BAR, "Ce qui Reste du Combat")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("E2"), 0, LEN, retrig=BAR * 4))

    # la marche martiale, calee sur le pointe du chant
    p.add_drums("K...K...", t0=BAR * 2, length=BAR * 2)
    p.add_drums("K..KS...", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.HKS.H.", t0=BAR * 12, length=BAR * 5)
    # mesures 18-19 : rien. On ecoute.
    p.add_drums([(0, "K"), (2, "T"), (2.5, "T"), (3, "T"), (3.5, "S")],
                t0=BAR * 19)
    p.add_drums("K.HKS.H.", t0=BAR * 20, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("arene.mid"))
