#!/usr/bin/env python3
"""« L'Appel du Marais » — theme d'accueil, page 000. Re dorien, 136 a la noire.

Cinq voix de hauteur et une batterie : la voix 5 est le bruit, donc le bourdon
de re a disparu — la grosse caisse en tient lieu, et elle frappe au lieu de
tenir.

Le CROCHET fait deux mesures (re-fa-sol-la, puis la retombee re-do-la) et il est
enonce **deux fois** de suite, mesures 5-6 puis 9-10, la seconde fois sur une
autre harmonie (F-G au lieu de F-Am) : la meme phrase, un autre eclairage.
Il revient une octave au-dessus a la mesure 21.

QUESTION ET REPONSE : quand la melodie tient (mesures 7, 12, 24), le
contre-chant repond en croches — voix 0 a gauche, voix 3 a droite, l'echange
traverse la stereo.

La PARTIE B (13-20) contraste par le registre — la melodie redescend d'une
octave — et par l'harmonie : si bemol, emprunte au re eolien, etranger au mode
dorien. La SURPRISE est la mesure 20, un la **majeur** : le do diese est la
seule sensible du morceau, et il ouvre la reprise.

Le SILENCE de deux temps a la fin de la mesure 20 est la vraie rupture : tout
s'arrete, puis A' repart une octave plus haut.

RYTHME HARMONIQUE : douze temps sur re mineur a l'intro, puis quatre, puis deux
a la mesure 11 ; l'harmonie se resserre a mesure que la piece avance.

28 mesures a 4/4, 49 s de boucle.

    python3 accueil.py && python3 ../../midi_to_mb.py accueil.mid \\
        WELCOME.MB.BIN --bpm 136 --max 2304 --wav ACCUEIL.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 136, 4, 28
LEN = BAR * BARS

#            intro      A1 (crochet)      A2 (crochet, autre harmonie)
CH = (["Dm", "C"] + ["Dm", "C", "F", "Am"] + ["Dm", "C", "F", "G", "Dm"]
      #        B — si bemol, registre grave, puis LA MAJEUR
      + ["Bb", "F", "C", "Gm", "Bb", "C", "Am", "A"]
      #        A' — a l'octave
      + ["Dm", "C", "F", "G", "Dm", "Bb", "C", "Dm"])
DU = ([12, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 4, 4, 4, 4]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "A5:4",                           "A5:2 D6:2",
    "D6:1 A5:1 F5:2",                 "G5:2 E5:2",
    "D5:1 F5:.5 G5:.5 A5:2",          "D6:1.5 C6:.5 A5:2",     # crochet
    "A5:4",                           "C6:1 A5:1 E5:2",        # 7 : la melodie tient
    "D5:1 F5:.5 G5:.5 A5:2",          "D6:1.5 C6:.5 A5:2",     # crochet, 2e fois
    "F6:2 E6:2",                      "D6:4",                  # 12 : la melodie tient
    "D5:1 F5:1 Bb5:2",                "A5:1.5 F5:.5 D5:2",     # B : une octave plus bas
    "E5:1 G5:1 C6:2",                 "Bb5:1 G5:1 D5:2",
    "D5:2 F5:2",                      "E5:1 G5:1 E5:1 C6:1",
    "A5:2 E5:2",                      "C#6:2 A5:2",            # 20 : la majeur, la sensible
    "D6:1 F6:.5 G6:.5 A6:2",          "E6:1.5 D6:.5 C6:2",     # A' : le crochet a l'octave
    "F6:2 G6:2",                      "A6:2 F6:2",             # 24 : la melodie tient
    "G6:1 F6:1 D6:2",                 "E6:1 C6:1 G5:2",
    "F5:1 E5:1 D5:2",                 "D5:4",
]
assert len(MEL) == BARS

CTR = [                                                        # la voix qui repond
    "A4:4",                           "A4:2 F4:2",
    "D4:2 F4:2",                      "E4:2 G4:2",
    "F4:2 A4:2",                      "E4:2 G4:2",
    "A4:.5 G4:.5 F4:1 A4:1 C5:1",     "A4:2 E4:2",             # 7 : la reponse
    "F4:2 A4:2",                      "E4:2 G4:2",
    "A4:2 B4:2",                      "A4:.5 G4:.5 F4:1 D4:1 F4:1",  # 12 : la reponse
    "D4:2 F4:2",                      "C5:2 A4:2",
    "G4:2 E4:2",                      "D4:2 G4:2",
    "Bb4:2 F4:2",                     "C5:2 G4:2",
    "C5:1 B4:1 A4:2",                 "E4:2 A4:2",
    "F4:2 A4:2",                      "G4:2 E4:2",
    "A4:2 B4:2",                      "A4:.5 G4:.5 F4:1 D4:1 A4:1",  # 24 : la reponse
    "F4:2 D4:2",                      "E4:2 G4:2",
    "A4:2 F4:2",                      "D4:1 F4:1 A4:2",        # relance la boucle
]
assert len(CTR) == BARS


def build():
    p = Piece("D", "dorien", BPM, BAR, "L'Appel du Marais")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # l'arc par la densite : noires a l'intro, croches en A, la premiere moitie
    # du B retombe a la noire, la seconde repart, A' ne lache plus
    arp = arpeggio(CH[0:2], 0, DU[0:2], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[2:11], BAR * 4, DU[2:11], 0.5, (0, 2, 1, 2), lo=53)
    arp += arpeggio(CH[11:15], BAR * 12, DU[11:15], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[15:19], BAR * 16, DU[15:19], 0.5, (0, 2, 1, 2), lo=53)
    arp += arpeggio(CH[19:], BAR * 20, DU[19:], 0.5, (0, 2, 1, 2), lo=53)
    p.add("arpege", arp)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))
    p.add("basse", progression(CH, 0, DU,
                               [(0, 1), (0, .5), (-1, .5), (0, 2)], lo=45))

    # la batterie : deux frappes a l'intro, la marche en A, la relance en A'
    p.add_drums("K...K...", t0=0, length=BAR * 4)
    p.add_drums("K.H.S.H.", t0=BAR * 4, length=BAR * 8)
    p.add_drums("K...S...", t0=BAR * 12, length=BAR * 4)
    p.add_drums("K..HS.H.", t0=BAR * 16, length=BAR * 4)
    p.add_drums("K.H.S.H.", t0=BAR * 20, length=BAR * 4)
    p.add_drums("K.HHS.HH", t0=BAR * 24, length=BAR * 4)
    p.add_drums([(0, "C")], t0=0)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 12)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 20)

    p.hush(BAR * 19 + 2, BAR * 20)                  # le silence avant la reprise
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("accueil.mid"))
