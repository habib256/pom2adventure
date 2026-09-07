#!/usr/bin/env python3
"""« La Berge aux Crocodiles » — clairiere 13, la Riviere Croupie. Sol dorien, 132.

Variation dans la couleur `riviere` : meme famille modale (dorien), meme procede
identifiable — le **bourdon sur la quinte**, jamais sur la tonique, si bien que
rien ne se pose et que tout coule. Ici la quinte est **re**, le mode est sol
dorien, et la piece regarde l'eau au lieu de la franchir.

La page 295 dit deux choses : la rive opposee est a deux cents metres, et le
cours d'eau est infeste de crocodiles. D'ou la largeur — melodie en valeurs
longues — et la basse en figure breve-longue, une machoire qui se referme sous
la surface.

Ce que la revision ajoute :

- un **crochet** de deux mesures, `re-sol-si bemol . la | sol . re`, la montee
  de l'accord de sol mineur qui retombe d'un demi-pas. Il est enonce mesure 5,
  repris mesure 9 la ou il monte au do, et redit tel quel a la reprise (mes. 21) :
  trois fois, c'est ce qu'on retient de la clairiere ;
- une **reponse** : mesures 7, 11 et 19 le chant tient une note et c'est
  l'arpege — la voix 3, a droite — qui repond, une octave plus bas, en citant le
  crochet. La question est a gauche, la reponse a droite ;
- un **rythme harmonique** qui bouge : la plupart des mesures gardent leur
  accord, six en changent au milieu (`F|C`, `Dm|C`, `C|Dm`, `Bb|C`, `F|C`), et
  la basse y marche en deux pas au lieu de sa breve-longue ;
- la **surprise** : mesures 17-18, un **mi bemol majeur** — l'accord etranger au
  dorien, celui qui eteint le mi naturel, seul reflet de lumiere de la piece —
  pose sur le bourdon de re, dont il frotte le demi-ton. La batterie s'y **tait**
  completement : le coeur s'arrete deux mesures ;
- une **cadence** franche : mesure 20, un **re majeur** avec son fa diese, la
  seule sensible du morceau, qui rejette dans le sol mineur de la reprise ;
- un **arc de densite** : intro en blanches d'arpege sans batterie, A en croches
  avec le coeur lent, B qui serre, silence, roulement de toms, A' plein ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le re du
  debut, la note meme par laquelle la piece recommence.

**La batterie** est le coeur sourd du danger, pas une marche : grosse caisse au
premier temps, un tom au troisieme une mesure sur deux, une caisse claire quand
B se resserre. Elle prend la voix 5 a droite ; il ne reste que cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cede la place — le bourdon fait
le caractere de la piece, on ne le retire pas.

24 mesures a 4/4, 43,6 s. Forme intro(4) - A(8) - B(8) - A'(4).

    python3 croupie.py && python3 ../../../midi_to_mb.py croupie.mid \\
        STAGNANT.MB.BIN --bpm 132 --max 2304 --wav CROUPIE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 132, 4, 24
LEN = BAR * BARS

# une entree par mesure ; « F|C » change d'accord au milieu de la mesure
CHORDS = (["Gm", "Gm", "F", "F"]
          + ["Gm", "Dm", "Bb", "C", "Gm", "F|C", "Dm|C", "Gm"]
          + ["Bb", "F", "C|Dm", "Bb", "Eb", "Eb", "C", "D"]
          + ["Gm", "Bb|C", "F|C", "Gm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "D5:4",                           "D5:2 G5:2",
    "F5:4",                           "C5:2 D5:2",
    "D5:1 G5:1 Bb5:1.5 A5:.5",        "G5:2 D5:2",              # le crochet
    "Bb5:4",                          "C6:2 A5:2",              # 7 : la reponse
    "D5:1 G5:1 Bb5:1.5 C6:.5",        "D6:2 G5:2",              # le crochet, ouvert
    "A5:4",                           "Bb5:1 A5:1 G5:2",        # 11 : la reponse
    "F6:2 D6:2",                      "C6:1 A5:1 F5:2",
    "G5:1 C6:1 E6:1 D6:1",            "D6:1.5 Bb5:.5 G5:2",
    "Eb6:2 Bb5:2",                    "Eb6:1 D6:1 Bb5:2",       # 17-18 : le reflet s'eteint
    "E6:1 C6:1 A5:2",                 "F#5:1 A5:1 D6:2",        # 20 : la cadence
    "D5:1 G5:1 Bb5:1.5 A5:.5",        "G5:2 Bb5:2",             # le crochet, une derniere fois
    "C6:1 A5:1 G5:2",                 "G5:3 D5:1",              # 24 : le re de la boucle
]
assert len(MEL) == BARS

CTR = [
    "G3:2 Bb3:2",                     "D4:2 G3:2",
    "A3:2 C4:2",                      "F4:2 A3:2",
    "G3:2 Bb3:2",                     "A3:2 F4:2",
    "Bb3:2 D4:2",                     "C4:2 E4:2",
    "D4:2 Bb3:2",                     "A3:2 C4:2",
    "F4:2 E4:2",                      "D4:2 G3:2",
    "D4:2 F4:2",                      "C4:2 A3:2",
    "E4:2 F4:2",                      "D4:2 Bb3:2",
    "Eb4:2 G3:2",                     "Bb3:2 Eb4:2",
    "C4:2 E4:2",                      "F#4:2 A3:2",
    "G3:2 D4:2",                      "Bb3:2 E4:2",
    "A3:2 G3:2",                      "D4:2 G3:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant, une octave sous lui, en citant le crochet
REPONSES = {
    6:  "G4:1 Bb4:1 D5:1.5 C5:.5",
    10: "D5:1 C5:1 Bb4:1 G4:1",
    18: "C5:1 A4:1 G4:1 E4:1",
}


def accompagnement():
    """L'arpege du courant — sauf aux mesures ou il repond au chant."""
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
    """Breve-longue — la machoire — tant que l'accord tient toute la mesure ;
    deux pas quand il change au milieu."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR, [(0, 2), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("G", "dorien", BPM, BAR, "La Berge aux Crocodiles")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("D2"), 0, LEN, retrig=BAR * 4))

    # le coeur sourd : rien a l'intro, lent en A, serre en B, muet aux mes. 17-18
    p.add_drums("K...T...K.......", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K...K.S.", t0=BAR * 12, length=BAR * 4)
    p.add_drums("K...K...", t0=BAR * 18, length=BAR * 2)
    p.add_drums([(2, "T"), (2.5, "T"), (3, "T"), (3.5, "T")], t0=BAR * 19)
    p.add_drums("K...S..K", t0=BAR * 20, length=BAR * 4)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("croupie.mid"))
