#!/usr/bin/env python3
"""« Trois Arcs dans la Brume » — clairiere 26, les Orques des Marais. Re phrygien, 166.

Pages 290, 323, 352, 309. Trois orques a la peau rongee, trois arcs, et une
fleche qui frole la tete des l'entree. Le procede de la zone `danger` est garde —
demi-ton phrygien **mi bemol-re**, bourdon de re — mais la piece est desormais
une **marche** : la grosse caisse tient le pas et le bourdon, libere de la voix
5, n'a plus besoin d'etre refrappe toutes les deux mesures. Le tempo passe de
158 a **166** : la troupe avance.

Ce que la revision ajoute :

* **le crochet** — l'appel pointe `la la | re do`, trois notes et un ecart de
  quarte — est enonce quatre fois : mesures 5, 9 (une quarte plus haut), 21 (a
  l'octave) et 25 (sur mi bemol). Trois arcs, la meme fleche ;
* **une vraie partie B** : mesures 13-20, le mode s'ouvre sur si bemol et fa —
  les deux seuls accords majeurs du morceau — et le chant monte au sol 6 ;
* **la reponse** : mesures 8, 12, 16 et 28, le chant tient une ronde et l'arpege
  lui rend l'appel une octave plus bas, a droite ;
* **le rythme harmonique varie** : la moitie des mesures portent deux accords ;
* **la surprise** : mesure 20, le **grand silence**. Tout se fige sur un re tenu,
  la batterie se tait ; deux coups de caisse claire au dernier temps relancent la
  troupe. C'est la fleche qui passe ;
* **l'arc** : rien a l'intro qu'un coup de caisse lointain, puis la marche, puis
  la marche doublee en A', puis la cadence.

28 mesures a 4/4, 40,5 s. Forme intro(4) - A(8) - B(8) - A' a l'octave(8).

    python3 orques.py && python3 ../../../midi_to_mb.py orques.mid \\
        ORCS.MB.BIN --bpm 166 --max 2304 --wav ORQUES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 166, 4, 28
LEN = BAR * BARS

GRILLE = [
    ("Dm",), ("Dm",), ("Eb",), ("Dm",),                          # intro
    ("Dm",), ("Dm", "Cm"), ("Bb", "Eb"), ("Dm",),                # A
    ("Gm",), ("Eb", "Bb"), ("Cm", "Gm"), ("Dm",),
    ("Bb",), ("F",), ("Gm", "Cm"), ("Bb",),                      # B
    ("Eb", "Bb"), ("F", "Cm"), ("Gm",), ("Dm",),
    ("Dm",), ("Dm", "Cm"), ("Bb", "Eb"), ("Gm",),                # A'
    ("Eb",), ("Bb", "F"), ("Cm", "Eb"), ("Dm",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

HOOK = "A5:1.5 A5:.5 D6:1 C6:1"         # l'appel : deux fois la meme note, puis la quarte
HOOKG = "D6:1.5 D6:.5 G6:1 F6:1"        # le meme, une quarte plus haut
HOOK8 = "A6:1.5 A6:.5 D6:1 C6:1"
HOOKE = "Eb6:1.5 Eb6:.5 G6:1 F6:1"      # le troisieme arc, sur mi bemol

MEL = [
    "D5:4",                           "D5:2 F5:2",               # intro
    "Eb5:4",                          "D5:2 A5:2",
    HOOK,                             "Bb5:1.5 A5:.5 G5:2",      # A
    "F5:1 Bb5:1 D6:2",                "A5:4",
    HOOKG,                            "Eb6:1.5 D6:.5 Bb5:2",
    "C6:1 G5:1 Bb5:2",                "D6:4",
    "Bb5:1 D6:1 F6:2",                "A5:1.5 C6:.5 F6:2",       # B
    "G6:1 D6:1 Bb5:2",                "F6:4",
    "Eb6:1.5 D6:.5 Bb5:2",            "C6:1 A5:1 F6:2",
    "G6:1.5 F6:.5 D6:2",              "D6:4",
    HOOK8,                            "Bb6:1.5 A6:.5 G6:2",      # A'
    "F6:1 Bb6:1 D6:2",                "G6:1.5 F6:.5 D6:2",
    HOOKE,                            "D6:1 Bb5:1 F6:2",
    "C6:1.5 Bb5:.5 Eb6:2",            "D6:4",
]
assert len(MEL) == BARS

CTR = [
    "A3:4",                           "D4:4",                    # intro
    "Bb3:4",                          "A3:4",
    "A3:2 D4:2",                      "F4:2 Eb4:2",              # A
    "D4:2 Bb3:2",                     "A3:2 F4:2",
    "G3:2 Bb3:2",                     "G4:2 Eb4:2",
    "Eb4:2 G3:2",                     "A3:2 D4:2",
    "D4:2 Bb3:2",                     "C4:2 A3:2",               # B
    "Bb3:2 G3:2",                     "D4:2 F4:2",
    "G4:2 Eb4:2",                     "C4:2 A3:2",
    "Bb3:2 D4:2",                     "A3:4",
    "A3:2 D4:2",                      "F4:2 Eb4:2",              # A'
    "D4:2 Bb3:2",                     "G3:1 Bb3:1 D4:2",
    "G4:2 Eb4:2",                     "D4:2 Bb3:2",
    "Eb4:2 C4:2",                     "A3:2 D4:2",
]
assert len(CTR) == BARS

REPONSES = {                            # l'arpege rend l'appel au chant
    7:  "A4:1.5 A4:.5 D5:1 C5:1",
    11: "D4:1.5 D4:.5 A4:1 F4:1",
    15: "F4:1.5 F4:.5 Bb4:1 D5:1",
    27: "A4:1.5 A4:.5 D5:1 D4:1",
}
PAUSE = 19                              # le grand silence : tout se fige


def arp(b0, b1, pattern, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES or b == PAUSE:
            continue
        out += progression(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, pattern, lo)
    return out


def bas(b0, b1, pattern, lo=45):
    out = []
    for b in range(b0, b1):
        if b == PAUSE:
            continue
        out += progression(CH[2 * b:2 * b + 2], BAR * b, BAR / 2, pattern, lo)
    return out


def build():
    p = Piece("D", "phrygien", BPM, BAR, "Trois Arcs dans la Brume")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # l'arpege pointe : noire pointee, croche, noire — le pas de la troupe
    a = arp(0, 4, [(0, 2)])
    a += arp(4, 12, [(0, 1.5), (2, 0.5)])
    a += arp(12, 20, [(0, 0.75), (2, 0.25), (1, 1)])
    a += arp(20, 28, [(0, 0.75), (2, 0.25), (1, 0.5), (2, 0.5)])
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    a += [(midi("A4"), BAR * PAUSE, BAR)]           # la pause : un son tenu
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1.5), (0, 0.5)])
    b += bas(12, 20, [(0, 1.5), (-1, 0.5)])
    b += bas(20, 28, [(0, 1), (0, 0.5), (-1, 0.5)])
    b += [(midi("D3"), BAR * PAUSE, BAR)]
    p.add("basse", b)

    # le bourdon migre a gauche et n'est plus refrappe : la grosse caisse a pris
    # le relais du tambour, et c'est un gain de trente notes.
    p.add("bourdon", pedal(midi("D2"), 0, LEN))

    # La marche. Rien avant la mesure 3 ; un tambour lointain, puis le pas
    # complet, puis le silence de la mesure 20, puis la troupe au grand complet.
    p.add_drums([(0, "K"), (2, "K")], t0=BAR * 2)
    p.add_drums([(0, "K"), (2, "K")], t0=BAR * 3)
    p.add_drums("K..KS...", t0=BAR * 4, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    p.add_drums("K..KS..H", t0=BAR * 12, length=BAR * 7)
    p.add_drums([(3, "S"), (3.5, "S")], t0=BAR * PAUSE)   # la fleche relance
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K.HKS.HS", t0=BAR * 20, length=BAR * 7)
    p.add_drums([(0, "K"), (1.5, "K"), (2, "S")], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("orques.mid"))
