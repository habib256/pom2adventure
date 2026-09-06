#!/usr/bin/env python3
"""« Ce qui Monte du Bassin » — clairiere 35, la Bete du bassin. Fa eolien, 150.

Pages 209, 082, 308, 397. « Une creature enorme a la peau brune et caoutchouteuse
emerge soudain du bassin et tente de vous saisir d'un tentacule. Un magnifique
Bijou Violet brille a son front. »

Le procede de la zone `sud` est garde : marche i-VI-III-VII (Fm-Db-Ab-Eb) sur un
bourdon de fa. Les deux traits de la clairiere aussi. **Ce qui monte** : la basse
ne descend jamais a l'interieur d'une mesure — elle part de la quinte grave et
remonte l'accord, quelque chose sort de l'eau et n'y retourne pas. **Le Bijou
Violet** : le re bemol majeur, seul accord eclatant du morceau, porte la note la
plus haute, tenue. Le tempo passe de 143 a **150**.

Ce que la revision ajoute :

* **le crochet** — `fa · do · fa'`, la quinte puis la quarte, tout en montant —
  est enonce quatre fois (mesures 5, 9 sur si bemol, 21 sur la bemol, et par
  l'arpege en reponse). Il monte, comme tout le reste ;
* **une vraie partie B** (mesures 13-20) : le re bemol majeur s'installe, le
  chant atteint le **la bemol 6 tenu une ronde entiere** mesure 16 — le Bijou —
  et c'est la seule fois de la piece ou quelque chose s'arrete de bouger ;
* **la reponse** : mesures 8, 12 et 16, le chant tient et l'arpege lui rend le
  crochet une octave plus bas, a droite : ce qui repond vient d'en dessous ;
* **le rythme harmonique varie** : un accord tenu par mesure a l'intro, deux des
  la mesure 6 ;
* **la surprise, et c'est la seule des onze a se la permettre** : mesures 25 a
  28, **le bourdon monte**. Immobile sur fa pendant vingt-quatre mesures, il
  passe a la bemol, puis a si bemol, et la piece se termine sur une quarte
  suspendue — le sol se souleve. La boucle le ramene sur fa et tout recommence ;
* **la batterie sort de l'eau elle aussi** : une grosse caisse sourde et isolee
  en A — une bulle — puis les toms en B, puis la caisse claire du tentacule en
  A'. Rien du tout dans les quatre premieres mesures.

28 mesures a 4/4, 44,8 s. Forme intro(4) - A(8) - B(8) - A' a l'octave(8).

    python3 bassin.py && python3 ../../../midi_to_mb.py bassin.mid \\
        POOL.MB.BIN --bpm 150 --max 2304 --wav BASSIN.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS

GRILLE = [
    ("Fm",), ("Fm",), ("Db",), ("Fm",),                          # intro
    ("Fm",), ("Db", "Ab"), ("Eb", "Cm"), ("Fm",),                # A
    ("Bbm",), ("Db", "Ab"), ("Eb", "Cm"), ("Fm",),
    ("Db",), ("Ab", "Eb"), ("Bbm", "Fm"), ("Db",),               # B
    ("Ab", "Eb"), ("Cm", "Fm"), ("Db", "Bbm"), ("Eb",),
    ("Fm",), ("Db", "Ab"), ("Eb", "Cm"), ("Bbm",),               # A'
    ("Db", "Ab"), ("Eb", "Cm"), ("Db", "Eb"), ("Fm",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

HOOK = "F5:1 C6:1 F6:2"                 # la quinte, la quarte : tout monte
HOOKB = "Bb5:1 F6:1 Bb6:2"
HOOK8 = "Ab5:1 Eb6:1 Ab6:2"

MEL = [
    "C6:4",                           "C6:2 F6:2",               # intro
    "Db6:4",                          "Ab5:2 C6:2",
    HOOK,                             "Db6:1 Ab5:1 F6:2",        # A
    "Eb6:1 G5:1 C6:2",                "F6:4",
    HOOKB,                            "Ab6:1 F6:1 Db6:2",
    "Eb6:1 C6:1 G5:2",                "F6:4",
    "Db6:1 Ab6:1 F6:2",               "C6:1 Eb6:1 Ab6:2",        # B
    "Bb5:1 F6:1 Db6:2",               "Ab6:4",                   # le Bijou Violet
    "C6:1 Ab5:1 Eb6:2",               "G5:1 C6:1 F6:2",
    "Db6:1 F6:1 Bb6:2",               "Eb6:1 Bb5:1 G5:2",
    HOOK8,                            "Db6:1 Ab5:1 F6:2",        # A'
    "Eb6:1 G5:1 C6:2",                "Bb5:1 Db6:1 F6:2",
    "Db6:1 Ab6:1 F6:2",               "Eb6:1 C6:1 G5:2",
    "Db6:1 F6:1 Bb6:2",               "F6:2 C6:2",
]
assert len(MEL) == BARS

CTR = [
    "C4:4",                           "Ab3:4",                   # intro
    "F4:4",                           "C4:4",
    "Ab3:2 C4:2",                     "F4:2 Db4:2",              # A
    "G3:2 Eb4:2",                     "C4:2 Ab3:2",
    "Db4:2 Bb3:2",                    "F4:2 Ab3:2",
    "G3:2 C4:2",                      "Ab3:2 C4:2",
    "F4:2 Ab4:2",                     "Eb4:2 C4:2",              # B
    "Db4:2 Bb3:2",                    "F4:2 Ab4:2",
    "C4:2 Eb4:2",                     "G3:2 C4:2",
    "Db4:2 F4:2",                     "Bb3:2 G3:2",
    "Ab3:2 C4:2",                     "F4:2 Db4:2",              # A'
    "G3:2 Eb4:2",                     "Db4:2 Bb3:2",
    "F4:2 Ab3:2",                     "G3:2 C4:2",
    "Ab4:2 F4:2",                     "C4:2 Ab3:2",
]
assert len(CTR) == BARS

REPONSES = {                            # ce qui repond vient d'en dessous
    7:  "F4:1 C5:1 F4:2",
    11: "Ab4:1 F4:1 C5:2",
    15: "F4:1 Ab4:1 Db5:2",
}


def arp(b0, b1, step, shape, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        out += arpeggio(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=48):
    """La basse ne redescend qu'a la barre de mesure : elle emerge."""
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("F", "eolien", BPM, BAR, "Ce qui Monte du Bassin")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = arp(0, 4, 2.0, (0,))
    a += arp(4, 12, 1.0, (0, 2))
    a += arp(12, 28, 0.5, (0, 2, 1, 2))
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 4, [(-1, 2)])
    b += bas(4, 12, [(-1, 1), (0, 1)])
    b += bas(12, 20, [(-1, 0.5), (0, 0.5), (1, 1)])
    b += bas(20, 28, [(-1, 0.5), (0, 0.5), (1, 0.5), (2, 0.5)])
    p.add("basse", b)

    # Le bourdon est immobile vingt-quatre mesures, puis il monte : la bemol,
    # si bemol, et la piece s'acheve sur une quarte suspendue. Le sol se souleve.
    d = pedal(midi("F2"), 0, BAR * 24)
    d += pedal(midi("Ab2"), BAR * 24, BAR * 2)
    d += pedal(midi("Bb2"), BAR * 26, BAR * 2)
    p.add("bourdon", d)

    # Elle sort de l'eau : une bulle sourde en A, les toms en B, le tentacule
    # (caisse claire) en A'. Rien pendant les quatre premieres mesures.
    p.add_drums("K.....K.", t0=BAR * 4, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K..S..T.", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K.TS.KTS", t0=BAR * 20, length=BAR * 7)
    p.add_drums([(0, "K"), (1, "S"), (2, "T"), (3, "S")], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("bassin.mid"))
