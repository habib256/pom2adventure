#!/usr/bin/env python3
"""« Les Pinces et l'Os » — clairiere 10, le Scorpion Geant et le Nain.

Variation de la couleur `danger` : meme demi-ton phrygien, meme bourdon
immobile, meme crescendo par la densite. La page 014 raconte deux choses a la
fois, la bete qui se repait et l'homme qui ne bouge plus, et la piece est donc
en deux matieres — le A et le A' sont le Scorpion, le B est le Nain.

Ce qui a change a la revision :

- **un crochet** de deux mesures, `la sib la mi do' / sib la` : la seconde
  phrygienne prise deux fois, qui est le claquement de la pince. Enonce trois
  fois, et la piece se ferme dessus ;
- **une reponse** : aux mesures 12, 20 et 28 le chant tient et les pinces —
  voix 3, a droite — repondent a sa place. C'est la lutte entendue derriere le
  tronc : deux choses qui ne parlent jamais en meme temps ;
- **la surprise** : au B, **la batterie s'arrete completement**. Huit mesures
  sans un coup, l'arpege en noires, la basse en blanches, le chant en valeurs
  longues qui descendent. C'est le seul endroit des douze clairieres ou la
  musique cesse de mordre — « il vous semble peu probable que vos Pierres de
  Magie aient de l'effet ici ». Elle revient a la mesure 21 sur une cymbale,
  apres **un temps et demi de silence general** ou plus rien ne sonne ;
- **la voix des accords a cede la place, pas le bourdon** : c'est la regle du
  `danger`. Cinq parties de hauteur — chant, pinces, contre-chant, basse,
  bourdon — la basse a droite sous l'arpege, le bourdon de mi au fond a gauche ;
- **la batterie** : le cliquetis. Charleston ferme en croches serrees, caisse
  claire seche, grosse caisse au premier temps. Rien dans l'intro, rien au B.

La phrygien, 184 a la noire — le tempo le plus vif des douze, celui de la lutte.
28 mesures a 4/4, 36,5 s. Forme intro(4) - A(8) - B(8) - A'(8).

    python3 scorpnain.py && python3 ../../../midi_to_mb.py scorpnain.mid \\
        DWARFSCORP.MB.BIN --bpm 184 --max 2304 --wav SCORPNAIN.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 184, 4, 28
LEN = BAR * BARS
HALF = BAR / 2.0
NAIN = (12, 20)                            # les mesures du Nain, en index
SILENCE = (BAR * 19 + 2.5, BAR * 20)       # plus rien, avant que ca reprenne

GRID = [
    ("Am", "Am"), ("Bb", "Bb"), ("Am", "Am"), ("Am", "Am"),    # intro — les bruits
    ("Am", "Am"), ("Bb", "Am"), ("Am", "Am"), ("Gm", "F"),     # A — le Scorpion
    ("Am", "Am"), ("Bb", "Am"), ("F", "Gm"), ("Am", "Am"),
    ("Dm", "Dm"), ("F", "F"), ("C", "C"), ("Gm", "Gm"),        # B — le Nain
    ("Dm", "Dm"), ("Bb", "Bb"), ("F", "F"), ("Am", "Am"),
    ("Am", "Am"), ("Bb", "Am"), ("Gm", "F"), ("Dm", "Dm"),     # A' — on s'en va
    ("Bb", "Bb"), ("F", "Gm"), ("Am", "Bb"), ("Am", "Am"),
]
assert len(GRID) == BARS
CH = [c for pair in GRID for c in pair]

H1 = "A5:.5 Bb5:.5 A5:1 E5:1 C6:1"         # le crochet : la pince
H2 = "Bb5:2 A5:2"

MEL = [
    "A5:1 Bb5:1 A5:2",                "Bb5:2 F5:2",            # intro
    "E5:2 A5:2",                      "C6:1 A5:1 E5:2",
    H1,                               H2,                      # A
    "E6:1 C6:1 A5:2",                 "G5:1 Bb5:1 D6:2",
    H1,                               H2,
    "F6:1 D6:1 Bb5:2",                "E6:4",                  # ← la reponse
    "D6:2 A5:2",                      "C6:2 A5:2",             # B — le Nain
    "G5:2 E6:2",                      "D6:1 Bb5:1 G5:2",
    "F6:2 D6:2",                      "Bb5:1 D6:1 F6:2",
    "A6:1 F6:1 C6:2",                 "A5:4",                  # ← la reponse
    H1,                               H2,                      # A' — on s'en va
    "G6:1 D6:1 Bb5:2",                "A5:1 C6:1 F6:2",
    "D6:1 F6:1 A6:2",                 "F6:1 Bb5:1 D6:2",
    "C6:1 A5:1 E5:1 A5:1",            "A5:.5 Bb5:.5 A5:3",     # ← la reponse
]
assert len(MEL) == BARS

CTR = [
    "C4:4",                           "D4:4",
    "A3:4",                           "E4:4",
    "C4:2 A3:2",                      "D4:2 C4:2",
    "E4:2 C4:2",                      "Bb3:2 A3:2",
    "C4:2 A3:2",                      "D4:2 F4:2",
    "A3:2 Bb3:2",                     "E4:2 A3:2",
    "F4:2 D4:2",                      "A3:2 C4:2",
    "G3:2 E4:2",                      "Bb3:2 D4:2",
    "A3:2 F4:2",                      "D4:2 Bb3:2",
    "C4:2 A3:2",                      "E4:2 C4:2",
    "A3:2 E4:2",                      "D4:2 C4:2",
    "Bb3:2 A3:2",                     "F4:2 D4:2",
    "D4:2 Bb3:2",                     "C4:2 Bb3:2",
    "C4:2 D4:2",                      "A3:2 E4:2",
]
assert len(CTR) == BARS

for _s in MEL + CTR:                                # chaque mesure fait 4 temps
    assert abs(sum(float(_t.rpartition(":")[2]) for _t in _s.split()) - BAR) < 1e-6, _s

REPONSE = {11: "A4:.5 Bb4:.5 A4:1 E4:1 C5:1",
           19: "F4:1 C5:1 A4:1.5 G4:.5",
           27: "C5:1 Bb4:1 A4:1 E4:1"}


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
    p = Piece("A", "phrygien", BPM, BAR, "Les Pinces et l'Os")
    a, b = SILENCE
    i, j = NAIN

    p.add("melodie", taire(lines(MEL, 0, bar=BAR), a, b))

    # les pinces : croches detachees sur le Scorpion, noires tenues sur le Nain
    pinces = (arpeggio(CH[:2 * i], 0, HALF, 0.5, (0, 1, 2, 1), lo=57)
              + arpeggio(CH[2 * j:], BAR * j, HALF, 0.5, (0, 1, 2, 1), lo=57))
    pinces = [(n, t, 0.42) for n, t, _ in pinces]
    pinces += arpeggio(CH[2 * i:2 * j], BAR * i, HALF, 1.0, (0, 2, 1, 2), lo=57)
    pinces = [e for e in pinces if int(e[1] // BAR) not in REPONSE]
    for k, spec in REPONSE.items():
        pinces += line(spec, k * BAR)
    p.add("pinces", taire(pinces, a, b))

    p.add("contre-chant", taire(lines(CTR, 0, bar=BAR), a, b))

    # la basse marche avec le Scorpion, elle tient avec le Nain
    marche = [(0, 1), (0, 1)]
    bas = (progression(CH[:2 * i], 0, HALF, marche, lo=47)
           + progression(CH[2 * i:2 * j], BAR * i, HALF, [(0, 2)], lo=47)
           + progression(CH[2 * j:], BAR * j, HALF, marche, lo=47))
    p.add("basse", taire(bas, a, b))

    p.add("bourdon", pedal(midi("E2"), 0, LEN, retrig=BAR * 4))

    # le cliquetis — et rien du tout pendant les huit mesures du Nain
    p.add_drums("K.HHS.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    p.add_drums("K.HHS.HH", t0=BAR * 20, length=BAR * 8)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("scorpnain.mid"))
