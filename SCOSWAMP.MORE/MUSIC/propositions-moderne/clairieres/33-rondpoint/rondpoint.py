#!/usr/bin/env python3
"""« Le Coeur du Marais » — clairiere 33, le large rond-point. Re eolien, 158.

C'est la premiere clairiere du Marais : le joueur y arrive page 195, le sol est
instable, trois sentiers partent de la et le brouillard monte. La piece est donc
le theme du Marais lui-meme. Elle prend la tonalite exacte de la zone `sud` — re
eolien, la seule des trente-cinq a le faire — et son procede : la marche
i-VI-III-VII (Dm-Bb-F-C) posee sur un bourdon de re qui ne bouge **jamais**,
d'un bout a l'autre, pas meme sous l'accord majeur de la fin.

Son theme est a elle : la **montee de trois notes** `re · mi · fa`, celle qui
redemande son chemin.

Ce que la revision ajoute :

* **la montee est desormais le crochet de toute la piece**, plus seulement de la
  partie B. Elle ouvre A (mesure 5), la relance (mesure 9), monte sur sol puis
  sur si bemol dans le B (mesures 14 et 18 — les trois sentiers), revient a
  l'octave en A' (mesure 21), et c'est elle que l'arpege renvoie en reponse
  (mesures 8, 12, 16). Sept enonces, jamais deux fois au meme degre ;
* **la reponse** : trois fois, le chant tient une ronde et le sentier d'en face
  lui rend la montee, a droite. C'est la seule des onze ou la reponse est
  litteralement le theme ;
* **une vraie partie B** (mesures 13-20) : le registre monte d'une octave et
  l'harmonie s'installe sur si bemol et fa avant de redescendre par la mineur ;
* **le rythme harmonique varie** : un accord tenu quatre mesures a l'intro, deux
  accords par mesure des la mesure 6, et de nouveau un seul dans la coda ;
* **la surprise** : mesure 31, **re majeur**. Un fa diese, un seul, le seul de
  toute la piece — la trouee de ciel au-dessus du rond-point. La mesure suivante
  le reprend : le Marais se referme et la boucle repart en mineur ;
* **la batterie est le pas du voyageur** : rien pendant six mesures, puis la
  grosse caisse au premier temps et la caisse claire au troisieme — une marche
  regulière, jamais une danse. Elle s'epaissit en B et en A', et la **derniere
  mesure ne contient plus que deux pas**, seuls, pour que la boucle reparte sur
  eux ;
* **l'arc** : deux notes d'arpege par mesure a l'intro, huit en B et en A', deux
  de nouveau a la derniere mesure. La piece s'ouvre et se referme sur le meme
  vide.

32 mesures a 4/4, 48,6 s. Forme intro(4) - A(8) - B(8) - A' a l'octave(8) - coda(4).

    python3 rondpoint.py && python3 ../../../midi_to_mb.py rondpoint.mid \\
        ROUNDABOUT.MB.BIN --bpm 158 --max 2304 --wav RONDPOINT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 158, 4, 32
LEN = BAR * BARS

GRILLE = [
    ("Dm",), ("Dm",), ("Gm",), ("Am",),                          # intro
    ("Dm",), ("F", "C"), ("Bb", "Gm"), ("Dm",),                  # A
    ("Dm",), ("Bb", "F"), ("C", "Am"), ("Dm",),
    ("Bb", "F"), ("Gm", "Dm"), ("Bb", "C"), ("Am",),             # B
    ("F", "C"), ("Dm", "Bb"), ("Gm", "C"), ("Am",),
    ("Dm",), ("F", "C"), ("Bb", "Gm"), ("Dm",),                  # A'
    ("Bb", "F"), ("Gm", "C"), ("F", "C"), ("Dm",),
    ("Bb",), ("Gm", "C"), ("D",), ("Dm",),                       # coda
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

MONTEE = "D5:1 E5:1 F5:2"               # le theme du Marais : trois notes
MONTEEG = "G5:1 A5:1 Bb5:2"             # le deuxieme sentier
MONTEEB = "Bb5:1 C6:1 D6:2"             # le troisieme
MONTEE8 = "D6:1 E6:1 F6:2"              # a l'octave

MEL = [
    "A5:4",                           "A5:2 D6:2",               # intro
    "Bb5:4",                          "G5:2 A5:2",
    MONTEE,                           "A5:1 C6:1 A5:2",          # A
    "Bb5:1 D6:1 G5:2",                "A5:4",
    MONTEE,                           "Bb5:1 D6:1 F6:2",
    "E6:1 C6:1 A5:2",                 "D6:4",
    "F6:1 D6:1 Bb5:2",                MONTEEG,                   # B
    "D6:1 F6:1 C6:2",                 "A5:4",
    "C6:1 A5:1 F6:2",                 MONTEEB,
    "G6:1 E6:1 C6:2",                 "A5:2 E6:2",
    MONTEE8,                          "A6:1 F6:1 C6:2",          # A'
    "D6:1 Bb5:1 G6:2",                "F6:1 D6:1 A5:2",
    "Bb5:1 D6:1 F6:2",                "G6:1 E6:1 C6:2",
    "A6:1 F6:1 C6:2",                 "D6:2 A5:2",
    "Bb5:1 D6:1 F6:2",                "G5:1 Bb5:1 C6:2",         # coda
    "F#6:2 A6:2",                     "D6:2 D5:2",
]
assert len(MEL) == BARS

CTR = [
    "D4:4",                           "A3:4",                    # intro
    "Bb3:4",                          "C4:4",
    "A3:2 D4:2",                      "C4:2 A3:2",               # A
    "D4:2 Bb3:2",                     "F4:2 D4:2",
    "A3:2 D4:2",                      "Bb3:2 F4:2",
    "C4:2 A3:2",                      "D4:2 A3:2",
    "D4:2 A3:2",                      "Bb3:2 D4:2",              # B
    "F4:2 C4:2",                      "E4:2 C4:2",
    "A3:2 C4:2",                      "D4:2 F4:2",
    "Bb3:2 E4:2",                     "C4:2 A3:2",
    "A3:2 D4:2",                      "C4:2 A3:2",               # A'
    "D4:2 Bb3:2",                     "F4:2 D4:2",
    "Bb3:2 F4:2",                     "Bb3:2 E4:2",
    "C4:2 A3:2",                      "D4:2 A3:2",
    "D4:2 Bb3:2",                     "Bb3:2 E4:2",              # coda
    "F#4:2 A3:2",                     "D4:2 A3:2",
]
assert len(CTR) == BARS

# La reponse est le theme lui-meme : le sentier d'en face redemande son chemin.
REPONSES = {
    7:  "D4:1 E4:1 F4:2",
    11: "A4:1 Bb4:1 C5:2",
    15: "F4:1 G4:1 A4:2",
}


def arp(b0, b1, step, shape, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        out += arpeggio(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=45):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("D", "eolien", BPM, BAR, "Le Coeur du Marais")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = arp(0, 4, 2.0, (0,))
    a += arp(4, 12, 1.0, (0, 2))
    a += arp(12, 30, 0.5, (0, 2, 1, 2))
    a += arp(30, 31, 1.0, (0, 2))
    a += arp(31, 32, 2.0, (0,))
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 28, [(0, 1), (0, 0.5), (-1, 0.5)])
    b += bas(28, 30, [(0, 1), (-1, 1)])
    b += bas(30, 32, [(0, 2)])
    p.add("basse", b)

    # Le bourdon de re ne bouge jamais : c'est le procede de `sud` et le sol du
    # Marais. Il migre seulement de la voix 5 a la voix 2, la batterie prenant
    # sa place a droite.
    p.add("bourdon", pedal(midi("D2"), 0, LEN))

    # Le pas du voyageur. Rien pendant six mesures : on ecoute d'abord. Puis la
    # marche, qui s'epaissit sans jamais devenir une danse — et la derniere
    # mesure ne garde que deux pas, pour que la boucle reparte sur eux.
    p.add_drums("K...S...", t0=BAR * 6, length=BAR * 6)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K..HS..H", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K.HHS.KH", t0=BAR * 20, length=BAR * 8)
    p.add_drums("K...S...", t0=BAR * 28, length=BAR * 2)
    p.add_drums([(0, "C", 7)], t0=BAR * 30)
    p.add_drums([(0, "K"), (2, "K")], t0=BAR * 31)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("rondpoint.mid"))
