#!/usr/bin/env python3
"""« Le Rocher qui Respire » — clairiere 27, le cul-de-sac de la Bete. Sol phrygien, 143.

Pages 011, 210, 299, 125, 228, 243. « Soudain, le rocher bouge : ce n'etait pas
de la pierre. Une BETE IMMONDE a six pattes griffues s'avance. Sa respiration
lourde fait vibrer le bois. »

Elle reste la seule des trente-cinq a ne pas etre a quatre temps : **6/4**, et
l'arpege y boite en 1 + ½ + ½ + 1 + 1½ + 1½, six pattes qui ne tombent pas
ensemble. Le procede de la zone `danger` est intact : demi-ton phrygien la
bemol-sol, bourdon de sol refrappe a chaque mesure — la respiration.

Ce que la revision ajoute :

* **la batterie du danger** : deux coups de grosse caisse colles, *loub-doub*, le
  **cœur qui bat sourd** sous le rocher. Il bat lentement en A, deux fois par
  mesure en B, et sans repit en A' ;
* **le crochet** — `re · mi bemol · re`, long-bref-long, le demi-ton phrygien
  etire sur six temps — ouvre A (mesure 3), revient a l'octave en A' (mesure 15)
  et conclut la piece ;
* **une vraie partie B** (mesures 9-14) : le chant passe au-dessus du sol 6 et
  l'harmonie quitte le sol pour do mineur, si bemol, fa mineur ;
* **la reponse** : mesures 8 et 18, le chant tient une ronde pointee et l'arpege
  lui rend le crochet une octave plus bas ;
* **le rythme harmonique varie** : les mesures a un accord gardent la boiterie a
  six temps, celles a deux accords la coupent en deux — la Bete change de pas ;
* **la surprise** : mesure 14, **la Bete cesse de respirer**. Un silence complet
  de la batterie sur un sol tenu, six temps entiers. Puis le cœur repart, plus
  vite qu'avant ;
* **la cadence** : la bemol - sol, le demi-ton phrygien pose a la basse, mesure
  18, et la boucle repart sur le meme sol.

18 mesures a 6/4, 45,3 s. Forme intro(2) - A(6) - B(6) - A'(4).

    python3 bete.py && python3 ../../../midi_to_mb.py bete.mid \\
        BEAST.MB.BIN --bpm 143 --max 2304 --wav BETE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 143, 6, 18
LEN = BAR * BARS

GRILLE = [
    ("Gm",), ("Gm",),                                            # intro
    ("Gm",), ("Ab",), ("Gm", "Fm"), ("Eb",),                     # A
    ("Cm", "Ab"), ("Gm",),
    ("Cm",), ("Ab", "Eb"), ("Bb",), ("Fm", "Cm"),                # B
    ("Eb", "Bb"), ("Gm",),
    ("Gm",), ("Ab", "Fm"), ("Eb", "Cm"), ("Gm",),                # A'
]
assert len(GRILLE) == BARS

HOOK = "D5:2 Eb5:1 D5:3"                # long - bref - long : la respiration
HOOK8 = "D6:2 Eb6:1 D6:3"

MEL = [
    "D5:6",                           "D5:2 F5:1 G5:3",          # intro
    HOOK,                             "Eb5:2 G5:1 Bb5:3",        # A
    "D6:2 Bb5:1 G5:3",                "Eb6:2 D6:1 Bb5:3",
    "C6:2 Ab5:1 Eb6:3",               "D6:6",
    "G5:2 C6:1 Eb6:3",                "Ab6:2 Eb6:1 C6:3",        # B
    "Bb5:2 D6:1 F6:3",                "C6:2 Ab5:1 F6:3",
    "Eb6:2 Bb5:1 G6:3",               "D6:6",
    HOOK8,                            "Eb6:2 C6:1 Ab5:3",        # A'
    "Bb5:2 Eb6:1 G6:3",               "D6:3 D5:3",
]
assert len(MEL) == BARS

CTR = [
    "G3:6",                           "Bb3:6",                   # intro
    "D4:3 Bb3:3",                     "C4:3 Ab3:3",              # A
    "Bb3:3 D4:3",                     "G3:3 Bb3:3",
    "Ab3:3 C4:3",                     "D4:3 G3:3",
    "Eb4:3 C4:3",                     "C4:3 Ab4:3",              # B
    "D4:3 Bb3:3",                     "Ab3:3 C4:3",
    "G4:3 Eb4:3",                     "D4:6",
    "Bb3:3 D4:3",                     "C4:3 Ab3:3",              # A'
    "G3:3 Eb4:3",                     "D4:3 G3:3",
]
assert len(CTR) == BARS

REPONSES = {                            # l'arpege reprend le crochet
    7:  "D4:2 Eb4:1 D4:1 A3:2",
    17: "D4:2 Eb4:1 D4:3",
}
PAUSE = 13                              # la Bete cesse de respirer

LIMP = [(0, 1), (2, 0.5), (1, 0.5), (0, 1), (2, 1.5), (1, 1.5)]
DEMI = [(0, 1), (2, 0.5), (1, 0.5), (0, 1)]


def arp(b0, b1, lo=57):
    """La demarche a six pattes ; deux accords dans la mesure la coupent en deux."""
    out = []
    for b in range(b0, b1):
        if b in REPONSES or b == PAUSE:
            continue
        if len(GRILLE[b]) == 1:
            out += progression([GRILLE[b][0]], BAR * b, BAR, LIMP, lo)
        else:
            out += progression(list(GRILLE[b]), BAR * b, BAR / 2, DEMI, lo)
    return out


def bas(b0, b1, pattern, lo=45):
    out = []
    for b in range(b0, b1):
        if b == PAUSE:
            continue
        ch = (GRILLE[b] * 2)[:2]
        out += progression(list(ch), BAR * b, BAR / 2, pattern, lo)
    return out


def build():
    p = Piece("G", "phrygien", BPM, BAR, "Le Rocher qui Respire")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = arp(0, 18)
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    a += [(midi("D4"), BAR * PAUSE, BAR)]           # la pause : un son tenu
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 2, [(0, 3)])
    b += bas(2, 8, [(0, 2), (-1, 1)])
    b += bas(8, 14, [(0, 1.5), (0, 0.5), (-1, 1)])
    b += bas(14, 18, [(0, 1), (2, 0.5), (0, 0.5), (-1, 1)])
    b += [(midi("G2"), BAR * PAUSE, BAR)]
    p.add("basse", b)

    # le bourdon migre a gauche mais garde sa respiration : une frappe par mesure
    p.add("bourdon", pedal(midi("G2"), 0, LEN, retrig=BAR))

    # Le cœur : deux grosses caisses collees, loub-doub. Lent en A, deux fois par
    # mesure en B, sans repit en A'. Rien pendant la pause de la mesure 14.
    p.add_drums("KK..........", t0=BAR * 2, length=BAR * 6)
    p.add_drums("KK....KK....", t0=BAR * 8, length=BAR * 5)
    p.add_drums("......T.....", t0=BAR * 10, length=BAR * 3)
    p.add_drums([(2.5, "T"), (5, "T")], t0=BAR * 12)
    p.add_drums([(0, "C", 7)], t0=BAR * 14)
    p.add_drums("KK.TKK..KK.T", t0=BAR * 14, length=BAR * 3)
    p.add_drums("KK..KK......", t0=BAR * 17, length=BAR)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("bete.mid"))
