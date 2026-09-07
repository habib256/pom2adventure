#!/usr/bin/env python3
"""« Le Seul Passage » — clairiere 15, le pont sur la Croupie. Si bemol dorien, 154.

Variation dans la couleur `riviere` : dorien, **bourdon sur la quinte** (fa),
arpege de croches sans arret. Mais la zone regarde l'eau ; cette piece la
traverse. D'ou la basse en noires marchees, quatre pas par mesure, du debut a
la fin : c'est le seul endroit du Marais ou l'on passe du nord au sud
(`CARTOGRAPHIE.md` § 1), et la musique y marche.

Ce que la revision ajoute :

- une **batterie de marche**, et c'est la piece des douze qui la reclamait le
  plus : grosse caisse au premier temps, caisse claire au troisieme, charleston
  entre les deux — le pas sur les planches. Elle entre mesure 3, seule, avant
  tout le reste ; elle se degarnit quand le soupcon vient ; elle se tait
  completement sur le piege ; elle revient doublee a la reprise ;
- un **crochet** de deux mesures : si bemol - re bemol - fa - la bemol, l'accord
  monte marche par marche, puis retombe sur la quinte. Enonce mesure 5, repris
  mesure 9 avec l'octave au sommet, et redit **une octave plus haut** mesure 21 :
  on a traverse ;
- une **reponse** : mesures 8, 11 et 16, le chant tient et l'arpege repond a
  droite. La reponse de la mesure 16 annonce le sol bemol **avant** que
  l'harmonie ne l'ose : c'est elle qui a vu le piege ;
- un **rythme harmonique** varie : huit mesures changent d'accord au milieu, et
  la basse y garde ses quatre noires — deux pas sur chaque accord au lieu de
  quatre ;
- la **surprise** : mesures 17-18, un **sol bemol majeur**. Le sol naturel est
  la note qui fait le dorien ; l'abaisser d'un demi-ton eteint la piece d'un
  coup. C'est la page 045 exactement — « ce pont vous parait trop simple ; il
  doit sans doute dissimuler un piege ». La batterie s'y arrete net : on ne pose
  plus le pied ;
- deux **cadences** franches : mesure 20 et mesure 25, un **fa majeur** avec son
  la naturel, la seule sensible du morceau, qui jette dans le si bemol mineur ;
- un **arc de densite** : intro nue, A la marche, B qui se degarnit, deux mesures
  de piege sans batterie, roulement de toms, A' a l'octave et double ;
- une **fin qui prepare la boucle** : la derniere mesure retombe de si bemol a
  fa, la quinte du bourdon, et la marche repart.

La batterie prend la voix 5 a droite : il ne reste que cinq parties de hauteur,
et c'est la voix d'accords tenus qui a cede la place. Le bourdon sur la quinte
est le procede de la zone, on ne le retire pas.

26 mesures a 4/4, 40,5 s. Forme intro(4) - A(8) la traversee - B(8) le soupcon -
A'(6) la reprise, a l'octave.

    python3 pont.py && python3 ../../../midi_to_mb.py pont.mid \\
        BRIDGE.MB.BIN --bpm 154 --max 2304 --wav PONT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 154, 4, 26
LEN = BAR * BARS

# une entree par mesure ; « Eb|Fm » change d'accord au milieu de la mesure
CHORDS = (["Bbm", "Bbm", "Ab", "Ab"]
          + ["Bbm", "Fm", "Db", "Eb|Fm", "Bbm", "Ab|Eb", "Fm|Eb", "Bbm"]
          + ["Db", "Ab", "Eb|Cm", "Db", "Gb", "Gb", "Cm|Db", "F"]
          + ["Bbm", "Db|Ab", "Eb|Cm", "Db|Eb", "F", "Bbm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "Bb4:4",                          "Bb4:2 F5:2",
    "Ab4:2 C5:2",                     "Eb5:4",
    "Bb4:1 Db5:1 F5:1 Ab5:1",         "Bb5:2 F5:2",             # le crochet
    "Db5:1 F5:1 Ab5:2",               "Bb5:4",                  # 8 : la reponse
    "Bb4:1 Db5:1 F5:1 Bb5:1",         "C6:2 Ab5:2",             # le crochet, a l'octave
    "F5:4",                           "Db5:1 C5:1 Bb4:2",       # 11 : la reponse
    "F5:1 F5:1 Ab5:2",                "Eb5:1 Eb5:1 C5:2",       # B : le pas hesite
    "Eb5:1 G5:1 Eb5:1 C5:1",          "F5:4",                   # 16 : la reponse voit le piege
    "Gb5:2 Db6:2",                    "Gb5:1 F5:1 Db5:2",       # 17-18 : le sol bemol
    "Eb5:1 G5:1 C6:2",                "A5:1 C6:1 F6:2",         # 20 : la cadence
    "Bb5:1 Db6:1 F6:1 Ab6:1",         "Bb6:2 F6:2",             # le crochet une octave plus haut
    "Eb6:1 C6:1 Ab5:2",               "Db6:1 Bb5:1 Gb5:2",      # le piege, garde en memoire
    "A5:1 C6:1 F6:2",                 "Bb5:3 F5:1",             # 26 : la quinte de la boucle
]
assert len(MEL) == BARS

CTR = [
    "Bb3:2 Db4:2",                    "F4:2 Bb3:2",
    "Ab3:2 C4:2",                     "Eb4:2 Ab3:2",
    "Bb3:2 Db4:2",                    "C4:2 Ab3:2",
    "Db4:2 F4:2",                     "Eb4:2 C4:2",
    "F4:2 Db4:2",                     "Ab3:2 G4:2",
    "Ab3:2 Bb3:2",                    "Db4:2 Bb3:2",
    "Ab3:2 F4:2",                     "Eb4:2 C4:2",
    "Bb3:2 Eb4:2",                    "F4:2 Ab3:2",
    "Gb3:2 Bb3:2",                    "Db4:2 Bb3:2",
    "G3:2 Ab3:2",                     "A3:2 C4:2",
    "Bb3:2 F4:2",                     "Ab3:2 Eb4:2",
    "G4:2 Eb4:2",                     "F4:2 Bb3:2",
    "C4:2 A3:2",                      "Db4:2 Bb3:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant, une octave sous lui, en citant le crochet
REPONSES = {
    7:  "F4:1 Ab4:1 C5:1 Db5:1",
    10: "C5:1 Bb4:1 Ab4:1 F4:1",
    15: "F4:1 Gb4:1 F4:1 Ab4:1",       # elle annonce le sol bemol
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
    """Quatre pas par mesure, du debut a la fin : on traverse. Quand l'accord
    change au milieu, ce sont deux pas sur chacun."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR,
                               [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("Bb", "dorien", BPM, BAR, "Le Seul Passage")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("F2"), 0, LEN, retrig=BAR * 4))

    # le pas sur les planches : il approche, il marche, il hesite, il s'arrete
    p.add_drums("K.......", t0=BAR * 2, length=BAR * 2)
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K...S...", t0=BAR * 12, length=BAR * 4)
    # mesures 17-18 : rien. On ne pose plus le pied.
    p.add_drums("K.H.S.H.", t0=BAR * 18, length=BAR * 2)
    p.add_drums([(2, "T"), (2.5, "T"), (3, "T"), (3.5, "T")], t0=BAR * 19)
    p.add_drums("K.HKS.H.", t0=BAR * 20, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("pont.mid"))
