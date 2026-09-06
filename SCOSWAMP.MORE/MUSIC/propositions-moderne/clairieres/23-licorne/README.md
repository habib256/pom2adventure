# Clairière 23 — La Licorne

**`UNICORN.MB.BIN` — 1 601 octets, 40,8 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **348** |
| Pages | 320 (la Licorne), 265 (la clairière déserte), 348 (quatre chemins) |
| Case | (1,5) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | N → 094 (brume), S → 157, E → 010 (les combats), O → 204 (les Fleurs) |
| Contenu | LICORNE blessée (11/4 en 221) ; **Corne de Licorne** (`277 G CO`) ; bénédiction (381) |

« Un animal de couleur blanche est couché au centre de la clairière. Vous pensez
d'abord qu'il s'agit d'un cheval, mais lorsqu'il tourne la tête dans votre
direction, vous reconnaissez aussitôt une LICORNE. Elle semble blessée : des
traces de griffes sont visibles sur son flanc. Elle se relève cependant et
baisse sa corne vers vous en lançant un grognement qui ressemble fort à un
défi. »

## La pièce

| | |
| --- | --- |
| Titre | **La Licorne Blessée** |
| Source | composition originale, `licorne.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | noble et blessée : elle est couchée, elle se relève, elle repart |
| Mode | **fa éolien** (fa sol la♭ si♭ do ré♭ mi♭) |
| Tempo | **142** à la noire (138 auparavant) |
| Forme | intro (4) — A (8) l'animal couché — B (8) le défi — A' (4) |
| Durée | 24 mesures à 4/4 = **40,8 s** |
| Taille | **1 601 octets** (tampon de zone : 2 304) |
| Notes | 348 de hauteur + **51 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** c'est la plus fidèle des sept pièces
`sud` — elle reprend la **marche i-VI-III-VII** de `SOUTHSWAMP.MB` (Fm-D♭-A♭-E♭,
soit Dm-B♭-F-C transposé) sur un **bourdon de tonique** qui ne bouge pas.

**Ce qui lui appartient :** la **noblesse**. La section A est en blanches, sans
une croche à la mélodie, chose qu'aucune autre des douze ne fait.

## Ce que la révision a changé

- **un crochet en blanches**, la quinte montée puis la chute : fa - do | si♭ -
  la♭. Mesure 5, redit mesure 9, repris mesure 21 — et surtout **redressé**
  mesure 13, où le même dessin revient au **rythme pointé**. C'est le même
  chant, debout : « elle se relève cependant et baisse sa corne vers vous en
  lançant un grognement qui ressemble fort à un défi ». Le crochet et le défi
  sont la même mélodie, ce qui n'était pas le cas avant ;
- **une réponse** : mesures 8, 11 et 16, le chant tient et l'arpège — la voix 3,
  à **droite** — répond le crochet une octave plus bas, **en blanches en A et
  pointé en B**, comme lui ;
- **un rythme harmonique varié** : onze mesures changent d'accord au milieu, et
  la marche i-VI-III-VII de la zone y garde sa carrure ;
- **la surprise** : mesure 19, un **fa majeur**. Toute la pièce est en fa éolien ;
  le la naturel d'une seule mesure montre l'animal en entier, blanc, avant que la
  mesure 20 ne rabatte le mode en mineur. C'est le seul moment où la Licorne
  n'est pas blessée ;
- **une cadence affirmée** : mesure 20, un **do majeur** avec son mi naturel —
  l'éolien n'en a pas, c'est bien pour cela qu'elle conclut. Elle revient
  mesure 23 ;
- **un arc de densité qui monte puis redescend**, ce qu'aucune autre des douze ne
  fait ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **do** du
  début.

Le tempo passe de 138 à **142** : le défi porte mieux, et l'animal couché reste
lent parce qu'il est écrit en blanches, pas parce que le métronome traîne.

## La batterie

Une **charge**, et seulement pendant le défi. C'est la seule des douze dont l'arc
monte puis redescend :

| mesures | ce qu'on entend |
| :---: | --- |
| 1-4 | rien |
| 5-12, l'animal couché | **un tom toutes les deux mesures**. Un sabot, pas un tempo |
| 13-20, le défi | cymbale, puis le galop plein `K.HKS.H.` sur huit mesures |
| 21-22 | `K...S...` — elle s'éloigne |
| 23 | une grosse caisse |
| 24 | **un seul tom**, et c'est tout. Elle se recouche, ou s'en va (page 265) |

51 coups, 153 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique est le procédé de la zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/23-licorne/licorne.mid --bpm 142`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie — 51 notes seulement, la plus dépouillée des douze | G♯4..F6 | 51 | 97 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | F3..G♯4 | 93 | 94 % |
| 2 | **gauche** | bourdon de fa (la tonique) | F2 | 6 | 100 % |
| 3 | **droite** | arpège, et les trois réponses | A♯3..C5 | 118 | 93 % |
| 4 | droite | basse brève-longue | G2..A♯3 | 80 | 95 % |
| 5 | **droite** | **batterie** — 19 grosse caisse, 16 charleston, 10 caisse claire, 5 toms, 1 cymbale | bruit | 51 | 5 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/23-licorne
python3 licorne.py
python3 ../../../midi_to_mb.py licorne.mid UNICORN.MB.BIN \
    --bpm 142 --max 2304 --wav LICORNE.wav
```
