#!/usr/bin/env python3
"""« L'Herbe qui Serre » — clairiere 25, l'Herbe a Pinces. Mi phrygien, 176.

Pages 388, 263, 033, 187. « Elle pousse si vite qu'on peut la voir bouger. Et
tandis que vous l'observez, des pinces apparaissent aux extremites de ses
tiges. » Le procede de la zone `danger` est intact — demi-ton phrygien **fa-mi**
et bourdon de mi — mais la piece a maintenant une **batterie** : la caisse claire
tombe exactement dans le trou de l'arpege, la ou la pince se referme.

Ce que la revision ajoute :

* **le crochet** — `mi fa mi | si`, la seconde mineure qui mord puis saute a la
  quinte — est enonce quatre fois (mesures 5, 10, 21, 27) et nulle part ailleurs ;
* **une vraie partie B** : le registre monte d'une octave et l'harmonie quitte le
  mi pour tourner autour de la mineur et do ;
* **la reponse** : quatre fois (mesures 8, 12, 16, 28) le chant tient une ronde
  et c'est l'arpege, a droite, qui repond a sa place avec le rythme du crochet ;
* **le rythme harmonique varie** : une mesure sur trois porte deux accords, la
  grille n'est plus un accord par mesure d'un bout a l'autre ;
* **la surprise** : mesures 19-20, la pedale quitte le mi et se pose un demi-ton
  plus haut, sur **fa** — le demi-ton phrygien passe enfin dans la basse, la
  batterie se tait, puis tout retombe sur mi a la mesure 21 ;
* **l'arc** : intro a deux notes par mesure, coda qui se vide ; la densite monte
  et redescend au lieu d'etre plate.

La batterie ne joue pas partout : rien dans l'intro, deux coups par mesure en A,
la grosse caisse en B, la pince complete en A', et plus rien a la derniere mesure
pour que la boucle reparte a nu.

32 mesures a 4/4, 43,6 s. Forme intro(4) - A(8) - B(8) - A' a l'octave(8) - coda(4).

    python3 pinces.py && python3 ../../../midi_to_mb.py pinces.mid \\
        PINCERS.MB.BIN --bpm 176 --max 2304 --wav PINCES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 176, 4, 32
LEN = BAR * BARS

# La grille se lit au demi-temps de mesure : un accord seul tient la mesure,
# deux accords la coupent en deux. C'est la que se joue le rythme harmonique.
GRILLE = [
    ("Em",), ("Em",), ("F",), ("Em",),                          # intro
    ("Em",), ("Em", "F"), ("Em",), ("Am",),                     # A
    ("F",), ("Em", "F"), ("Dm", "C"), ("Em",),
    ("Am", "C"), ("F",), ("C", "G"), ("Am",),                   # B
    ("Dm", "F"), ("C",), ("F",), ("F", "Em"),
    ("Em",), ("Em", "F"), ("Em",), ("Dm", "C"),                 # A'
    ("F", "G"), ("Am", "F"), ("Em", "F"), ("Em",),
    ("Am",), ("F",), ("F", "Em"), ("Em",),                      # coda
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]                  # deux par mesure

HOOK = "E5:.5 F5:.5 E5:1 B5:2"          # le crochet : fa-mi, puis la quinte
HOOK8 = "E6:.5 F6:.5 E6:1 B5:2"

MEL = [
    "B5:4",                           "B5:2 C6:2",              # intro
    "A5:4",                           "G5:2 F5:2",
    HOOK,                             "C6:.5 B5:.5 A5:1 G5:2",  # A
    "E5:.5 F5:.5 G5:1 B5:2",          "A5:4",
    "C6:1 A5:1 F5:2",                 HOOK,
    "A5:1 F5:1 E5:2",                 "E5:4",
    "A5:1 C6:1 E6:2",                 "F6:.5 E6:.5 C6:1 A5:2",  # B
    "G5:1 C6:1 E6:2",                 "C6:4",
    "D6:1 A5:1 F6:2",                 "E6:1 C6:1 G5:2",
    "F6:.5 E6:.5 C6:1 A5:2",          "E6:4",
    HOOK8,                            "C6:.5 B5:.5 A5:1 F6:2",  # A'
    "E6:.5 F6:.5 G6:1 B5:2",          "A5:1 F5:1 D6:2",
    "C6:1 A5:1 F6:2",                 "G6:1 E6:1 C6:2",
    HOOK8,                            "E6:4",
    "A5:1 C6:1 E6:2",                 "F6:.5 E6:.5 C6:1 A5:2",  # coda
    "F5:2 E5:2",                      "E5:4",
]
assert len(MEL) == BARS

CTR = [
    "E4:4",                           "B3:4",                   # intro
    "A3:4",                           "B3:4",
    "B3:2 E4:2",                      "G3:2 A3:2",              # A
    "B3:2 G3:2",                      "A3:2 C4:2",
    "A3:2 F4:2",                      "B3:2 G3:2",
    "A3:2 E4:2",                      "B3:2 E4:2",
    "C4:2 A3:2",                      "A3:2 F4:2",              # B
    "G3:2 B3:2",                      "A3:2 C4:2",
    "D4:2 A3:2",                      "E4:2 C4:2",
    "A3:2 F4:2",                      "C4:2 B3:2",
    "B3:2 E4:2",                      "G3:1 A3:1 B3:2",         # A'
    "B3:2 G3:2",                      "A3:1 F4:1 E4:2",
    "A3:2 B3:2",                      "C4:1 A3:1 F4:2",
    "B3:2 G3:2",                      "E4:2 B3:2",
    "A3:4",                           "A3:4",                   # coda
    "A3:2 G3:2",                      "E4:4",
]
assert len(CTR) == BARS

# Les reponses de l'arpege, la ou le chant tient une ronde. Meme rythme que le
# crochet, deux octaves plus bas : la clairiere repond au voyageur.
REPONSES = {
    7:  "E4:.5 F4:.5 E4:1 A4:1 C5:1",
    11: "E4:.5 F4:.5 E4:1 B4:2",
    15: "A4:.5 B4:.5 C5:1 A4:2",
    27: "E4:.5 F4:.5 E4:1 B4:1 E5:1",
}
MUET = sorted(REPONSES)                 # mesures ou l'ostinato cede la place


def arp(b0, b1, step, shape, lo=57):
    """L'arpege des mesures b0..b1-1, en sautant celles qui portent une reponse."""
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        out += arpeggio(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=47):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("E", "phrygien", BPM, BAR, "L'Herbe qui Serre")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # la pince : trois croches et un trou, huit fois par mesure. Clairseme a
    # l'intro (noires), plein des la mesure 5, vide a la derniere mesure.
    a = arp(0, 4, 1.0, (0, 2))
    a += arp(4, 31, 0.5, (0, 2, 1, None))
    a += arp(31, 32, 2.0, (0,))
    for b in MUET:
        a += line(REPONSES[b], BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    # la basse suit l'arc : ronde, blanche, noire, noire pointee
    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 28, [(0, 1), (0, 0.5), (-1, 0.5)])
    b += bas(28, 32, [(0, 2)])
    p.add("basse", b)

    # le bourdon quitte la voix 5 (prise par la batterie) et migre a gauche ;
    # mesures 19-20 il se deplace d'un demi-ton, sur fa : la surprise.
    d = pedal(midi("E2"), 0, BAR * 18)
    d += pedal(midi("F2"), BAR * 18, BAR * 2)
    d += pedal(midi("E2"), BAR * 20, BAR * 12)
    p.add("bourdon", d)

    # La batterie : la caisse claire tombe dans le trou de l'arpege (croches 4
    # et 8), la ou la pince se referme. Rien avant la mesure 5, rien pendant le
    # deplacement de pedale, rien a la derniere mesure.
    p.add_drums("...S...S", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K..S...S", t0=BAR * 12, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K..S.K.S", t0=BAR * 20, length=BAR * 8)
    p.add_drums("K..S...S", t0=BAR * 28, length=BAR * 2)
    p.add_drums([(0, "K"), (2, "S")], t0=BAR * 30)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("pinces.mid"))
