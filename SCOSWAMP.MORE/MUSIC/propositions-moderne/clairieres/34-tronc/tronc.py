#!/usr/bin/env python3
"""« Pierres Plates » — clairiere 34, les pierres et le tronc creux. Do eolien, 150.

Pages 105, 330, 390. « Le sol y est ferme ; vous pouvez y penetrer d'un pas
assure. Des pierres plates de grande taille, un tronc creux massif, et deux
chemins. » Et au retour : « le tronc a deja abrite autre chose que des
ossements. »

C'est la seule clairiere sure des onze — sol ferme, pas de monstre a l'entree —
et la musique le dit par le **vide**, pas par la joie. Le procede de la zone
`sud` est la : marche i-VI-III-VII (Cm-Ab-Eb-Bb) sur un bourdon de do immobile.
Celui de la clairiere aussi : l'arpege ne joue que des **quintes a vide** (la
liste `CREUX` remplace chaque accord par sa quinte nue).

Le lit d'accords tenus a cede sa voix a la batterie ; c'est donc le
**contre-chant** qui porte desormais la seule tierce du morceau, et lui seul qui
dise le mode. Le tronc est un peu plus creux qu'avant.

Ce que la revision ajoute :

* **le crochet est le coup sur le bois** : deux noires sur la meme hauteur, puis
  une chute de quarte — `do do | sol`. On frappe le tronc pour savoir s'il est
  habite. Enonce quatre fois (mesures 5, 9 sur mi bemol, 22 a l'octave, et par
  l'arpege en reponse) ;
* **la batterie est faite de toms et presque rien d'autre** : deux coups colles,
  bois sur bois, jamais de charleston. La grosse caisse n'entre qu'en B, quand
  on decide d'y regarder de plus pres ;
* **une vraie partie B** (mesures 13-20) : le registre monte au la bemol 6 et
  l'harmonie s'installe sur fa mineur et si bemol, les deux degres que A n'a pas ;
* **la reponse** : mesures 8, 12 et 16, le chant tient une ronde et l'arpege
  rend le coup — les quintes a vide repondent au bois ;
* **le rythme harmonique varie** : un accord tenu par mesure a l'intro, deux des
  la mesure 6, un seul de nouveau a la cadence ;
* **la surprise** : mesure 21, **on frappe et on ecoute**. Deux coups de tom, et
  puis plus rien : la batterie disparait une mesure entiere, les cinq voix
  tiennent un do mineur immobile, et personne ne repond du fond du tronc ;
* **l'arc** : deux notes d'arpege par mesure a l'intro, huit en A' ; la basse
  passe de la ronde a la croche.

28 mesures a 4/4, 44,8 s. Forme intro(4) - A(8) - B(8) - on ecoute(1) - A'(7).

    python3 tronc.py && python3 ../../../midi_to_mb.py tronc.mid \\
        LOG.MB.BIN --bpm 150 --max 2304 --wav TRONC.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS
ECOUTE = 20                             # la mesure ou l'on frappe et on ecoute

GRILLE = [
    ("Cm",), ("Gm",), ("Ab",), ("Cm",),                          # intro
    ("Cm",), ("Ab", "Eb"), ("Bb", "Gm"), ("Cm",),                # A
    ("Cm",), ("Fm", "Cm"), ("Ab", "Bb"), ("Cm",),
    ("Ab", "Eb"), ("Bb",), ("Fm", "Cm"), ("Eb",),                # B
    ("Ab", "Bb"), ("Cm", "Gm"), ("Fm", "Ab"), ("Bb",),
    ("Cm",),                                                     # on ecoute
    ("Cm",), ("Ab", "Eb"), ("Bb", "Gm"), ("Fm", "Cm"),           # A'
    ("Ab", "Bb"), ("Eb", "Gm"), ("Cm",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]
# le tronc est creux : l'arpege ne connait que la quinte a vide de chaque accord
CREUX = [c.replace("m", "") + "5" for c in CH]

HOOK = "C6:1 C6:1 G5:2"                 # le coup sur le bois, puis la quarte
HOOKE = "Eb6:1 Eb6:1 C6:2"
HOOK8 = "C6:1 C6:1 G6:2"

MEL = [
    "G5:4",                           "G5:2 D6:2",               # intro
    "Eb6:4",                          "C6:2 G5:2",
    HOOK,                             "Eb6:1 C6:1 G5:2",         # A
    "F6:1 D6:1 Bb5:2",                "C6:4",
    HOOKE,                            "Ab5:1 C6:1 F6:2",
    "Eb6:1 G5:1 D6:2",                "C6:4",
    "Ab5:1 Eb6:1 C6:2",               "Bb5:1 F6:1 D6:2",         # B
    "Ab6:1 F6:1 C6:2",                "G6:4",
    "Eb6:1 C6:1 Ab5:2",               "G6:1 Eb6:1 Bb5:2",
    "F6:1 Ab6:1 C6:2",                "D6:1 Bb5:1 G5:2",
    "C6:4",                                                      # on ecoute
    HOOK8,                            "Eb6:1 C6:1 Ab5:2",        # A'
    "F6:1 D6:1 Bb5:2",                "Ab5:1 F6:1 C6:2",
    "Eb6:1 C6:1 Ab5:2",               "G6:1 Eb6:1 D6:2",
    "C6:2 G5:2",
]
assert len(MEL) == BARS

CTR = [                                 # la seule voix qui ait encore une tierce
    "C4:4",                           "Bb3:4",                   # intro
    "Ab3:4",                          "Eb4:4",
    "Eb4:2 C4:2",                     "C4:2 G3:2",               # A
    "D4:2 Bb3:2",                     "Eb4:2 C4:2",
    "G3:2 Eb4:2",                     "Ab3:2 C4:2",
    "C4:2 D4:2",                      "Eb4:2 C4:2",
    "C4:2 G3:2",                      "D4:2 F4:2",               # B
    "Ab3:2 Eb4:2",                    "G3:2 Bb3:2",
    "C4:2 D4:2",                      "Eb4:2 Bb3:2",
    "Ab3:2 C4:2",                     "D4:2 F4:2",
    "Eb4:4",                                                     # on ecoute
    "Eb4:2 C4:2",                     "C4:2 G3:2",               # A'
    "D4:2 Bb3:2",                     "Ab3:2 Eb4:2",
    "C4:2 D4:2",                      "G3:2 Bb3:2",
    "Eb4:2 C4:2",
]
assert len(CTR) == BARS

REPONSES = {                            # les quintes a vide rendent le coup
    7:  "C4:1 C4:1 G4:2",
    11: "G4:1 G4:1 C5:2",
    15: "Bb4:1 Bb4:1 F4:2",
}


def arp(b0, b1, step, shape, lo=57):
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        out += arpeggio(CREUX[2 * b:2 * b + 2], BAR * b, BAR / 2, step, shape, lo)
    return out


def bas(b0, b1, pattern, lo=43):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("C", "eolien", BPM, BAR, "Pierres Plates")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = arp(0, 4, 2.0, (0,))
    a += arp(4, 12, 1.0, (0, 1))
    a += arp(12, 20, 0.5, (0, 1, 2, 1))
    a += arp(20, 21, 2.0, (0,))
    a += arp(21, 28, 0.5, (0, 1, 2, 1))
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 1), (-1, 1)])
    b += bas(12, 20, [(0, 1), (0, 0.5), (-1, 0.5)])
    b += bas(20, 21, [(0, 2)])
    b += bas(21, 28, [(0, 0.5), (0, 0.5), (-1, 0.5), (0, 0.5)])
    p.add("basse", b)

    # le bourdon de do migre a gauche ; il ne bouge pas, le sol est ferme
    p.add("bourdon", pedal(midi("C2"), 0, LEN))

    # Du bois sur du bois : deux toms colles, jamais de charleston. La grosse
    # caisse n'entre qu'en B. Mesure 21, deux coups et le silence : on ecoute.
    p.add_drums("TT......", t0=BAR * 4, length=BAR * 8)
    p.add_drums("KT..S.TT", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "T"), (0.5, "T")], t0=BAR * ECOUTE)
    p.add_drums("KT.TS.TT", t0=BAR * 21, length=BAR * 6)
    p.add_drums([(0, "K"), (2, "T"), (2.5, "T")], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("tronc.mid"))
