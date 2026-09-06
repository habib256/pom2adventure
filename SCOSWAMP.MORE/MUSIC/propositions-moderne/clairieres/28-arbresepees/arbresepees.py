#!/usr/bin/env python3
"""« Les Bras qui Repoussent » — clairiere 28, les Arbres-Epees. Fa phrygien, 166.

Pages 157, 279, 022. « Chaque bras tient une epee a son extremite. » Et si l'on
revient : « les branches des terribles Arbres-Epees ont deja repousse. »

Le procede de la zone `danger` est intact : demi-ton phrygien **sol bemol-fa**,
bourdon de fa immobile. Le procede propre a la clairiere aussi : le **canon**
court. La cellule `fa - sol bemol - fa` que le chant lance repousse au
contre-chant, une octave plus bas, la mesure suivante — mesures 6, 19 et 23 —
et une derniere fois dans la mesure amputee.

Ce que la revision ajoute :

* **le crochet est la cellule elle-meme** : trois notes, deux secondes mineures.
  Enoncee par le chant aux mesures 5, 22 (a l'octave) et dans la mesure courte
  21 ; par le contre-chant aux mesures 6, 19, 21 et 23. Rien d'autre dans la
  piece ne ressemble a ca ;
* **une vraie partie B** (mesures 13-20) : re bemol et la bemol, les deux seuls
  accords majeurs, et le chant monte au si bemol 6 — la seule clarte du morceau ;
* **la reponse** : mesures 8, 12 et 16, le chant tient une ronde et c'est
  l'arpege, a droite, qui repousse la cellule a sa place ;
* **le rythme harmonique varie** : les mesures a deux accords doublent la vitesse
  de la marche harmonique, et l'intro tient un seul accord sur quatre mesures ;
* **la surprise** : la **mesure 21 n'a que trois temps**. La lame coupe un temps
  a la piece — c'est la seule mesure impaire des trente-cinq clairieres avec le
  6/4 de la Bete, et elle tombe juste avant la reprise ;
* **l'arc** : l'intro n'a que deux notes d'arpege par mesure et pas de batterie ;
  A' en a huit et la caisse claire sur chaque temps faible.

La batterie, ce sont les lames : la caisse claire seche sur les temps faibles,
la grosse caisse sur le premier, et trois coups nus dans la mesure amputee.

28 mesures a 4/4 moins un temps, 40,3 s. Forme intro(4) - A(8) - B(8) -
mesure courte(1) - A'(7).

    python3 arbresepees.py && python3 ../../../midi_to_mb.py arbresepees.mid \\
        SWORDTREES.MB.BIN --bpm 166 --max 2304 --wav ARBRESEPEES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 166, 4, 28
COURTE = 20                             # la mesure amputee : trois temps
BEATS = [3 if i == COURTE else 4 for i in range(BARS)]
T = [sum(BEATS[:i]) for i in range(BARS + 1)]
LEN = T[-1]

GRILLE = [
    ("Fm",), ("Fm",), ("Gb",), ("Fm",),                          # intro
    ("Fm",), ("Ab", "Gb"), ("Bbm",), ("Fm",),                    # A
    ("Db", "Ab"), ("Ebm",), ("Bbm", "Gb"), ("Fm",),
    ("Db",), ("Ab",), ("Ebm", "Bbm"), ("Db",),                   # B
    ("Gb", "Db"), ("Ab", "Ebm"), ("Bbm",), ("Fm",),
    ("Fm",),                                                     # mesure courte
    ("Fm",), ("Ab", "Gb"), ("Bbm",), ("Db", "Ab"),               # A'
    ("Ebm", "Bbm"), ("Gb", "Db"), ("Fm",),
]
assert len(GRILLE) == BARS

CELL = "F5:1 Gb5:1 F5:2"                # le crochet : la cellule qui repousse
CELL8 = "F6:1 Gb6:1 F6:2"
ECHO = "F4:1 Gb4:1 F4:2"                # la meme, une octave plus bas

MEL = [
    "C6:4",                           "C6:2 F6:2",               # intro
    "Db6:4",                          "Bb5:2 C6:2",
    CELL,                             "Ab5:1 C6:1 Gb6:2",        # A
    "Bb5:1 F6:1 Db6:2",               "C6:4",
    "Db6:1 Ab5:1 F6:2",               "Eb6:1 Bb5:1 Gb6:2",
    "F6:1 Db6:1 Bb5:2",               "F6:4",
    "Db6:1 F6:1 Ab6:2",               "C6:1 Ab5:1 Eb6:2",        # B
    "Gb6:1 Eb6:1 Bb5:2",              "F6:4",
    "Gb6:1 Db6:1 Bb5:2",              "Ab6:1 Eb6:1 C6:2",
    "Bb6:1 F6:1 Db6:2",               "C6:2 Ab5:2",
    "F5:1 Gb5:1 F5:1",                                           # mesure courte
    CELL8,                            "Ab6:1 C6:1 Gb6:2",        # A'
    "Bb5:1 F6:1 Db6:2",               "Db6:1 Ab6:1 F6:2",
    "Eb6:1 Bb5:1 Gb6:2",              "Gb6:1 F6:1 Db6:2",
    "C6:2 F6:2",
]
assert len(MEL) == BARS

CTR = [
    "C4:4",                           "Ab3:4",                   # intro
    "Db4:4",                          "Ab3:4",
    "C4:2 F4:2",                      ECHO,                      # A : premiere repousse
    "Bb3:2 Db4:2",                    "C4:2 Ab3:2",
    "Db4:2 Ab3:2",                    "Gb3:2 Bb3:2",
    "F4:2 Db4:2",                     "C4:2 F4:2",
    "Ab3:2 Db4:2",                    "C4:2 Ab3:2",              # B
    "Gb4:2 Bb3:2",                    "F4:2 Db4:2",
    "Db4:2 Gb3:2",                    "C4:2 Eb4:2",
    ECHO,                             "C4:2 Ab3:2",              # deuxieme repousse
    "F4:1 Gb4:1 F4:1",                                           # mesure courte
    "C4:2 F4:2",                      ECHO,                      # troisieme repousse
    "Bb3:2 Db4:2",                    "Ab3:2 F4:2",
    "Gb4:2 Bb3:2",                    "Db4:2 Ab3:2",
    "C4:2 F4:2",
]
assert len(CTR) == BARS

REPONSES = {                            # la cellule repousse a l'arpege
    7:  "F4:1 Gb4:1 F4:1 C5:1",
    11: "C5:1 Db5:1 C5:2",
    15: "F4:1 Gb4:1 Ab4:1 C5:1",
}


def arp(b0, b1, pattern, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES or b == COURTE:
            continue
        ch = (GRILLE[b] * 2)[:2]
        out += progression(list(ch), T[b], BEATS[b] / 2, pattern, lo)
    return out


def bas(b0, b1, pattern, lo=46):
    out = []
    for b in range(b0, b1):
        if b == COURTE:
            continue
        ch = (GRILLE[b] * 2)[:2]
        out += progression(list(ch), T[b], BEATS[b] / 2, pattern, lo)
    return out


def build():
    p = Piece("F", "phrygien", BPM, BAR, "Les Bras qui Repoussent")

    mel = []
    for i, s in enumerate(MEL):
        mel += line(s, T[i])
    p.add("melodie", mel)

    a = arp(0, 4, [(0, 1), (2, 1)])
    a += arp(4, 12, [(0, 0.5), (2, 0.5), (1, 0.5), (2, 0.5)])
    a += arp(12, 20, [(0, 0.5), (2, 0.5), (1, 0.5), (0, 0.5)])
    a += arp(21, 28, [(0, 0.5), (2, 0.5), (1, 0.5), (2, 0.5)])
    for b, spec in REPONSES.items():
        a += line(spec, T[b])
    a += line("F4:.5 Gb4:.5 F4:1 C5:1", T[COURTE])
    p.add("arpege", a)

    ctr = []
    for i, s in enumerate(CTR):
        ctr += line(s, T[i])
    p.add("contre-chant", ctr)

    # les lames : la basse frappe les noires et ne s'arrete jamais
    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 20, [(0, 1), (0, 0.5), (-1, 0.5)])
    b += bas(21, 28, [(0, 0.5), (0, 0.5), (-1, 0.5), (0, 0.5)])
    b += line("F3:1 Ab3:1 C3:1", T[COURTE])
    p.add("basse", b)

    # le bourdon migre a gauche, immobile d'un bout a l'autre
    p.add("bourdon", pedal(midi("F2"), 0, LEN))

    # Les lames : caisse claire seche sur les temps faibles. Rien a l'intro.
    p.add_drums("K.S...S.", t0=T[4], length=T[12] - T[4])
    p.add_drums([(0, "C", 7)], t0=T[12])
    p.add_drums("K.S.K.S.", t0=T[12], length=T[20] - T[12])
    p.add_drums([(0, "S"), (1, "S"), (2, "S")], t0=T[COURTE])    # les trois coups
    p.add_drums("K.SHK.SH", t0=T[21], length=T[27] - T[21])
    p.add_drums([(0, "K"), (2, "S")], t0=T[27])
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("arbresepees.mid"))
