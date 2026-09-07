# Clairière 25 — Herbe à Pinces (`hub` 187)

**`PINCERS.MB.BIN` — 2 184 octets, 43,9 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 388 | l'entrée : une agréable clairière envahie d'herbes — puis « des pinces apparaissent aux extrémités de ses tiges » |
| 263 | le retour : des taches brunes là où les lianes se sont refermées |
| 033 | la traversée en courant : « l'herbe pousse plus vite encore » |
| 187 | le carrefour à trois chemins, sud, est le long de la rivière, ouest |

Zone de référence : **`danger`** (`DANGER.MB`, *Ce qui Attend Sous l'Eau*).

## La pièce

| | |
| --- | --- |
| Titre | **L'Herbe qui Serre** |
| Source | composition originale, `pinces.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | ça pousse plus vite que vous : la plus rapide des onze clairières, et la seule dont l'accompagnement claque au lieu de couler |
| Mode | **mi phrygien** (mi **fa** sol la si do ré) |
| Tempo | **176** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (8) — A' à l'octave (8) — coda (4) |
| Durée | 32 mesures à 4/4 = **43,9 s** |
| Taille | **2 184 octets** (tampon de zone : 2 304) |
| Notes | 469 hauteurs + **75 coups de batterie**, **0 abandonnée** |

Ce qui la rattache à `danger` n'a pas bougé : le **demi-ton phrygien** fa–mi et
le bourdon de mi. Ce qui n'appartient qu'à elle non plus : la **pince**, cet
arpège qui joue trois croches puis se tait à la quatrième (`0, 2, 1, silence`).

**Ce que la révision change.**

* **Le crochet.** `mi fa mi | si` — la seconde mineure qui mord, puis le saut à
  la quinte. Il est énoncé quatre fois (mesures 5, 10, 21, 27) et nulle part
  ailleurs ; le reste de la mélodie ne fait que tourner autour.
* **La batterie tombe dans le trou.** La caisse claire frappe exactement sur les
  croches 4 et 8, là où l'arpège se tait : c'est la pince qui se referme. Rien
  avant la mesure 5, rien pendant la mesure 19, rien à la dernière mesure.
* **La réponse.** Quatre fois (mesures 8, 12, 16, 28) le chant tient une ronde
  et c'est l'arpège, à droite, qui répond à sa place, avec le rythme du crochet
  deux octaves plus bas.
* **Le rythme harmonique varie** : une mesure sur trois porte deux accords, la
  grille n'est plus un accord par mesure d'un bout à l'autre.
* **La surprise** : mesures 19-20, la pédale quitte le mi et se pose un demi-ton
  plus haut, sur **fa**. Le demi-ton phrygien passe enfin dans la basse, la
  batterie se tait, et tout retombe sur mi à la mesure 21.
* **L'arc** : deux notes d'arpège par mesure à l'intro, six dès la mesure 5,
  une seule à la dernière — la boucle repart à nu.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | E5..G6 | 88 |
| 1 | gauche | contre-chant | G2..G4 | 76 |
| 2 | **gauche** | bourdon de mi, puis de fa (mes. 19-20) | E2..F2 | 3 |
| 3 | **droite** | l'arpège à pinces, et les quatre réponses | G2..E5 | 190 |
| 4 | droite | basse | G2..A3 | 112 |
| 5 | **droite** | **BATTERIE** — caisse claire 49, grosse caisse 25, cymbale 1 | bruit | 75 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 62/38.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/25-pinces
python3 pinces.py
python3 ../../../midi_to_mb.py pinces.mid PINCERS.MB.BIN \
    --bpm 176 --max 2304 --wav PINCES.wav
```
