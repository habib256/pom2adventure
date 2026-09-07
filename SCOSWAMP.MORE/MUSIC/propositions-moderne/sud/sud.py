#!/usr/bin/env python3
"""« Sentiers Verts » — le Marais sud, douze clairieres. Re eolien, 150.

Marcher longtemps sans savoir ou : la zone la plus vaste a la musique la moins
pressee de conclure. Cinq voix de hauteur et une batterie de marche ; le bourdon
de re a cede sa voix a la grosse caisse, qui marque le pas a sa place.

Le CROCHET (re-fa-la qui monte, si bemol-la-fa qui redescend) est enonce **deux
fois**, mesures 5-6 puis 9-10 ; la seconde fois il debouche sur un **la majeur**
(mesure 11), seule sensible du morceau, et la cadence sur re en devient franche.

QUESTION ET REPONSE mesures 7, 12 et 24 : la melodie tient, le contre-chant
repond.

La SURPRISE est aux mesures 17-18 : tout passe en demi-mesure — la batterie ne
frappe plus que les temps 1 et 3, l'arpege retombe a la noire, l'harmonie tient
huit temps sur si bemol. Le sentier debouche sur une trouee, on ralentit, puis
la marche reprend.

Le si bemol separe cette piece du re dorien de l'accueil : **meme tonique,
autre monde.** Le joueur qui ressort du Marais (page 208) reentend le si becarre
du village ; c'est le seul repere tonal du jeu, et il est gratuit.

28 mesures a 4/4, 44,8 s.

    python3 sud.py && python3 ../../midi_to_mb.py sud.mid \\
        SOUTHSWAMP.MB.BIN --bpm 150 --max 2304 --wav MARAISUD.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 150, 4, 28
LEN = BAR * BARS

CH = (["Dm", "Bb", "C"] + ["Dm", "Bb", "F", "C"] + ["Dm", "Bb", "Gm", "A", "Dm"]
      + ["Bb", "F", "C", "Gm", "Bb", "C", "A"]
      + ["Dm", "Bb", "F", "C", "Dm", "Gm", "C", "Dm"])
DU = ([8, 4, 4] + [4, 4, 4, 4] + [4, 4, 2, 2, 4]
      + [4, 4, 4, 4, 8, 4, 4]
      + [4, 4, 2, 2, 4, 4, 4, 8])
assert len(CH) == len(DU) and sum(DU) == LEN

MEL = [
    "A5:2 D6:2",                      "F5:2 A5:2",
    "D5:2 F5:2",                      "E5:2 G5:2",
    "D5:1 F5:1 A5:2",                 "Bb5:1.5 A5:.5 F5:2",    # le crochet
    "A5:4",                           "E6:1.5 C6:.5 G5:2",     # 7 : la melodie tient
    "D5:1 F5:1 A5:2",                 "Bb5:1.5 A5:.5 F5:2",    # le crochet, 2e fois
    "G5:2 C#6:2",                     "D6:4",                  # 11-12 : la sensible
    "F5:1 Bb5:1 D6:2",                "C6:1 A5:1 F5:2",
    "G5:1 C6:1 E6:2",                 "D6:1 Bb5:1 G5:2",
    "F6:2 D6:2",                      "Bb5:2 F5:2",            # 17-18 : la trouee
    "E6:1 G6:1 C6:2",                 "E6:2 C#6:2",
    "D6:1 F6:1 A6:2",                 "G6:1.5 F6:.5 D6:2",     # le crochet a l'octave
    "C6:1 F6:1 A6:2",                 "D6:4",                  # 24 : la melodie tient
    "D6:1 Bb5:1 G6:2",                "F6:1 D6:1 Bb5:2",
    "C6:1 E6:1 G6:1 E6:1",            "D6:4",
]
assert len(MEL) == BARS

CTR = [
    "A4:2 D4:2",                      "F4:2 D4:2",
    "Bb4:2 D4:2",                     "G4:2 E4:2",
    "A4:2 F4:2",                      "D4:2 Bb4:2",
    "C5:.5 Bb4:.5 A4:1 F4:1 A4:1",    "G4:2 E4:2",             # 7 : la reponse
    "A4:2 F4:2",                      "D4:2 Bb4:2",
    "G4:2 E4:2",                      "A4:.5 Bb4:.5 A4:1 F4:1 D4:1",  # 12 : la reponse
    "D4:2 F4:2",                      "C5:2 A4:2",
    "G4:2 E4:2",                      "D4:2 Bb4:2",
    "F4:2 D4:2",                      "Bb4:2 F4:2",
    "G4:2 C5:2",                      "A4:2 E4:2",
    "A4:2 F4:2",                      "D4:2 Bb4:2",
    "C5:2 A4:2",                      "A4:.5 Bb4:.5 A4:1 F4:1 A4:1",  # 24 : la reponse
    "Bb4:2 D4:2",                     "F4:2 D4:2",
    "E4:2 G4:2",                      "A4:2 D4:2",
]
assert len(CTR) == BARS


def build():
    p = Piece("D", "eolien", BPM, BAR, "Sentiers Verts")
    p.add("melodie", lines(MEL, 0, bar=BAR))

    # l'arc : noires a l'intro, croches en marche, la noire revient dans la trouee
    arp = arpeggio(CH[0:3], 0, DU[0:3], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[3:16], BAR * 4, DU[3:16], 0.5, (0, 2, 1, 2), lo=53)
    arp += arpeggio(CH[16:17], BAR * 16, DU[16:17], 1.0, (0, 1, 2, 1), lo=53)
    arp += arpeggio(CH[17:], BAR * 18, DU[17:], 0.5, (0, 2, 1, 2), lo=53)
    p.add("arpege", arp)

    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("accords", bed(CH, 0, DU, lo=50, which=1))

    march = [(0, 1), (0, 1), (-1, 1), (0, 1)]
    p.add("basse", progression(CH[0:16], 0, DU[0:16], march, lo=45)
                   + progression(CH[16:17], BAR * 16, DU[16:17], [(0, 2), (-1, 2)], lo=45)
                   + progression(CH[17:], BAR * 18, DU[17:], march, lo=45))

    p.add_drums("K...K...", t0=0, length=BAR * 4)
    p.add_drums("K..HS.H.", t0=BAR * 4, length=BAR * 12)
    p.add_drums("K...S...", t0=BAR * 16, length=BAR * 2)        # la trouee
    p.add_drums("K.HHS.H.", t0=BAR * 18, length=BAR * 10)
    p.add_drums([(0, "C")], t0=BAR * 4)
    p.add_drums([(0, "C"), (0, "K")], t0=BAR * 18)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("sud.mid"))
