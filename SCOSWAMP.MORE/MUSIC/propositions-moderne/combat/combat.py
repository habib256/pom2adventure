#!/usr/bin/env python3
"""« Le Fer et la Pince » — surcouche de combat, 32 pages. Si eolien, 200.

200 a la noire, quinze ticks par temps : la valeur la plus rapide qui tombe
juste sur l'horloge de la carte. Maintenant que le lecteur sait faire du bruit,
c'est la **batterie** qui court — grosse caisse, caisse claire, charleston en
croches — et les quintes a vide n'ont plus qu'a frapper les temps. Le morceau y
gagne : avant, cinq voix de hauteur essayaient de faire un rythme.

Le CROCHET (si-re-mi-fa diese qui monte, sol-fa diese-re qui retombe) est enonce
mesures 5-6 puis **repris mesures 9-10**, la seconde fois sur la-fa diese
mineur : la meme phrase, une issue differente. QUESTION ET REPONSE mesures 7 et
12 : la melodie tient une ronde en haut du registre, le contre-chant repond.

La SURPRISE est mesure 16 : **deux temps de rien**, batterie comprise, en plein
milieu de la melee. Puis les huit dernieres mesures ne lachent plus.

Le bourdon de fa diese a cede sa voix a la batterie ; c'est la grosse caisse qui
tient la dominante desormais, et rien ne se resout tant que le combat dure.

20 mesures a 4/4, 24 s — la duree d'une melee, et le flux tient dans le tampon
de surcouche de 1 280 octets.

    python3 combat.py && python3 ../../midi_to_mb.py combat.mid \\
        BATTLE.MB.BIN --bpm 200 --max 1280 --wav COMBAT.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 200, 4, 20
LEN = BAR * BARS

CH = (["Bm", "Bm", "F#m"] + ["Bm", "G", "D", "A", "Bm", "G", "A", "F#m"]
      + ["Em", "G", "D", "A", "Em", "G", "F#m"])
DU = ([8, 4, 4] + [4, 4, 4, 4, 4, 4, 4, 4]
      + [4, 4, 4, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "F#5:1 F#5:1 B5:2",               "F#5:1 F#5:1 D6:2",
    "B5:1 D6:1 F#6:2",                "E6:1 D6:1 B5:2",
    "B5:1 D6:.5 E6:.5 F#6:2",         "G6:1 F#6:1 D6:2",       # le crochet
    "A6:4",                           "E6:2 C#6:2",            # 7 : la melodie tient
    "B5:1 D6:.5 E6:.5 F#6:2",         "G6:1 F#6:1 D6:2",       # le crochet, 2e fois
    "C#6:1 E6:1 A6:2",                "F#6:4",                 # 12 : la melodie tient
    "E6:1 G6:1 B6:2",                 "A6:1 G6:1 D6:2",
    "F#6:1 A6:1 D6:2",                "E6:2 -:2",              # 16 : deux temps de rien
    "B5:1 E6:1 G6:2",                 "D6:1 B5:1 G6:2",
    "A6:1 F#6:1 C#6:2",               "F#6:2 B5:2",
]
assert len(MEL) == BARS

CTR = [
    "F#4:2 B4:2",                     "F#4:2 D4:2",
    "B4:2 F#4:2",                     "D4:2 F#4:2",
    "B4:2 F#4:2",                     "G4:2 D4:2",
    "A4:.5 B4:.5 C#5:1 A4:1 F#4:1",   "E4:2 C#5:2",            # 7 : la reponse
    "B4:2 F#4:2",                     "G4:2 D4:2",
    "C#5:2 E4:2",                     "F#4:.5 G4:.5 A4:1 C#5:1 A4:1",  # 12
    "E4:2 B4:2",                      "G4:2 D4:2",
    "A4:2 F#4:2",                     "E4:2 -:2",              # 16
    "B4:2 G4:2",                      "D4:2 B4:2",
    "C#5:2 A4:2",                     "F#4:2 B4:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("B", "eolien", BPM, BAR, "Le Fer et la Pince")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    # les quintes a vide frappent les temps ; c'est la batterie qui court
    p.add("quintes", arpeggio(CH, 0, DU, 1.0, (0, 2, 0, 2), lo=53))
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=48, which=1))
    # la basse tient la garde en blanches, puis frappe le contretemps des le B
    p.add("basse", progression(CH[0:11], 0, DU[0:11], [(0, 2), (-1, 2)], lo=43)
                   + progression(CH[11:], BAR * 12, DU[11:],
                                 [(0, 1.5), (-1, .5), (0, 2)], lo=43))

    p.add_drums("K...K...", t0=0, length=BAR * 4)               # la garde
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K.HHS.H.", t0=BAR * 12, length=BAR * 8)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 4)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 16)

    p.hush(BAR * 15 + 2, BAR * 16)                              # deux temps de rien
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("combat.mid"))
