# Clairière 13 — La Rivière Croupie

**`STAGNANT.MB.BIN` — 1 595 octets, 43,9 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **295** |
| Pages | 295 |
| Case | (1,3) |
| Zone de référence | `riviere` (`RIVER.MB`) |
| Sorties | E → 183 (falaise), S → 094 (brume fétide) |

La berge. « La rive opposée est à 200 mètres de distance au moins et le cours
d'eau est infesté de crocodiles et d'autres créatures tout aussi peu
accueillantes. » On ne traverse pas ici ; on regarde.

## La pièce

| | |
| --- | --- |
| Titre | **La Berge aux Crocodiles** |
| Source | composition originale, `croupie.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | large et lourde : une eau qui ne mène nulle part, et quelque chose dessous |
| Mode | **sol dorien** (sol la si♭ do ré **mi** fa) |
| Tempo | **132** à la noire |
| Forme | intro (4) — A (8) — B (8) — A' (4) |
| Durée | 24 mesures à 4/4 = **43,9 s** |
| Taille | **1 595 octets** (tampon de zone : 2 304) |
| Notes | 354 de hauteur + **45 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `riviere` :** le mode dorien, l'arpège de croches
qui ne s'arrête jamais, et surtout le **bourdon sur la quinte** — ré, pas sol.
C'est le procédé identifiable de la zone : la tonique n'est jamais soutenue,
donc rien ne se pose, donc tout coule. La batterie n'y touche pas.

**Ce qui lui appartient :** la basse en figure brève-longue, une mâchoire qui se
referme sous la surface, et le **mi naturel** du mode dorien comme unique reflet
de lumière sur une eau boueuse.

## Ce que la révision a changé

- **un crochet**, deux mesures : `ré sol si♭ . la | sol . ré`, l'accord de sol
  mineur monté d'un trait et retombé d'un demi-pas. Mesure 5, mesure 9 (il monte
  au do), mesure 21 tel quel. Trois énoncés ;
- **une réponse** : mesures 7, 11 et 19, le chant tient une note et l'arpège —
  la voix 3, à **droite** — répond le crochet une octave plus bas. La question
  est à gauche, la réponse à droite ;
- **un rythme harmonique qui bouge** : six mesures changent d'accord au milieu
  (`F|C`, `Dm|C`, `C|Dm`, `B♭|C`, `F|C`), et la basse y marche en deux pas au
  lieu de sa brève-longue ;
- **la surprise** : mesures 17-18, un **mi♭ majeur** — l'accord étranger au
  dorien, celui qui éteint le mi naturel — posé sur le bourdon de ré dont il
  frotte le demi-ton. La batterie s'y tait complètement : le cœur s'arrête deux
  mesures ;
- **une cadence affirmée** : mesure 20, un **ré majeur** avec son fa♯, la seule
  sensible du morceau, qui rejette dans le sol mineur de la reprise ;
- **un arc de densité** : intro en blanches d'arpège et sans batterie, A en
  croches avec le cœur lent, B qui se resserre, deux mesures muettes, roulement
  de toms, A' plein ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **ré**
  du début — la note même par laquelle la pièce recommence. Le fondu automatique
  (0,9 s) fait la couture.

## La batterie

Le **cœur sourd du danger**, pas une marche : grosse caisse au premier temps, un
tom au troisième une mesure sur deux, une caisse claire quand B se resserre, une
cymbale à la reprise. 45 coups en tout — 135 octets — pour une pièce qui doit
rester large.

Elle prend la **voix 5, à droite** : il ne reste donc que **cinq** parties de
hauteur. C'est la voix d'accords tenus qui a cédé la place, pas le bourdon : le
bourdon sur la quinte est le procédé de la zone, on ne le retire pas.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/13-croupie/croupie.mid --bpm 132`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, valeurs longues | C5..F6 | 59 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | F3..A4 | 96 | 94 % |
| 2 | **gauche** | bourdon de ré (la quinte) | D2 | 6 | 100 % |
| 3 | **droite** | arpège de croches, et les trois réponses | G3..D5 | 117 | 93 % |
| 4 | droite | basse brève-longue | G2..A♯3 | 76 | 95 % |
| 5 | **droite** | **batterie** — 28 grosse caisse, 8 toms, 8 caisse claire, 1 cymbale | bruit | 45 | 6 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/13-croupie
python3 croupie.py
python3 ../../../midi_to_mb.py croupie.mid STAGNANT.MB.BIN \
    --bpm 132 --max 2304 --wav CROUPIE.wav
```
