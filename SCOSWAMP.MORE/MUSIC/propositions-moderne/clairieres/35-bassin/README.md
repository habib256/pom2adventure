# Clairière 35 — Bête du bassin (`hub` 082)

**`POOL.MB.BIN` — 2 024 octets, 45,1 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 209 | « une créature énorme à la peau brune et caoutchouteuse émerge soudain du bassin et tente de vous saisir d'un tentacule » — un magnifique Bijou Violet brille à son front |
| 082 | le duel au bord de l'eau (cette page-là passe en `+BATTLE.MB`, la surcouche) |
| 308 | la Bête morte, le Bijou Violet détaché du front, et l'unique chemin qui ramène vers l'ouest |
| 397 | la fuite : le même unique chemin |

Zone de référence : **`sud`** (`SOUTHSWAMP.MB`, *Sentiers Verts*).

## La pièce

| | |
| --- | --- |
| Titre | **Ce qui Monte du Bassin** |
| Source | composition originale, `bassin.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | quelque chose sort de l'eau à chaque mesure et n'y retourne pas |
| Mode | **fa éolien** (fa sol la♭ si♭ do ré♭ mi♭) |
| Tempo | **150** à la noire (143 auparavant) |
| Forme | intro (4) — A (8) — B (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **45,1 s** |
| Taille | **2 024 octets** (tampon de zone : 2 304) |
| Notes | 439 hauteurs + **88 coups de batterie**, **0 abandonnée** |

Le procédé de `sud` est gardé : marche i-VI-III-VII (Fm-D♭-A♭-E♭). Les deux
traits de la clairière aussi. **Ce qui monte** : la basse ne descend jamais à
l'intérieur d'une mesure — elle part de la quinte grave et remonte l'accord.
**Le Bijou Violet** : le ré♭ majeur, seul accord éclatant du morceau, porte la
note la plus haute.

**Ce que la révision change.**

* **Le crochet** : `fa · do · fa'`, la quinte puis la quarte, tout en montant.
  Énoncé quatre fois (mesures 5, 9 sur si♭, 21 sur la♭, et par l'arpège en
  réponse). Il monte, comme tout le reste.
* **Le Bijou tient une ronde entière.** Mesure 16, sur le ré♭ majeur, le chant se
  pose sur un la♭ 6 et ne bouge plus pendant quatre temps : c'est la seule fois
  de la pièce où quelque chose s'arrête. C'est ce que le joueur vient chercher.
* **La batterie sort de l'eau elle aussi** : une grosse caisse sourde et isolée
  en A — une bulle —, les toms en B, la caisse claire du tentacule en A'. Rien
  du tout dans les quatre premières mesures.
* **La réponse** : mesures 8, 12 et 16, le chant tient et l'arpège lui rend le
  crochet une octave plus bas : ce qui répond vient d'en dessous.
* **La surprise, et c'est la seule des onze à se la permettre** : mesures 25 à
  28, **le bourdon monte**. Immobile sur fa pendant vingt-quatre mesures, il
  passe à la♭, puis à si♭, et la pièce se termine sur une quarte suspendue — le
  sol se soulève, et la basse et lui s'échangent leurs voix. La boucle le ramène
  sur fa et tout recommence.
* **L'arc** : deux notes d'arpège par mesure à l'intro, huit en B et en A' ; la
  basse passe de la blanche à quatre croches montantes.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie — le Bijou Violet mesure 16 | F5..B♭6 | 71 |
| 1 | gauche | contre-chant | G3..B♭4 | 87 |
| 2 | **gauche** | bourdon de fa, qui monte à la♭ puis si♭ (mes. 25-28) | F2..C4 | 18 |
| 3 | **droite** | l'arpège, et les trois réponses | B♭3..E♭5 | 126 |
| 4 | droite | basse ascendante | G2..F4 | 137 |
| 5 | **droite** | **BATTERIE** — grosse caisse 39, caisse claire 24, tom 23, cymbale 2 | bruit | 88 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/35-bassin
python3 bassin.py
python3 ../../../midi_to_mb.py bassin.mid POOL.MB.BIN \
    --bpm 150 --max 2304 --wav BASSIN.wav
```
