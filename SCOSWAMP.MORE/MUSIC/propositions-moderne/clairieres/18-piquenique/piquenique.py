#!/usr/bin/env python3
"""« Le Repas du Voleur » — clairiere 18, le pique-nique suspect. Fa dorien, 176.

Variation dans la couleur `sud` : **bourdon de tonique immobile**, marche modale
large — mais a **3/4**, la seule des trente-cinq clairieres a ne pas etre a
quatre temps. Le petit homme joyeux de la page 066 mange son fromage adosse a un
chene ; il faut une valse.

La gaite est fausse, et le mode le dit : fa dorien a un **si bemol majeur** au
quatrieme degre — c'est la couleur riante de la piece — mais un **sol bemol
majeur** vient s'y planter, le second degre abaisse, qui n'appartient pas au
mode. C'est le demi-ton phrygien de la zone `danger`, cite ici a decouvert :
l'Anneau de Cuivre chauffe, et l'on comprend qu'il s'agit d'un VOLEUR.

Ce que la revision ajoute :

- un **crochet** de deux mesures, la premiere phrase de la valse : fa - la bemol
  - do | si bemol tenu, la bemol. Enonce mesure 5, repris mesure 11 sur si
  bemol, redit tel quel mesure 29, et sa tete revient encore mesure 39, juste
  avant la boucle. Quatre fois ;
- une **reponse** : mesures 8, 20 et 32, le chant tient une blanche pointee et
  l'arpege — la voix 3, a droite — repond `fa la bemol do`, le crochet une
  octave plus bas. C'est le petit homme qui reprend la chanson la bouche pleine ;
- un **rythme harmonique** varie : treize mesures changent d'accord au
  **troisieme temps** — deux temps pour le premier accord, un pour le second —
  ce qui donne a la valse le boitement qu'on entend dans les vraies ;
- la **surprise**, et c'est une **hemiole** : mesures 25-26, la valse trebuche.
  Le chant, l'arpege, la basse et la batterie passent tous en groupes de **deux**
  temps sur six — trois pas au lieu de deux mesures — et c'est exactement la ou
  le **sol bemol** arrive. Deux mesures a 3/4 qui sonnent comme trois a 2/4 : la
  seule mesure impaire du dossier, obtenue sans changer de chiffrage ;
- une **cadence** : mesure 28, un **do majeur** avec son mi naturel, etranger au
  mode ; elle revient mesure 38. C'est la seule sensible du morceau, et elle
  arrive deux fois, aux deux jointures qui comptent ;
- un **arc de densite** : intro a deux sons par mesure et sans batterie, A la
  valse, B qui se serre a la caisse claire, l'hemiole, A' pleine avec le
  charleston double ;
- une **fin qui prepare la boucle** : la derniere mesure retombe sur le do du
  debut, et la valse repart.

**La batterie** est celle d'une valse — grosse caisse au premier temps,
charleston aux deux autres — jusqu'a l'hemiole, ou elle frappe sur les temps 1,
3 et 5 et fait trebucher tout le monde avec elle. Elle prend la voix 5 a
droite ; il ne reste que cinq parties de hauteur, et c'est la voix d'accords
tenus qui a cede la place — le bourdon de tonique est le procede de la zone.

40 mesures a 3/4, 40,9 s. Forme intro(4) - A(12) le repas - B(12) l'Anneau
chauffe - A'(12) la reprise empoisonnee.

    python3 piquenique.py && python3 ../../../midi_to_mb.py piquenique.mid \\
        PICNIC.MB.BIN --bpm 176 --max 2304 --wav PIQUENIQUE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 176, 3, 40
LEN = BAR * BARS
HEMIOLE = (24, 25)                         # les deux mesures qui trebuchent

# une entree par mesure ; « Bb|Fm » change d'accord au TROISIEME temps
CHORDS = (["Fm", "Fm", "Bb", "Bb"]
          + ["Fm", "Ab", "Bb|Fm", "Fm", "Cm", "Eb|Bb", "Bb", "Fm",
             "Db", "Eb|Bb", "Cm|C", "Fm"]
          + ["Bb", "Fm", "Eb|Cm", "Cm", "Db", "Bb|Ab", "Ab", "Eb",
             "Gb", "Gb", "Db", "C"]
          + ["Fm", "Ab|Bb", "Bb|Fm", "Fm", "Cm", "Eb|Bb", "Db", "Bb|Ab",
             "Gb", "Cm|C", "Fm", "Fm"])
assert len(CHORDS) == BARS

MEL = [
    "C5:3",                 "C5:1 F5:2",            "D5:1 F5:2",
    "Bb4:1 D5:2",
    "F5:1 Ab5:1 C6:1",      "Bb5:2 Ab5:1",          "D6:1 Bb5:1 F5:1",   # le crochet
    "Ab5:3",                "G5:1 C6:1 Eb6:1",      "D6:2 Bb5:1",        # 8 : la reponse
    "F5:1 Bb5:1 D6:1",      "C6:2 Ab5:1",           "F5:1 Ab5:1 Db6:1",  # le crochet sur si bemol
    "C6:2 G5:1",            "Eb5:1 G5:1 C6:1",      "F5:3",
    "D6:1 F6:1 D6:1",       "C6:2 Ab5:1",           "Bb5:1 G5:1 Eb5:1",
    "G5:3",                 "Ab5:1 F5:1 Db5:1",     "D5:1 F5:1 Bb5:1",   # 20 : la reponse
    "C6:2 Ab5:1",           "Bb5:1 G5:1 Eb5:1",
    "Gb5:2 Bb5:2 Db6:2",    "",                                          # 25-26 : l'hemiole
    "Db6:1 Ab5:1 F5:1",     "E5:1 G5:1 C6:1",                            # 28 : la cadence
    "F5:1 Ab5:1 C6:1",      "Bb5:2 Ab5:1",          "D6:1 Bb5:1 F5:1",   # le crochet, redit
    "C6:3",                 "G5:1 C6:1 Eb6:1",      "D6:2 Bb5:1",        # 32 : la reponse
    "F5:1 Ab5:1 Db6:1",     "C6:2 Ab5:1",           "Gb5:1 Db6:1 Bb5:1", # 37 : le poison, garde
    "C6:1 G5:1 E5:1",       "F5:1 Ab5:1 C6:1",      "F5:2 C5:1",         # 40 : le do de la boucle
]
assert len(MEL) == BARS

CTR = [
    "Ab3:2 C4:1",           "F4:2 C4:1",            "Bb3:2 D4:1",
    "F4:2 Bb3:1",
    "C4:2 Ab3:1",           "Eb4:2 C4:1",           "D4:2 C4:1",
    "C4:2 Ab3:1",           "Eb4:2 G3:1",           "Bb3:2 D4:1",
    "D4:2 F4:1",            "Ab3:2 C4:1",           "F4:2 Db4:1",
    "G3:2 F4:1",            "Eb4:2 E4:1",           "Ab3:2 C4:1",
    "D4:2 F4:1",            "C4:2 Ab3:1",           "Bb3:2 Eb4:1",
    "G3:2 C4:1",            "Db4:2 Ab3:1",          "D4:2 C4:1",
    "C4:2 Eb4:1",           "Bb3:2 G3:1",
    "Db4:2 Bb3:2 Gb4:2",    "",
    "Ab3:2 F4:1",           "E4:2 G3:1",
    "C4:2 Ab3:1",           "Eb4:2 D4:1",           "F4:2 C4:1",
    "Ab3:2 C4:1",           "Eb4:2 G3:1",           "Bb3:2 F4:1",
    "F4:2 Ab3:1",           "D4:2 Eb4:1",           "Bb3:2 Db4:1",
    "Eb4:2 E4:1",           "C4:2 Ab3:1",           "Ab3:2 C4:1",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le crochet, une octave plus bas
REPONSES = {
    7:  "F4:1 Ab4:1 C5:1",
    19: "G4:1 C5:1 Eb5:1",
    31: "F4:1 Ab4:1 C5:1",
}


def accompagnement():
    """Un son d'accord par temps — la valse — sauf quand l'arpege repond, et
    sauf a l'hemiole, ou il passe en blanches."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in HEMIOLE or i in REPONSES:
            continue
        if "|" in CHORDS[i]:
            a, b = CHORDS[i].split("|")
            out += arpeggio([a], t, 2.0, 1.0, (0, 1), lo=54)
            out += arpeggio([b], t + 2, 1.0, 1.0, (2,), lo=54)
        elif i < 4:                    # l'intro : deux sons par mesure
            out += arpeggio([CHORDS[i]], t, BAR, 1.5, (0, 2), lo=54)
        else:
            out += arpeggio([CHORDS[i]], t, BAR, 1.0, (0, 1, 2), lo=54)
    for i, spec in REPONSES.items():
        out += line(spec, i * BAR)
    out += arpeggio(["Gb"], BAR * 24, 6.0, 2.0, (0, 1, 2), lo=54)
    return sorted(out, key=lambda e: e[1])


def basse():
    """Une fondamentale de blanche, une quinte de noire — le pas de la valse.
    Quand l'accord change au troisieme temps, la quinte lui appartient."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if i in HEMIOLE:
            continue
        if "|" in b:
            a, c = b.split("|")
            out += progression([a], t, 2.0, [(0, 2)], lo=48)
            out += progression([c], t + 2, 1.0, [(-1, 1)], lo=48)
        else:
            out += progression([b], t, BAR, [(0, 2), (-1, 1)], lo=48)
    out += progression(["Gb"], BAR * 24, 6.0, [(0, 2), (-1, 2), (0, 2)], lo=48)
    return sorted(out, key=lambda e: e[1])


def build():
    p = Piece("F", "dorien", BPM, BAR, "Le Repas du Voleur")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", pedal(midi("F2"), 0, LEN, retrig=BAR * 8))

    # la valse : caisse au premier temps, charleston aux deux autres
    p.add_drums("K.H.H.", t0=BAR * 4, length=BAR * 12)
    p.add_drums("K.H.S.", t0=BAR * 16, length=BAR * 8)
    # l'hemiole : trois frappes sur six temps, et la valse trebuche
    p.add_drums([(0, "K"), (2, "S"), (4, "K")], t0=BAR * 24)
    p.add_drums("K.H.S.", t0=BAR * 26, length=BAR * 2)
    p.add_drums([(2, "T"), (2.5, "S")], t0=BAR * 27)
    p.add_drums("K.HSH.", t0=BAR * 28, length=BAR * 12)
    p.add_drums([(0, "C", 7)], t0=BAR * 28)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("piquenique.mid"))
