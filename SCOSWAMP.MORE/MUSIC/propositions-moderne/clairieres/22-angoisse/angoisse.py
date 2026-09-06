#!/usr/bin/env python3
"""« Les Fleurs d'Angoisse » — clairiere 22. Mi phrygien, 148.

Variation dans la couleur `danger` : le mode **phrygien**, donc le demi-ton pose
juste au-dessus de la tonique — ici fa contre mi — le **bourdon de tonique** qui
ne bouge pas, et le crescendo obtenu **par la densite** et non par le volume,
comme dans `DANGER.MB` : la basse passe en blanches jusqu'a la mesure 12, en
noires ensuite, et la batterie fait exactement le meme chemin.

Ce que la clairiere ajoute est le contraste de la page 204. Les fleurs sont
belles ; puis « votre Anneau de Cuivre devient brulant ».

Ce que la revision ajoute :

- un **crochet** de deux mesures qui **finit par le motto** : mi - sol - do . si
  | **fa . mi**. Les trois premieres notes sont douces, la quatrieme mesure est
  le demi-ton. Enonce mesure 5, redit mesure 9, repris mesure 21 — et la
  derniere mesure de la piece ne garde plus que sa fin, fa - mi, seule. Le
  crochet et le motto sont la meme chose : c'est ce qui rend la piece
  inquietante des la premiere phrase ;
- une **reponse** : mesures 8, 11 et 15, le chant tient sa ronde et l'arpege — la
  voix 3, a droite — repond le crochet une octave plus bas. La fleur repond a la
  fleur ;
- un **rythme harmonique** varie : onze mesures changent d'accord au milieu, et
  les deux mesures de fa n'en changent plus du tout ;
- la **surprise**, et c'est la pire qui puisse arriver a une piece batie sur un
  bourdon immobile : **la pedale monte d'un demi-ton**. Mesures 17-18, le mi du
  bourdon devient **fa** — le demi-ton phrygien quitte la melodie et passe dans
  le sol. Ce n'est plus une couleur, c'est le terrain qui se derobe ; la batterie
  y tremble en doubles croches de tom, et le point d'HABILETE est perdu. Mesure
  19 le mi est revenu, et l'on n'est pas sur d'avoir bien entendu ;
- une **cadence** : mesure 20, un **si majeur** avec son re diese. Le phrygien
  n'a pas de sensible ; c'est justement pour cela qu'elle tranche ;
- un **arc de densite** en cinq paliers : rien, une caisse par mesure, deux, le
  charleston, le tremblement, le plein ;
- une **fin qui prepare la boucle** : apres le motto, la derniere note est le
  **si** par lequel la piece recommence.

**La batterie** est un coeur qui bat sourd et qui s'accelere : c'est elle qui
porte le crescendo par la densite, le meme procede que la zone `danger`
applique a un instrument que la zone n'avait pas. Elle prend la voix 5 a droite ;
il ne reste que cinq parties de hauteur, et c'est la voix d'accords tenus qui a
cede la place — le bourdon de tonique fait le caractere de la piece.

24 mesures a 4/4, 38,9 s. Forme intro(4) - A(8) les fleurs - B(8) le
tremblement - A'(4).

    python3 angoisse.py && python3 ../../../midi_to_mb.py angoisse.mid \\
        DREAD.MB.BIN --bpm 148 --max 2304 --wav ANGOISSE.wav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from compose import *                                          # noqa: E402,F403

BPM, BAR, BARS = 148, 4, 24
LEN = BAR * BARS
CUT = 12                                   # la mesure ou la basse passe en noires

# une entree par mesure ; « C|Am » change d'accord au milieu de la mesure
CHORDS = (["Em", "Em", "F", "F"]
          + ["Em", "C|Am", "Am", "F|Em", "Em", "G|F", "F|Em", "Em"]
          + ["Am", "F|C", "C|G", "Am|Dm", "F", "F", "Dm|Em", "B"]
          + ["Em", "C|Am", "F|Em", "Em"])
assert len(CHORDS) == BARS
CH2 = [c for b in CHORDS for c in (b.split("|") * 2)[:2]]      # par demi-mesure

MEL = [
    "B4:4",                           "B4:2 E5:2",
    "C5:2 F5:2",                      "F5:2 E5:2",
    "E5:1 G5:1 C6:1.5 B5:.5",         "F5:2 E5:2",              # le crochet, et son motto
    "A5:1 C6:1 E6:2",                 "F6:4",                   # 8 : la reponse
    "E5:1 G5:1 C6:1.5 B5:.5",         "D6:2 B5:2",              # le crochet, redit
    "C6:4",                           "G5:1 E5:1 B4:2",         # 11 : la reponse
    "E6:.25 F6:.25 E6:.5 C6:1 A5:2",  "F6:.25 E6:.25 F6:.5 A5:1 C6:2",
    "G5:4",                           "D6:.25 C6:.25 B5:.5 G5:1 D6:2",  # 15 : la reponse
    "F6:.25 E6:.25 F6:.5 A5:1 C6:2",  "F6:2 C6:2",              # 17-18 : la pedale monte au fa
    "D6:1 A5:1 F5:2",                 "D#6:1 F#6:1 B5:2",       # 20 : la cadence
    "E5:1 G5:1 C6:1.5 B5:.5",         "F5:2 E5:2",              # le crochet, une derniere fois
    "F6:1 C6:1 A5:2",                 "F5:.5 E5:.5 E5:2 B4:1",  # 24 : le motto, puis le si
]
assert len(MEL) == BARS

CTR = [
    "E4:2 G3:2",                      "B3:2 E4:2",
    "F4:2 A3:2",                      "C4:2 A3:2",
    "E4:2 B3:2",                      "C4:2 A3:2",
    "A3:2 E4:2",                      "F4:2 E4:2",
    "B3:2 G3:2",                      "D4:2 C4:2",
    "A3:2 B3:2",                      "G3:2 E4:2",
    "A3:2 C4:2",                      "F4:2 E4:2",
    "G3:2 B3:2",                      "C4:2 D4:2",
    "A3:2 C4:2",                      "F4:2 A3:2",
    "F4:2 E4:2",                      "D#4:2 F#4:2",
    "E4:2 B3:2",                      "G3:2 A3:2",
    "C4:2 B3:2",                      "G3:2 E4:2",
]
assert len(CTR) == BARS

# la voix 3 repond au chant : le crochet, une octave plus bas
REPONSES = {
    7:  "E4:1 G4:1 C5:1.5 B4:.5",
    10: "F4:1 A4:1 C5:1.5 B4:.5",
    14: "E4:1 G4:1 C5:1.5 B4:.5",
}


def accompagnement():
    """L'arpege marche en noires tant que les fleurs sont belles, puis en
    croches — sauf aux mesures ou il repond au chant."""
    out = []
    for i in range(BARS):
        t = i * BAR
        if i in REPONSES:
            out += line(REPONSES[i], t)
        elif i < 4:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 1.0, (0, 2), lo=54)
        else:
            out += arpeggio(CH2[2 * i:2 * i + 2], t, BAR / 2, 0.5,
                            (0, 1, 2, 1), lo=54)
    return out


def basse():
    """Le crescendo est fait par la densite : blanches, puis noires."""
    out = []
    for i, b in enumerate(CHORDS):
        t = i * BAR
        if "|" in b:
            out += progression(b.split("|"), t, BAR / 2, [(0, 1), (-1, 1)], lo=48)
        elif i < CUT:
            out += progression([b], t, BAR, [(0, 2), (-1, 2)], lo=48)
        else:
            out += progression([b], t, BAR,
                               [(0, 1), (0, 1), (-1, 1), (0, 1)], lo=48)
    return out


def bourdon():
    """La tonique, immobile — sauf mesures 17-18, ou elle monte au fa."""
    return (pedal(midi("E2"), 0, BAR * 16, retrig=BAR * 4)
            + pedal(midi("F2"), BAR * 16, BAR * 2, retrig=BAR * 2)
            + pedal(midi("E2"), BAR * 18, BAR * 6, retrig=BAR * 3))


def build():
    p = Piece("E", "phrygien", BPM, BAR, "Les Fleurs d'Angoisse")
    p.add("melodie", lines(MEL, 0, bar=BAR))
    p.add("arpege", accompagnement())
    p.add("contre-chant", lines(CTR, 0, bar=BAR))
    p.add("basse", basse())
    p.add("bourdon", bourdon())

    # le coeur bat, puis bat plus vite : le crescendo est dans la densite
    p.add_drums("K.......", t0=BAR * 4, length=BAR * 4)
    p.add_drums("K...K...", t0=BAR * 8, length=BAR * 4)
    p.add_drums("K.H.K.H.", t0=BAR * 12, length=BAR * 4)
    for m in (16, 17):                     # le tremblement, sur la pedale de fa
        p.add_drums([(0, "K"), (2, "T"), (2.25, "T"), (2.5, "T"), (2.75, "T"),
                     (3, "S")], t0=BAR * m)
    p.add_drums("K.HKS.H.", t0=BAR * 18, length=BAR * 2)
    p.add_drums("K.HKS.HS", t0=BAR * 20, length=BAR * 4)
    p.add_drums([(0, "C", 7)], t0=BAR * 20)
    return p


if __name__ == "__main__":
    build().write(Path(__file__).with_name("angoisse.mid"))
