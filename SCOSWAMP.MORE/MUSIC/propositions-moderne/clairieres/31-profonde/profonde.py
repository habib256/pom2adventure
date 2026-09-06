#!/usr/bin/env python3
"""« L'Eau Noire » — clairiere 31, la riviere profonde. Sol dorien, 136.

Pages 090, 044, 254, 370. « Celui qui se trouve devant vous est beaucoup plus
profond. La riviere tourbillonne en remous et n'inspire guere confiance : qui
sait quelles creatures se cachent dans son lit ? » Et sur l'autre rive, les
sangsues.

Les deux marques de la zone `riviere` sont gardees : l'arpege de croches qui
**ne s'arrete jamais** d'un bout a l'autre — pas une mesure, pas une reponse ne
l'interrompt — et le bourdon pose non sur la tonique mais sur la **quinte** (re
sous un sol dorien). Le dessin du remous non plus n'a pas bouge :
`0-2-1-2-0-1-2-1`, l'arpege revient sur lui-meme au lieu de monter.

Ce que la revision ajoute :

* **la batterie de cette piece est de l'eau, et rien d'autre** : neuf nappes de
  bruit longues — 0,6 a 1,2 seconde chacune — et quelques clapotis. Pas un seul
  coup sec, pas de grosse caisse, pas de temps marque. Sur un AY, le canal de
  bruit *est* le sifflement de l'eau ; c'est la seule des onze ou il ne bat rien ;
* **le crochet** — `re · sol | si bemol · la`, quarte montante pointee puis
  retombee — est enonce quatre fois (mesures 5, 9 sur re mineur, 21 a l'octave,
  et en croches par l'arpege) ;
* **une vraie partie B** (mesures 13-20) : le do majeur du mode dorien — le mi
  becarre sous une armure a si bemol — prend le dessus ; c'est la surface, vue
  d'en dessous, et c'est la seule clarte du morceau ;
* **la reponse sans rupture** : mesures 8, 12 et 16, le chant tient une ronde et
  l'arpege lui repond — mais en croches continues, le remous se contentant de
  prendre la forme d'une phrase. Le courant ne s'arrete pas pour parler ;
* **le rythme harmonique varie** : deux accords par mesure des la mesure 6, et un
  seul tenu quatre mesures a l'intro ;
* **la surprise** : mesures 26-27, **le bourdon descend enfin sur le sol**. Tout
  le morceau flotte sur la quinte ; deux mesures durant, on touche le fond — puis
  la pedale remonte sur le re et la boucle repart en suspension ;
* **l'arc** : la basse passe de la ronde a la noire pointee, le contre-chant du
  souffle tenu a la blanche, les nappes de bruit de une a quatre par phrase.

28 mesures a 4/4, 49,4 s. Forme intro(4) - A(8) - B(8) - A'(8).

    python3 profonde.py && python3 ../../../midi_to_mb.py profonde.mid \\
        DEEPWATER.MB.BIN --bpm 136 --max 2304 --wav PROFONDE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 136, 4, 28
LEN = BAR * BARS

GRILLE = [
    ("Gm",), ("Gm",), ("F",), ("Gm",),                           # intro
    ("Gm",), ("C", "Dm"), ("Bb", "F"), ("Gm",),                  # A
    ("Dm",), ("Bb", "C"), ("Am", "F"), ("Gm",),
    ("Bb", "F"), ("C",), ("Dm", "Am"), ("C",),                   # B
    ("Bb", "Gm"), ("C", "F"), ("Dm",), ("Gm",),
    ("Gm",), ("C", "Dm"), ("Bb", "F"), ("Dm",),                  # A'
    ("Bb", "C"), ("Am", "F"), ("C", "Dm"), ("Gm",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

HOOK = "D5:1.5 G5:.5 Bb5:1 A5:1"        # la quarte pointee, puis la retombee
HOOKD = "D6:1.5 A5:.5 F6:1 D6:1"
HOOK8 = "D6:1.5 G6:.5 Bb6:1 A6:1"

MEL = [
    "D5:4",                           "D5:2 G5:2",               # intro
    "F5:4",                           "F5:2 D5:2",
    HOOK,                             "E6:1 C6:1 A5:2",          # A
    "D6:1 Bb5:1 F5:2",                "G5:4",
    HOOKD,                            "Bb5:1 D6:1 G6:2",
    "C6:1 A5:1 E6:2",                 "D6:4",
    "Bb5:1 F6:1 D6:2",                "E6:1 G6:1 C6:2",          # B
    "D6:1 A5:1 F6:2",                 "E6:4",
    "G6:1 D6:1 Bb5:2",                "C6:1 E6:1 G6:2",
    "F6:1 D6:1 A5:2",                 "G5:2 D6:2",
    HOOK8,                            "E6:1 C6:1 A5:2",          # A'
    "D6:1 Bb5:1 F6:2",                "A5:1 D6:1 F6:2",
    "Bb5:1 D6:1 G6:2",                "C6:1 A5:1 E6:2",
    "G6:1 E6:1 C6:2",                 "D6:2 G5:2",
]
assert len(MEL) == BARS

CTR = [
    "G3:4",                           "Bb3:4",                   # intro
    "A3:4",                           "D4:4",
    "G3:2 D4:2",                      "E4:2 C4:2",               # A
    "D4:2 A3:2",                      "Bb3:2 G3:2",
    "A3:2 D4:2",                      "Bb3:2 G3:2",
    "C4:2 A3:2",                      "D4:2 G3:2",
    "D4:2 Bb3:2",                     "E4:2 G4:2",               # B
    "F4:2 A3:2",                      "E4:2 C4:2",
    "D4:2 G3:2",                      "C4:2 E4:2",
    "A3:2 F4:2",                      "D4:2 Bb3:2",
    "G3:2 D4:2",                      "E4:2 C4:2",               # A'
    "D4:2 A3:2",                      "F4:2 D4:2",
    "Bb3:2 G4:2",                     "C4:2 A3:2",
    "E4:2 C4:2",                      "D4:2 G3:2",
]
assert len(CTR) == BARS

# Les reponses restent en croches : le courant ne s'arrete pas pour parler.
REPONSES = {
    7:  "G4:.5 D5:.5 Bb4:.5 A4:.5 G4:.5 A4:.5 Bb4:.5 D5:.5",
    11: "D5:.5 A4:.5 F4:.5 D4:.5 F4:.5 A4:.5 C5:.5 D5:.5",
    15: "C5:.5 G4:.5 E4:.5 G4:.5 C5:.5 E5:.5 C5:.5 G4:.5",
}
REMOUS = (0, 2, 1, 2, 0, 1, 2, 1)       # l'arpege revient sur lui-meme


def remous(b0, b1, lo=57):
    """Huit croches par mesure, l'accord changeant au milieu — jamais un trou."""
    out = []
    for b in range(b0, b1):
        if b in REPONSES:
            continue
        for j in range(8):
            ch = CH[2 * b + (0 if j < 4 else 1)]
            out.append((pick(voicing(ch, lo), REMOUS[j]), BAR * b + j * 0.5, 0.5))
    return out


def bas(b0, b1, pattern, lo=45):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("G", "dorien", BPM, BAR, "L'Eau Noire")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    a = remous(0, BARS)
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    b = bas(0, 4, [(0, 2)])
    b += bas(4, 12, [(0, 2)])
    b += bas(12, 20, [(0, 1), (-1, 1)])
    b += bas(20, 28, [(0, 1), (0, 0.5), (-1, 0.5)])
    p.add("basse", b)

    # Le bourdon est sur la quinte, pas sur la tonique : rien ne se pose. Sauf
    # mesures 26-27, ou il descend sur le sol — on touche le fond, une fois.
    d = pedal(midi("D2"), 0, BAR * 25)
    d += pedal(midi("G2"), BAR * 25, BAR * 2)
    d += pedal(midi("D2"), BAR * 27, BAR)
    p.add("bourdon", d)

    # L'eau : des nappes de bruit longues, pas des coups. La cymbale tenue 30 a
    # 60 ticks est le sifflement du courant ; le charleston ouvert, un clapotis ;
    # la grosse caisse, la seule fois ou elle sonne, est ce qui touche le fond.
    p.add_drums([(0, "C", 30)], t0=BAR * 3)
    p.add_drums([(0, "C", 45)], t0=BAR * 11)
    p.add_drums([(0, "C", 60), (3, "O", 8)], t0=BAR * 12)
    p.add_drums([(2, "O", 6)], t0=BAR * 14)
    p.add_drums([(0, "C", 40), (3.5, "O", 6)], t0=BAR * 16)
    p.add_drums([(1, "O", 6), (3, "O", 10)], t0=BAR * 18)
    p.add_drums([(0, "C", 60)], t0=BAR * 20)
    p.add_drums([(2, "O", 8)], t0=BAR * 23)
    p.add_drums([(0, "K", 20), (2, "K", 20)], t0=BAR * 25)       # le fond
    p.add_drums([(0, "C", 55)], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("profonde.mid"))
