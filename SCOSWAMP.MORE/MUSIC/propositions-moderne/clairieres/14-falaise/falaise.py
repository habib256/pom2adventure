#!/usr/bin/env python3
"""« Le Ciel s'Ouvre » — clairiere 14, sommet de la falaise. Si dorien, 144.

Variation dans la couleur `riviere` : dorien, et le **bourdon sur la quinte**
(fa diese), la marque de la zone. Ce qui change, c'est la direction : la riviere
coule, la falaise monte. L'arpege n'y tourne plus sur trois sons mais en atteint
**quatre**, l'octave comprise — une figure qui s'ouvre au lieu de tourner, comme
le ciel qui remplace le feuillage a la page 183.

**Cette piece est la seule des douze sans batterie**, et c'est un choix, pas un
oubli. Un seul coup de bruit couterait la voix 5 et ramenerait la piece a cinq
parties de hauteur : au sommet de la falaise, c'est la largeur qui compte, pas
la frappe. Les six voix sont donc gardees — melodie, arpege a quatre sons,
contre-chant, accords tenus, basse en blanches et bourdon. Le vent n'a pas de
tambour.

Ce que la revision ajoute :

- un **crochet** de deux mesures : si - fa diese - la - si, la quinte montee
  d'un trait puis la septieme et l'octave, et la retombee sur la quinte. Enonce
  mesure 5, varie mesure 9, et redit **a l'octave** mesure 21, ou il touche le si
  aigu, la note la plus haute de tout le dossier ;
- une **reponse** : mesures 8, 11 et 15, le chant tient une ronde et l'arpege —
  la voix 3, a droite — reprend le crochet une octave plus bas. Question a
  gauche, reponse a droite ;
- un **rythme harmonique** qui varie : sept mesures changent d'accord au milieu,
  et les mesures 15 a 18 n'en changent presque plus du tout — le ciel s'ouvre,
  l'harmonie s'arrete ;
- la **surprise**, et c'est la plus grosse que puisse subir une piece batie sur
  un bourdon : **la pedale se deplace**. Mesures 15 a 18, le fa diese descend au
  **mi** — la falaise s'ouvre sous les pieds — puis remonte mesure 19. Les
  accords de ces quatre mesures (la, la, re, la) sont choisis pour que le mi n'y
  soit **jamais** la fondamentale : le procede de la zone tient, meme deplace ;
- une **cadence** : mesure 20, un **fa diese majeur** avec son la diese, la seule
  sensible du morceau. C'est aussi le seul instant ou le bourdon est la
  fondamentale de l'accord — la dominante, et elle seule, a le droit de poser
  le pied ;
- un **arc de densite** : intro en blanches d'arpege, A en croches, B qui s'ouvre
  en rondes sur la pedale deplacee, A' a l'octave superieure ;
- une **fin qui prepare la boucle** : la derniere mesure retombe de si a fa
  diese, la quinte par laquelle la piece va repartir.

24 mesures a 4/4, 40,0 s. Forme intro(4) - A(8) - B(8) - A'(4).

    python3 falaise.py && python3 ../../../midi_to_mb.py falaise.mid \\
        CLIFF.MB.BIN --bpm 144 --max 2304 --wav FALAISE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 144, 4, 24
LEN = BAR * BARS

# une entree par mesure ; « A|E » change d'accord au milieu de la mesure
CHORDS = (["Bm", "Bm", "A", "A"]
          + ["Bm", "F#m", "D", "A|E", "Bm", "E", "A|F#m", "Bm"]
          + ["D", "A|E", "A", "A", "D", "A", "D|E", "F#"]
          + ["Bm", "D|A", "E|F#", "Bm"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "B4:4",                           "B4:2 F#5:2",
    "A4:2 C#5:2",                     "E5:4",
    "B4:1 F#5:1 A5:1.5 B5:.5",        "F#5:2 C#5:2",            # le crochet
    "D5:1 F#5:1 A5:2",                "B5:4",                   # 8 : la reponse
    "E5:1 B5:1 D6:1.5 C#6:.5",        "B5:2 F#5:2",             # le crochet, ouvert
    "A5:4",                           "C#6:1 B5:1 F#5:2",       # 11 : la reponse
    "D6:2 F#6:2",                     "E6:1 C#6:1 A5:2",        # B : le registre monte
    "C#6:4",                          "E6:2 A5:2",              # 15 : la reponse, la pedale bouge
    "F#6:2 D6:2",                     "E6:1 C#6:1 A5:2",
    "B5:1 D6:1 F#6:2",                "A#5:1 C#6:1 F#6:2",      # 20 : la cadence
    "B5:1 F#6:1 A6:1.5 B6:.5",        "F#6:2 D6:2",             # le crochet a l'octave
    "E6:1 C#6:1 A5:2",                "B5:3 F#5:1",             # 24 : la quinte de la boucle
]
assert len(MEL) == BARS

CTR = [
    "B3:2 D4:2",                      "F#4:2 B3:2",
    "A3:2 C#4:2",                     "E4:2 A3:2",
    "B3:2 D4:2",                      "C#4:2 A3:2",
    "D4:2 F#4:2",                     "E4:2 B3:2",
    "F#4:2 D4:2",                     "G#3:2 B3:2",
    "A3:2 C#4:2",                     "D4:2 B3:2",
    "F#4:2 A3:2",                     "E4:2 G#3:2",
    "A3:2 C#4:2",                     "E4:2 A3:2",
    "D4:2 F#4:2",                     "C#4:2 E4:2",
    "A3:2 B3:2",                      "A#3:2 C#4:2",
    "B3:2 F#4:2",                     "D4:2 C#4:2",
    "B3:2 A#3:2",                     "D4:2 B3:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant, une octave sous lui, en citant le crochet
REPONSES = {
    7:  "F#4:1 B4:1 D5:1.5 C#5:.5",
    10: "C#5:1 B4:1 A4:1 F#4:1",
    14: "A4:1 C#5:1 E5:1.5 D5:.5",
}


def accompagnement():
    """L'arpege a quatre sons — la figure qui s'ouvre — sauf quand il repond."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in REPONSES:
            out += line(REPONSES[i], t)
        elif i < 4:                    # l'intro : deux sons par demi-mesure
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 1.0, (0, 3), lo=54)
        else:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.5,
                            (0, 1, 2, 3), lo=54)
    return out


def lit():
    """Les accords tenus : une note par accord, deux si la mesure en change."""
    out = []
    for i, b in enumerate(CHORDS):
        cs = b.split("|")
        out += bed(cs, i * BAR, BAR / len(cs), lo=50, which=1)
    return out


def basse():
    """Deux blanches ouvertes : rien ne marche, on est en haut. Quatre pas de
    noire quand l'accord change au milieu de la mesure."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR, [(0, 2), (-1, 2)], lo=48)
    return out


def bourdon():
    """La quinte, immobile — sauf mesures 15 a 18, ou elle descend au mi."""
    return (pedal(midi("F#2"), 0, BAR * 14, retrig=BAR * 4)
            + pedal(midi("E2"), BAR * 14, BAR * 4, retrig=BAR * 4)
            + pedal(midi("F#2"), BAR * 18, BAR * 6, retrig=BAR * 3))


def build():
    p = Piece("B", "dorien", BPM, BAR, "Le Ciel s'Ouvre")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", lit())
    p.add("basse", basse())
    p.add("bourdon", bourdon())
    return p                          # pas de batterie : voir l'en-tete


if __name__ == "__main__":
    build().write(Path(__file__).with_name("falaise.mid"))
