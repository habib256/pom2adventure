# Clairière 30 — Clairière des grenouilles (`hub` 230)

**`FROGS.MB.BIN` — 2 246 octets, 38,5 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 053 | « le coassement de milliers de grenouilles vous accompagne » — d'immenses champignons, un petit homme corpulent assis sur l'un d'eux, la bouche anormalement large, deux énormes grenouilles pour le garder |
| 329 | le champignon lumineux, des traces de dents humaines sur le chapeau, une odeur agréable |
| 230 | la clairière silencieuse : les Grenouilles Géantes mortes, le Maître disparu |

Zone de référence : **`sud`** (`SOUTHSWAMP.MB`, *Sentiers Verts*).

## La pièce

| | |
| --- | --- |
| Titre | **Le Bal des Mares** |
| Source | composition originale, `grenouilles.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | la seule clairière comique des onze, et la seule où le Marais danse |
| Mode | **sol éolien** (sol la si♭ do ré mi♭ fa) |
| Tempo | **176** à la noire (166 auparavant : on danse) |
| Forme | intro (4) — A (8) — B (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **38,5 s** |
| Taille | **2 246 octets** (tampon de zone : 2 304) — la plus grosse des onze |
| Notes | 459 hauteurs + **115 coups de batterie**, **0 abandonnée** |

Le procédé de `sud` est gardé tel quel : la marche i-VI-III-VII (Gm-E♭-B♭-F)
posée sur un bourdon de sol qui ne bouge pas. Le caractère aussi : la mélodie
**saute** l'octave en croches et retombe lourdement, la basse alterne
fondamentale et quinte grave. Le petit homme est corpulent : ça rebondit, ça ne
vole pas.

**Ce que la révision change.**

* **C'est la pièce à batterie du lot.** Le bal a enfin son tambourin :
  charleston sur les croches — c'est le coassement —, grosse caisse au premier
  temps, caisse claire au troisième, charleston ouvert en A'. C'est la seule des
  onze dont la batterie ne se retire jamais une fois entrée.
* **Le crochet** : le saut d'octave `sol · sol' | ré · si♭`. Énoncé quatre fois
  (mesures 5, 9 renversé vers le bas, 21 à l'octave, et à la cadence).
* **Une vraie partie B** (mesures 13-20) : do mineur et fa, registre haut, et le
  chant qui ne redescend plus sous le do 6.
* **La réponse** : mesures 8, 12 et 16, le chant tient une ronde et l'arpège lui
  répond par le même saut d'octave — la grenouille d'en face.
* **La surprise** : mesures 13 et 25, **sol majeur**. Le si bécarre n'est pas
  dans le mode ; c'est la bouche anormalement large du petit homme, un sourire
  qui ne devrait pas être là.
* **L'arc** : deux notes d'arpège par mesure et pas un coup à l'intro ; huit
  notes, le charleston ouvert et la basse en croches en A'.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie, qui saute l'octave | D5..G6 | 82 |
| 1 | gauche | contre-chant | D3..B♭4 | 104 |
| 2 | **gauche** | bourdon de sol, une seule note tenue | G2 | 1 |
| 3 | **droite** | l'arpège, et les trois réponses | B♭3..D5 | 149 |
| 4 | droite | basse — fondamentale et quinte grave | F2..D4 | 123 |
| 5 | **droite** | **BATTERIE** — charleston fermé 57, grosse caisse 25, caisse claire 24, charleston ouvert 7, cymbale 2 | bruit | 115 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/30-grenouilles
python3 grenouilles.py
python3 ../../../midi_to_mb.py grenouilles.mid FROGS.MB.BIN \
    --bpm 176 --max 2304 --wav GRENOUILLES.wav
```
