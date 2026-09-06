# Clairière 32 — Clairière du Maître des Loups (`hub` 314)

**`WOLFMASTER.MB.BIN` — 2 182 octets, 45,9 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 398 | une petite maison en rondins, un Loup debout à côté ; un homme robuste vêtu comme un Garde Forestier, l'Amulette d'Argent en forme de loup — « il vous répond avec mauvaise humeur en vous ordonnant de passer votre chemin » |
| 239 | la maison fermée à double tour, aucun signe de vie |
| 314 | deux directions, et un énorme escargot qui passe doucement devant vous |

Zone de référence : **`sud`** (`SOUTHSWAMP.MB`, *Sentiers Verts*).

## La pièce

| | |
| --- | --- |
| Titre | **Le Cor du Maître** |
| Source | composition originale, `maitreloups.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | un cor, un homme qui garde son bois, et deux loups debout à côté de lui |
| Mode | **mi éolien** (mi fa♯ sol la si do ré) |
| Tempo | **150** à la noire (143 auparavant : la meute part) |
| Forme | intro (4) — A (8) — B (7) — mesure longue (1) — A' (8) |
| Durée | 28 mesures à 4/4 **plus deux temps** = **45,9 s** |
| Taille | **2 182 octets** (tampon de zone : 2 304) |
| Notes | 427 hauteurs + **119 coups de batterie**, **0 abandonnée** |

Le procédé de `sud` est gardé : marche i-VI-III-VII (Em-C-G-D) sur un bourdon de
mi immobile. Le caractère aussi : la mélodie est faite de quintes et de quartes
à vide, et l'arpège sonne fondamentale-quinte sans **aucune** tierce — un
pavillon de cuivre n'en donne pas.

**Ce que la révision change.**

* **Le galop.** La batterie est écrite au **quart de temps** : `ta-ta-TAM`,
  trois coups groupés, la seule des onze à sortir de la grille de croches. Elle
  entre au trot mesure 5, passe au galop plein en B, et c'est elle — pas le
  volume — qui fait monter la chasse.
* **Le crochet** : l'appel `mi · si · mi'`, quinte puis quarte, tout ouvert.
  Énoncé quatre fois (mesures 5, 9 sur la, 21 à l'octave, 24).
* **Une vraie partie B** (mesures 13-19) : le chant monte au sol 6 et l'harmonie
  passe par si mineur et ré, les deux degrés que A n'a jamais.
* **La réponse** : mesures 8, 12 et 16, le chant tient une ronde et l'arpège lui
  renvoie l'appel — c'est le second cor, de l'autre côté du bois, à droite.
* **La surprise** : la **mesure 20 a six temps**. Le Maître lève la main, le cor
  tient, la batterie s'arrête net, et la meute attend deux temps de trop avant
  que la reprise ne parte.
* **L'arc** : intro sans batterie et arpège en rondes ; A' au galop double avec
  la basse pointée, et une dernière mesure où il ne reste qu'un pas.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie — le cor, quintes et quartes à vide | E5..B6 | 70 |
| 1 | gauche | contre-chant | D3..A4 | 81 |
| 2 | **gauche** | bourdon de mi, une seule note tenue | E2 | 1 |
| 3 | **droite** | l'arpège sans tierce, et les trois réponses | A3..E5 | 131 |
| 4 | droite | basse pointée | E2..G3 | 144 |
| 5 | **droite** | **BATTERIE** — le galop : grosse caisse 87, caisse claire 30, cymbale 2 | bruit | 119 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 59/41.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/32-maitreloups
python3 maitreloups.py
python3 ../../../midi_to_mb.py maitreloups.mid WOLFMASTER.MB.BIN \
    --bpm 150 --max 2304 --wav MAITRELOUPS.wav
```
