# Clairière 15 — Le pont sur la rivière Croupie

**`BRIDGE.MB.BIN` — 1 946 octets, 40,8 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **045** |
| Pages | 138 (l'arrivée), 045 (le pont suspect), 101 (le vieux pont) |
| Case | (3,3) |
| Zone de référence | `riviere` (`RIVER.MB`) |
| Sorties | N → 331, S → 303 |

**Le seul passage nord ⇄ sud du Marais** (`CARTOGRAPHIE.md` § 1) : douze
clairières d'un côté, vingt-trois de l'autre, et ce pont entre les deux. « Un
pont l'enjambe, apparemment désert. » La page 045 est le refus : « ce pont vous
paraît trop simple ; il doit sans doute dissimuler un piège quelconque. »

## La pièce

| | |
| --- | --- |
| Titre | **Le Seul Passage** |
| Source | composition originale, `pont.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | une marche, une hésitation au milieu, et on repart à l'octave |
| Mode | **si bémol dorien** (si♭ do ré♭ mi♭ fa **sol** la♭) |
| Tempo | **154** à la noire (150 auparavant) |
| Forme | intro (4) — A (8) la traversée — B (8) le soupçon — A' (6) à l'octave |
| Durée | 26 mesures à 4/4 = **40,8 s** |
| Taille | **1 946 octets** (tampon de zone : 2 304) |
| Notes | 408 de hauteur + **85 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `riviere` :** le mode dorien, l'arpège de croches,
le **bourdon sur la quinte** — fa, pas si♭.

**Ce qui lui appartient :** la zone regarde l'eau, cette pièce la traverse.
D'où la basse en **quatre noires marchées par mesure**, du début à la fin.

## La batterie

C'est la pièce des douze qui la réclamait le plus : une **marche**. Grosse
caisse au premier temps, caisse claire au troisième, charleston entre les deux —
le pas sur les planches. Sa dramaturgie est celle de la page :

- **mesure 3** : la grosse caisse entre **seule**, avant tout le reste. On
  entend quelqu'un approcher ;
- **A (5-12)** : la marche complète, `K.H.S.H.` ;
- **B (13-16)** : elle se dégarnit à `K...S...` — le marcheur ralentit ;
- **mesures 17-18** : **rien du tout**. On ne pose plus le pied ;
- **mesure 20** : roulement de toms, cymbale, et A' repart avec une grosse
  caisse doublée sur la croche (`K.HKS.H.`) : on a traversé.

85 coups, 255 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur seulement, et c'est la voix d'accords tenus qui a cédé la place — le
bourdon sur la quinte est le procédé de la zone.

## Ce que la révision a changé

- **un crochet** : si♭ - ré♭ - fa - la♭, l'accord monté marche par marche, puis
  la retombée sur la quinte. Mesure 5, mesure 9 avec l'octave au sommet, et
  mesure 21 **une octave plus haut** ;
- **une réponse** : mesures 8, 11 et 16. Celle de la mesure 16 annonce le **sol
  bémol avant** que l'harmonie ne l'ose : c'est elle qui a vu le piège ;
- **un rythme harmonique varié** : huit mesures changent d'accord au milieu, et
  la basse y garde ses quatre noires — deux pas sur chaque accord ;
- **la surprise** : mesures 17-18, un **sol bémol majeur**. Le sol naturel est la
  note qui fait le dorien ; l'abaisser d'un demi-ton éteint la pièce d'un coup.
  C'est la page 045 exactement, et la batterie s'y arrête net ;
- **deux cadences affirmées** : mesures 20 et 25, un **fa majeur** avec son la
  naturel, la seule sensible du morceau ;
- **un arc de densité** : intro nue, la caisse seule, la marche, le soupçon, le
  silence, le roulement, A' à l'octave et doublé ;
- **une fin qui prépare la boucle** : la dernière mesure retombe de si♭ à **fa**,
  la quinte du bourdon, et la marche repart.

Le tempo passe de 150 à **154** : la marche a besoin d'aller quelque part.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/15-pont/pont.mid --bpm 154`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie | G♯4..A♯6 | 65 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | D♯3..A♯4 | 119 | 93 % |
| 2 | **gauche** | bourdon de fa (la quinte) | F2 | 7 | 100 % |
| 3 | **droite** | arpège de croches, et les trois réponses | F♯3..C♯5 | 119 | 93 % |
| 4 | droite | basse, quatre noires marchées | G2..A♯3 | 98 | 94 % |
| 5 | **droite** | **batterie** — 32 charleston, 28 grosse caisse, 20 caisse claire, 4 toms, 1 cymbale | bruit | 85 | 8 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/15-pont
python3 pont.py
python3 ../../../midi_to_mb.py pont.mid BRIDGE.MB.BIN \
    --bpm 154 --max 2304 --wav PONT.wav
```
