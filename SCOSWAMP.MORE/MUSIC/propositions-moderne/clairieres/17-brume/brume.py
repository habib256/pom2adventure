#!/usr/bin/env python3
"""« La Brume Fetide » — clairiere 17. Do eolien, 128.

Variation dans la couleur `sud` : eolien comme la zone, **bourdon de tonique
immobile** comme la zone, mais transpose sur do et pris par le bas. Le procede
propre a la clairiere est la **descente** : la page 094 commence par « le sentier
descend », et la piece descend en effet, du do aigu jusqu'au do grave.

C'est la piece la plus lente des douze — 128, le plancher du dossier — et elle
le reste : on ne court pas dans une odeur pareille.

Ce que la revision ajoute :

- un **crochet** de deux mesures qui **est** la descente : do - si bemol - la
  bemol . sol | fa . do. Quatre notes qui tombent, deux qui se posent. Enonce
  mesure 5, repris mesure 9 avec une autre chute, redit tel quel mesure 18 ;
- une **reponse** : mesures 7, 12 et 14, le chant tient une ronde et l'arpege —
  la voix 3, a droite — laisse retomber la meme descente une octave plus bas.
  C'est la brume qui repond au marcheur ;
- un **rythme harmonique** varie : sept mesures changent d'accord au milieu, les
  deux mesures de re bemol n'en changent plus du tout ;
- la **surprise**, et c'est la seule chose qui arrive dans cette clairiere :
  mesures 15-16, un **re bemol majeur**, le second degre abaisse — le demi-ton
  phrygien de la zone `danger`, cite ici a decouvert. Il frotte le **do du
  bourdon** d'un demi-ton entier, deux mesures durant, pendant que le chant fait
  battre re bemol contre do : c'est l'odeur, et c'est le point d'ENDURANCE. La
  batterie s'y **tait** ;
- une **cadence** : mesure 17, un **sol majeur** avec son si naturel, la seule
  sensible du morceau, qui rejette dans le do mineur de la reprise ;
- un **arc de densite** : intro sans batterie, A un coeur lent, B qui se serre,
  deux mesures muettes, A' pleine ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le do du
  debut, et le sentier redescend.

**La batterie** est un coeur qui bat sourd, jamais une marche : grosse caisse au
premier temps, un tom au troisieme une mesure sur deux, une caisse claire quand
la reprise arrive. Elle prend la voix 5 a droite ; il ne reste que cinq parties
de hauteur, et c'est la voix d'accords tenus qui a cede la place — le bourdon de
tonique est le procede de la zone.

22 mesures a 4/4, 41,3 s. Forme intro(4) - A(6) la descente - B(6) l'odeur -
A'(6) la brume se referme.

    python3 brume.py && python3 ../../../midi_to_mb.py brume.mid \\
        MIST.MB.BIN --bpm 128 --max 2304 --wav BRUME.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 128, 4, 22
LEN = BAR * BARS

# une entree par mesure ; « Bb|Ab » change d'accord au milieu de la mesure
CHORDS = (["Cm", "Cm", "Ab", "Ab"]
          + ["Cm", "Bb|Ab", "Gm", "Fm|Cm", "Ab|Bb", "Cm"]
          + ["Ab", "Eb|Bb", "Fm|Gm", "Ab", "Db", "Db"]
          + ["G", "Cm", "Ab|Bb", "Fm|G", "Ab|G", "Cm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "C5:4",                           "C5:2 Eb5:2",
    "C5:2 Ab4:2",                     "Eb5:2 C5:2",
    "C6:1 Bb5:1 Ab5:1.5 G5:.5",       "F5:2 C5:2",              # le crochet : la descente
    "G5:4",                           "Ab5:1 F5:1 C5:2",        # 7 : la reponse
    "C6:1 Bb5:1 Ab5:1.5 F5:.5",       "Eb5:1 D5:1 C5:2",        # le crochet, autre chute
    "Eb5:2 C5:2",                     "G5:4",                   # 12 : la reponse
    "Ab4:1 C5:1 F5:2",                "Eb5:4",                  # 14 : la reponse
    "Db5:1 C5:1 Db5:1 C5:1",          "F5:2 Db5:2",             # 15-16 : le re bemol
    "B4:1 D5:1 G5:2",                 "C6:1 Bb5:1 Ab5:1.5 G5:.5",  # 17 : la cadence, 18 : le crochet
    "F5:2 D5:2",                      "Eb5:1 C5:1 B4:2",
    "Ab5:2 G5:2",                     "Eb5:1 D5:1 C5:2",        # 22 : le do de la boucle
]
assert len(MEL) == BARS

CTR = [
    "C4:2 Eb4:2",                     "G3:2 C4:2",
    "Ab3:2 C4:2",                     "Eb4:2 Ab3:2",
    "C4:2 G3:2",                      "Bb3:2 C4:2",
    "D4:2 Bb3:2",                     "Ab3:2 G3:2",
    "Eb4:2 D4:2",                     "C4:2 G3:2",
    "C4:2 Eb4:2",                     "G3:2 F4:2",
    "Ab3:2 Bb3:2",                    "Eb4:2 C4:2",
    "Ab3:2 F4:2",                     "Db4:2 Ab3:2",
    "B3:2 D4:2",                      "C4:2 Eb4:2",
    "C4:2 D4:2",                      "Ab3:2 B3:2",
    "Eb4:2 D4:2",                     "G3:2 C4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : la meme descente, une octave plus bas
REPONSES = {
    6:  "C5:1 Bb4:1 Ab4:1.5 G4:.5",
    11: "Bb4:1 Ab4:1 G4:1 Eb4:1",
    13: "Eb4:1 G4:1 C5:1.5 Bb4:.5",
}


def accompagnement():
    """L'arpege qui monte de trois sons et retombe — les tourbillons de brume ;
    sauf aux mesures ou il repond au chant."""
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
    """Deux blanches, rien de plus : on avance a peine. Deux pas de noire
    seulement quand l'accord change au milieu de la mesure."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR, [(0, 2), (-1, 2)], lo=48)
    return out


def build():
    p = Piece("C", "eolien", BPM, BAR, "La Brume Fetide")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("C2"), 0, LEN, retrig=BAR * 4))

    # le coeur sourd, tres lent — et muet sur le re bemol
    p.add_drums("K.......K...T...", t0=BAR * 4, length=BAR * 6)
    p.add_drums("K...T...", t0=BAR * 10, length=BAR * 4)
    # mesures 15-16 : rien
    p.add_drums("K...S..K", t0=BAR * 16, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 16)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("brume.mid"))
