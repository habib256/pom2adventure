#!/usr/bin/env python3
"""« Le Fil d'Argent » — clairiere 29, la tente aux araignees. Do diese phrygien, 150.

Pages 144, 345, 354, 165. « Des milliers de fils forment des guirlandes entre
les arbres. Au centre, une tente somptueuse : un homme de haute taille, barbe et
sourcils d'un blanc de neige, une Amulette d'Argent en forme d'araignee. » Puis,
si l'on revient : la clairiere est en feu.

Les deux procedes sont intacts. Celui de la zone `danger` : demi-ton phrygien
**re-do diese**, bourdon immobile, crescendo par la densite et non par le volume.
Celui de la clairiere : la **toile** — une cellule de **trois** sons debitee en
croches sur des mesures de **quatre** temps, si bien qu'elle ne retombe jamais
deux fois au meme endroit du cycle. Elle roule sans se reinitialiser d'un bout a
l'autre du morceau, meme par-dessus les mesures ou l'arpege repond au chant.

Ce que la revision ajoute :

* **le crochet** — `do diese · re · do diese`, le demi-ton, puis la chute de
  quarte sur sol diese — est enonce quatre fois (mesures 5, 9, 21 a l'octave,
  26) ; c'est le fil que la piece tire ;
* **une vraie partie B** (mesures 13-16) : la majeur et mi majeur, registre haut,
  la tente somptueuse — la seule douceur du morceau ;
* **la reponse** : mesures 8, 12 et 16, le chant tient une ronde et la toile,
  a droite, repond en reprenant le crochet ;
* **le rythme harmonique varie** : deux accords dans une mesure sur deux, un
  seul accord tenu sur quatre mesures a l'intro ;
* **la surprise** : mesures 19 et 27, **sol diese majeur** — la sensible et la
  tierce majeure, deux notes etrangeres au mode. C'est l'incendie qui eclaire ce
  que le phrygien tenait dans l'ombre ;
* **la batterie est le feu**, et rien d'autre : pas un coup avant la mesure 14,
  ou l'araignee pose un pied ; puis, a partir de la mesure 17, le charleston
  crepite, les toms montent et ne s'arretent plus.

L'incendie de la page 345 est ecrit comme dans `danger` : par la densite. La
toile passe de la noire a la croche, la basse de la blanche a la noire, la
batterie de rien a tout — en une mesure.

28 mesures a 4/4, 44,8 s. Forme intro(4) - A(8) - B(4) - incendie(4) - A'(8).

    python3 araignees.py && python3 ../../../midi_to_mb.py araignees.mid \\
        SPIDERS.MB.BIN --bpm 150 --max 2304 --wav ARAIGNEES.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS
FEU = 16                                   # la mesure ou la clairiere prend feu

GRILLE = [
    ("C#m",), ("C#m",), ("D",), ("C#m",),                        # intro
    ("C#m",), ("D", "C#m"), ("Bm", "A"), ("C#m",),               # A
    ("F#m",), ("D", "A"), ("Bm", "E"), ("C#m",),
    ("A", "E"), ("F#m",), ("D", "Bm"), ("E",),                   # B
    ("C#m",), ("A", "F#m"), ("G#",), ("Bm", "E"),                # l'incendie
    ("C#m",), ("D", "C#m"), ("Bm", "A"), ("F#m",),               # A'
    ("D", "A"), ("Bm", "E"), ("G#",), ("C#m",),
]
assert len(GRILLE) == BARS
CH = [c for b in GRILLE for c in (b * 2)[:2]]

HOOK = "C#6:.5 D6:.5 C#6:1 G#5:2"       # le demi-ton, puis la chute de quarte
HOOKE = "C#6:.5 D6:.5 C#6:1 E6:2"
HOOK8 = "C#6:.5 D6:.5 C#6:1 G#6:2"

MEL = [
    "G#5:4",                          "G#5:2 C#6:2",             # intro
    "A5:4",                           "F#5:2 G#5:2",
    HOOK,                             "D6:1 A5:1 F#5:2",         # A
    "B5:1 E6:1 C#6:2",                "A5:4",
    HOOKE,                            "F#6:1 D6:1 A5:2",
    "B5:1 G#5:1 E6:2",                "C#6:4",
    "A5:1 C#6:1 E6:2",                "F#6:1 C#6:1 A5:2",        # B
    "D6:1 B5:1 F#6:2",                "E6:4",
    "C#6:1 G#5:1 E6:2",               "A6:1 E6:1 C#6:2",         # l'incendie
    "C6:1 D#6:1 G#6:2",               "B5:1 F#6:1 D6:2",
    HOOK8,                            "D6:1 A6:1 F#6:2",         # A'
    "B5:1 E6:1 C#6:2",                "A5:1 C#6:1 F#6:2",
    "D6:1 F#6:1 A6:2",                HOOKE,
    "C6:1 D#6:1 G#6:2",               "C#6:2 G#5:2",
]
assert len(MEL) == BARS

CTR = [
    "C#4:4",                          "G#3:4",                   # intro
    "A3:4",                           "C#4:4",
    "G#3:2 E4:2",                     "A3:2 F#4:2",              # A
    "B3:2 A3:2",                      "C#4:2 G#3:2",
    "A3:2 C#4:2",                     "F#4:2 D4:2",
    "B3:2 G#3:2",                     "E4:2 C#4:2",
    "A3:2 C#4:2",                     "A3:2 F#4:2",              # B
    "D4:2 B3:2",                      "G#3:2 B3:2",
    "E4:2 C#4:2",                     "C#4:2 A3:2",              # l'incendie
    "D#4:2 G#3:2",                    "B3:2 F#4:2",
    "G#3:2 E4:2",                     "A3:2 F#4:2",              # A'
    "B3:2 G#3:2",                     "C#4:2 A3:2",
    "D4:2 F#4:2",                     "B3:2 E4:2",
    "D#4:2 G#3:2",                    "C#4:2 G#3:2",
]
assert len(CTR) == BARS

REPONSES = {                            # la toile repond au chant
    7:  "C#5:.5 D5:.5 C#5:1 G#4:2",
    11: "A4:1 C#5:1 E5:2",
    15: "G#4:.5 A4:.5 G#4:1 E5:2",
}
CELLULE = (0, 2, 1)                     # trois sons — la toile


def toile(b0, b1, step, lo=57, k0=0):
    """La cellule de trois sons, debitee sans jamais se reinitialiser.

    Le compteur `k` avance meme dans les mesures sautees : la toile continue de
    tourner derriere la reponse, et retombe decalee de l'autre cote.
    """
    out, k, n = [], k0, int(round(BAR / step))
    for b in range(b0, b1):
        if b not in REPONSES:
            for j in range(n):
                ch = CH[2 * b + (0 if j < n // 2 else 1)]
                out.append((pick(voicing(ch, lo), CELLULE[(k + j) % 3]),
                            BAR * b + j * step, step))
        k += n
    return out, k


def bas(b0, b1, pattern, lo=45):
    return progression(CH[2 * b0:2 * b1], BAR * b0, BAR / 2, pattern, lo)


def build():
    p = Piece("C#", "phrygien", BPM, BAR, "Le Fil d'Argent")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # avant le feu, la toile est en noires ; a partir de la mesure 17, en croches
    a, k = toile(0, FEU, 1.0)
    b2, _ = toile(FEU, BARS, 0.5, k0=k)
    a += b2
    for b, spec in REPONSES.items():
        a += line(spec, BAR * b)
    p.add("arpege", a)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))

    # l'incendie : la basse passe de la blanche a la noire et n'y revient pas
    bs = bas(0, 4, [(0, 2)])
    bs += bas(4, FEU, [(0, 2)])
    bs += bas(FEU, BARS, [(0, 1), (-1, 1)])
    p.add("basse", bs)

    # le bourdon migre a gauche (la voix 5 est a la batterie) et ne bouge pas
    p.add("bourdon", pedal(midi("C#2"), 0, LEN))

    # La batterie EST le feu. Un pied d'araignee mesure 14, puis plus rien
    # jusqu'a l'incendie — et l'incendie ne s'arrete plus.
    p.add_drums([(0, "H"), (2.5, "H")], t0=BAR * 13)
    p.add_drums([(0, "H"), (1.5, "H"), (3, "H")], t0=BAR * 15)
    p.add_drums([(0, "C", 7), (0, "K")], t0=BAR * FEU)
    p.add_drums("H.HHH.H.", t0=BAR * FEU, length=BAR * 4)
    p.add_drums("K...S...", t0=BAR * FEU, length=BAR * 4)
    p.add_drums("H.HHH.HH", t0=BAR * 20, length=BAR * 8)
    p.add_drums("K..TS..K", t0=BAR * 20, length=BAR * 7)
    p.add_drums([(0, "K"), (2, "S"), (3, "T")], t0=BAR * 27)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("araignees.mid"))
