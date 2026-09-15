#!/usr/bin/env python3
"""« Cinq Voix derriere l'Arbre » — clairiere 8, la clairiere aux brigands.

Variation de la couleur `nord`. L'ostinato de la zone est ici une cellule de
**cinq notes** — un homme par note, quatre croches et une noire — donc de trois
temps, dans une mesure qui en compte quatre : la figure decale d'un temps a
chaque mesure et ne retombe a sa place que toutes les quatre mesures. C'est ce
qu'on entend depuis derriere l'arbre de la page 065, cinq voix qui parlent en
meme temps sans jamais dire la meme chose au meme moment.

L'harmonie est le tetracorde descendant re - do - si bemol - la, la marche de
tous les brigands de la musique modale.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `la re' do' la fa / sol fa mi re` : une
  descente effrontee, celle de gens qui ne sont pas mechants mais qui prennent
  la bourse. Enonce trois fois ;
- **une reponse** : aux mesures 8, 12 et 28 le chant tient et les cinq voix —
  voix 3, a droite — repondent a sa place. On les entend de l'autre cote ;
- **la surprise**, et c'est la meilleure des douze : la piece **finit en re
  majeur**. Le fa diese de la derniere mesure n'existe nulle part ailleurs
  dans le morceau ; il tombe apres un accord de **la majeur** a la mesure 20,
  qui l'annonce. Les brigands vous saluent. Et comme la boucle repart sur le
  re mineur de l'intro, la tierce se recouvre a chaque tour ;
- **un silence** : mesure 20, un temps et demi ou plus personne ne parle. Les
  cinq voix se taisent, la caisse claire reste seule, et c'est la que l'on
  decide de les saluer ou de les charger ;
- **la cellule s'aligne** aux quatre dernieres mesures : la noire finale
  s'allonge a la blanche, la cellule fait quatre temps, tout retombe ensemble ;
- **la batterie** : un tambourin de foire. Contretemps au charleston, caisse
  claire aux deuxieme et quatrieme temps, grosse caisse au premier. Rien
  derriere l'arbre — l'intro est muette. La voix 5 lui revient, le bourdon de
  re a cede la place.

Re mineur eolien (majeur a la fin), 187,5 a la noire, 28 mesures a 4/4, 35,8 s.
Forme intro(4) - A(8) - B(8) - A'(8).

    python3 brigands.py && python3 ../../../midi_to_mb.py brigands.mid \\
        BRIGANDS.MB.BIN --bpm 187.5 --max 2304 --wav BRIGANDS.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 3000 / 16, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0
ALIGNE = BAR * 24                          # la cellule retombe d'aplomb
SILENCE = (BAR * 19 + 2.5, BAR * 20)       # plus personne ne parle

GRID = [
    ("Dm", "Dm"), ("Dm", "Dm"), ("Bb", "Bb"), ("C", "C"),      # intro — le champignon
    ("Dm", "Dm"), ("C", "Bb"), ("Dm", "Dm"), ("Am", "C"),      # A — les cinq hommes
    ("Dm", "Dm"), ("C", "Bb"), ("Gm", "Am"), ("Bb", "C"),
    ("Gm", "Gm"), ("Dm", "Dm"), ("Bb", "F"), ("C", "C"),       # B — la cachette
    ("Am", "Am"), ("F", "C"), ("Bb", "Bb"), ("A", "A"),        # ← la majeur
    ("Dm", "Dm"), ("C", "Bb"), ("Dm", "Dm"), ("Am", "C"),      # A' — le salut
    ("Gm", "Gm"), ("Bb", "C"), ("Gm", "A"), ("D", "D"),        # ← re majeur
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "A5:1 D6:.5 C6:.5 A5:1 F5:1"          # le crochet : la descente effrontee
H2 = "G5:1.5 F5:.5 E5:1 D5:1"

MEL = [
    "D5:2 A5:2",                      "F5:1 D5:1 A5:2",        # intro
    "Bb5:1 F5:1 D6:2",                "C6:1 G5:1 E5:2",
    H1,                               H2,                      # A
    "Bb5:1 D6:1 F6:2",                "E6:4",                  # ← la reponse
    H1,                               H2,
    "G5:1 Bb5:1 D6:2",                "A5:4",                  # ← la reponse
    "G5:1 Bb5:1 D6:2",                "F6:1 D6:1 A5:2",        # B — la cachette
    "Bb5:1 D6:1 F6:2",                "E6:1 C6:1 G5:2",
    "A5:1 C6:1 E6:2",                 "F6:1 A6:1 C6:2",
    "D6:1 Bb5:1 F6:2",                "C#6:1 E6:1 A6:2",       # ← do diese
    H1,                               H2,                      # A' — le salut
    "D6:1 A5:1 F6:2",                 "E6:1 C6:1 G5:2",
    "G5:1 Bb5:1 D6:2",                "F6:1 D6:1 Bb5:2",
    "E6:1 G6:1 C#6:1 E6:1",           "D6:4",                  # ← re majeur
]
assert len(MEL) == BARS

CTR = [
    "F4:4",                           "D4:4",
    "Bb3:4",                          "E4:4",
    "A3:2 D4:2",                      "E4:2 G4:2",
    "F4:2 D4:2",                      "E4:2 C4:2",
    "A3:2 F4:2",                      "G4:2 Bb3:2",
    "D4:2 C4:2",                      "F4:2 E4:2",
    "Bb3:2 G4:2",                     "A3:2 F4:2",
    "D4:2 Bb3:2",                     "G4:2 E4:2",
    "E4:2 C4:2",                      "A3:2 E4:2",
    "F4:2 D4:2",                      "C#4:2 E4:2",
    "A3:2 D4:2",                      "E4:2 G4:2",
    "F4:2 D4:2",                      "E4:2 C4:2",
    "Bb3:2 G4:2",                     "F4:2 E4:2",
    "D4:2 C#4:2",                     "F#4:2 A3:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

CINQ = [midi("D4"), midi("F4"), midi("A4"), midi("G4"), midi("E4")]

REPONSE = {7:  "A4:1 F4:1 D4:1.5 C4:.5",
           11: "D4:1 G4:1 Bb4:1 A4:1",
           27: "A4:1 F#4:1 D4:1 A4:1"}      # ← le fa diese de la fin


def tenue(chords, per, lo, which=1, t0=0.0):
    """Le lit d'accords : une note tenue, fusionnee quand l'accord se repete."""
    out = []
    for i, c in enumerate(chords):
        n = pick(voicing(c, lo), which)
        if out and out[-1][0] == n:
            out[-1][2] += per
        else:
            out.append([n, t0 + i * per, per])
    return [tuple(e) for e in out]


def sec(part, coupe=0.30):
    """Detache : la note lache avant la suivante."""
    return [(n, t, max(d - coupe, 0.2)) for n, t, d in part]


def taire(part, a, b):
    """Le silence general : rien ne sonne entre `a` et `b`, tout repart ensemble."""
    out = []
    for n, t, d in part:
        if a - 1e-6 <= t < b - 1e-6:
            continue
        if t < a - 1e-6 < t + d:
            d = a - t
        out.append((n, t, d))
    return out


def build():
    p = Piece("D", "eolien", BPM, BAR, "Cinq Voix derriere l'Arbre")
    a, b = SILENCE

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # cinq notes en trois temps, puis cinq notes en quatre : le silence tombe.
    # Le cycle ne s'interrompt pas dans les mesures de reponse : on le couvre.
    cinq = (ostinato(CINQ, [.5, .5, .5, .5, 1], 0, ALIGNE, gap=0.08)
            + ostinato(CINQ, [.5, .5, .5, .5, 2], ALIGNE, LEN - ALIGNE, gap=0.08))
    cinq = [e for e in cinq if int(e[1] // BAR) not in REPONSE]
    for i, spec in REPONSE.items():
        cinq += line(spec, i * BAR)
    p.add("cinq voix", taire(cinq, a, b))

    p.add("contre-chant", taire(sec(lines(CTR, 0, bar=BAR)), a, b))
    p.add("accords", taire(tenue(CH, HALF, lo=50), a, b))

    # la basse pose jusqu'au salut, puis balance croche pointee - croche
    bas = (progression(CH[:40], 0, HALF, [(0, 1.5), (None, .5)], lo=45)
           + progression(CH[40:], BAR * 20, HALF, [(0, 1.5), (0, .5)], lo=45))
    p.add("basse", taire(sec(bas, 0.35), a, b))

    # le tambourin de foire : contretemps, caisse claire aux temps pairs
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.H.S.HH", t0=BAR * 12, length=BAR * 7 + 2.5)
    p.add_drums([(0, "S"), (.5, "S"), (1, "S", 5)], t0=BAR * 19 + 2.5)
    p.add_drums("K.H.S.H.", t0=BAR * 20, length=BAR * 8)
    p.add_drums("......O.", t0=BAR * 20, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 12)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("brigands.mid"))
