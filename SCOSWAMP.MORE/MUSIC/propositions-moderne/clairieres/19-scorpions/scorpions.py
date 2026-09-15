#!/usr/bin/env python3
"""« La Nuee » — clairiere 19, la clairiere des scorpions. Re phrygien, 187,5.

Variation dans la couleur `danger` : le mode **phrygien**, donc le demi-ton pose
juste au-dessus de la tonique — ici mi bemol contre re — et le **bourdon de
tonique** immobile, exactement le procede de `DANGER.MB`. Ce qui change, c'est
la vitesse : 187,5 a la noire, le tempo le plus rapide des trente-cinq (a egalite
avec les clairieres 8 et 10), parce que
la page 118 ne laisse pas le choix (« des dizaines de petits scorpions accourent
vers vous. Tentez votre Chance ») et que la page 319 s'appelle « Vous vous hatez
de choisir une direction ».

Ce que la revision ajoute :

- un **crochet** de deux mesures, et c'est le grouillement lui-meme : quatre
  doubles croches qui montent l'accord d'un trait, une noire au sommet, une
  blanche qui retombe — puis la meme chose un demi-ton plus haut, sur le **mi
  bemol phrygien**. Enonce mesure 5, redit mesure 9, repris mesures 21-22 : la
  paire re / mi bemol est ce qu'on emporte de cette clairiere ;
- une **reponse** : mesures 8, 11 et 17, le chant tient et l'arpege — la voix 3,
  a droite — repond la meme montee, plus bas. Une bete appelle a gauche, une
  autre repond a droite : c'est une nuee, pas un solo ;
- un **rythme harmonique** varie : neuf mesures changent d'accord au milieu, ce
  qui donne deux pas de basse au lieu de quatre, et les mesures 17-18 n'en
  changent plus du tout ;
- la **surprise**, et c'est **le silence** : mesure 17, tout s'arrete. La
  batterie se tait, la basse tient une ronde, le contre-chant une ronde, le
  chant un mi bemol tenu, et l'arpege seul fait battre mi bemol contre re. C'est
  « Tentez votre Chance » : une seconde ou rien ne bouge avant que tout reparte.
  Un roulement de toms sur la mesure 18, et la nuee est de nouveau sur vous ;
- une **cadence** : mesure 20, un **la majeur** avec son do diese — la sensible,
  interdite au phrygien, et donc la seule chose qui puisse conclure ici ;
- un **arc de densite** : intro a deux sons par demi-mesure, la grosse caisse
  seule mesure 3, le galop en A, il se double en B, le silence, puis A' plein ;
- une **fin qui prepare la boucle** : la derniere mesure lache la nuee, ne garde
  que le frottement mi bemol - re, et retombe sur le **la** par lequel la piece
  recommence.

**La batterie** est un galop, pas une marche : grosse caisse sur le temps et sur
la croche qui suit, caisse claire au troisieme, charleston entre les deux. Elle
prend la voix 5 a droite ; il ne reste que cinq parties de hauteur, et c'est la
voix d'accords tenus qui a cede la place — le bourdon de tonique est le procede
de la zone `danger`.

24 mesures a 4/4, 30,7 s. Forme intro(4) - A(8) - B(8) l'assaut - A'(4).

    python3 scorpions.py && python3 ../../../midi_to_mb.py scorpions.mid \\
        SCORPIONS.MB.BIN --bpm 187.5 --max 2304 --wav SCORPIONS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 3000 / 16, 4, 24
LEN = BAR * BARS
GEL = 16                                   # la mesure ou tout se fige

# une entree par mesure ; « Gm|Cm » change d'accord au milieu de la mesure
CHORDS = (["Dm", "Dm", "Eb", "Eb"]
          + ["Dm", "Eb", "Gm|Cm", "Bb|F", "Dm", "Eb|Dm", "Gm|A", "Dm"]
          + ["Gm", "F|Eb", "Bb", "Cm|Gm", "Eb", "Eb", "Cm|Dm", "A"]
          + ["Dm", "Eb|Dm", "Gm|A", "Dm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "A4:.5 Bb4:.5 A4:1 A4:2",         "A4:.5 Bb4:.5 A4:1 D5:2",
    "Bb4:.5 C5:.5 Bb4:1 G4:2",        "Eb5:2 D5:2",
    "D5:.25 F5:.25 A5:.5 D6:1 A5:2",                            # le crochet
    "Eb5:.25 G5:.25 Bb5:.5 Eb6:1 Bb5:2",                        # le crochet, un demi-ton plus haut
    "D6:.5 Bb5:.5 G5:1 C6:2",         "D6:4",                   # 8 : la reponse
    "D5:.25 F5:.25 A5:.5 D6:1 A5:2",                            # le crochet, redit
    "Eb6:.5 Bb5:.5 G5:1 D5:2",        "A5:4",                   # 11 : la reponse
    "F5:.5 D5:.5 A4:1 D5:2",
    "G5:.25 A5:.25 Bb5:.25 D6:.25 G6:1 D6:2",
    "F6:.25 C6:.25 A5:.25 F5:.25 Bb5:1 G5:2",
    "D6:.5 Bb5:.5 F5:1 D6:2",
    "C6:.5 Eb6:.5 G5:1 D6:2",
    "Eb6:4",                                                    # 17 : le gel
    "Eb6:2 D6:2",
    "C6:.25 Eb6:.25 G6:.25 Eb6:.25 C6:1 A5:2",
    "C#6:1 E6:1 A5:2",                                          # 20 : la cadence
    "D5:.25 F5:.25 A5:.5 D6:1 A5:2",                            # le crochet, une derniere fois
    "Eb5:.25 G5:.25 Bb5:.5 Eb6:1 Bb5:2",
    "D6:.5 Bb5:.5 G5:1 A5:2",         "F5:.5 Eb5:.5 D5:2 A4:1",  # 24 : le la de la boucle
]
assert len(MEL) == BARS

CTR = [
    "D4:2 F4:2",                      "A3:2 D4:2",
    "Bb3:2 Eb4:2",                    "G3:2 Bb3:2",
    "D4:2 A3:2",                      "Eb4:2 Bb3:2",
    "G3:2 Eb4:2",                     "D4:2 C4:2",
    "F4:2 D4:2",                      "Bb3:2 A3:2",
    "D4:2 C#4:2",                     "A3:2 D4:2",
    "Bb3:2 D4:2",                     "C4:2 Bb3:2",
    "F4:2 D4:2",                      "Eb4:2 D4:2",
    "Bb3:4",                          "Eb4:2 G3:2",
    "Eb4:2 F4:2",                     "C#4:2 E4:2",
    "D4:2 A3:2",                      "Bb3:2 F4:2",
    "D4:2 E4:2",                      "F4:2 D4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : la meme montee, une octave plus bas
REPONSES = {
    7:  "F4:.5 A4:.5 D5:1 A4:2",
    10: "D5:.5 Bb4:.5 G4:1 A4:2",
    16: "Eb5:.5 D5:.5 Eb5:.5 D5:.5 Bb4:2",     # seul, dans le gel
}


def accompagnement():
    """L'arpege de la nuee — sauf aux mesures ou il repond au chant."""
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
    """Quatre noires des la premiere mesure : rien ne se met en place, on court.
    Deux pas quand l'accord change au milieu ; une ronde au gel."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if i == GEL:
            out += progression([b], t, BAR, [(0, 4)], lo=48)
        elif "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR,
                               [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=48)
    return out


def build():
    p = Piece("D", "phrygien", BPM, BAR, "La Nuee")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("D2"), 0, LEN, retrig=BAR * 4))

    # le galop, puis rien du tout, puis le galop double
    p.add_drums("K...K...", t0=BAR * 2, length=BAR * 2)
    p.add_drums("K.HKS.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.HKS.HS", t0=BAR * 12, length=BAR * 4)
    # mesure 17 : rien. Tentez votre Chance.
    p.add_drums([(0, "K"), (2, "T"), (2.5, "T"), (3, "T"), (3.5, "T")],
                t0=BAR * 17)
    p.add_drums("K.HKS.H.", t0=BAR * 18, length=BAR * 2)
    p.add_drums("K.HKS.HS", t0=BAR * 20, length=BAR * 4)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("scorpions.mid"))
