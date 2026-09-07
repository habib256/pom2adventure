# Clairière 22 — Les Fleurs d'Angoisse

**`DREAD.MB.BIN` — 1 773 octets, 39,2 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **367** |
| Pages | 204 (les Fleurs), 250 (la clairière des Fleurs), 367 (deux chemins) |
| Case | (0,5) |
| Zone de référence | `danger` (`DANGER.MB`) |
| Sorties | N → 304 (les Oiseaux, sens unique), E → 265 (la Licorne) |
| Effet | `E HABILETE -1`, et −1 de plus si l'on fuit (269) |

« Le sentier s'élargit, et des fleurs colorées bordent le chemin. Mais soudain,
un frisson vous parcourt : quelque chose ne va pas. Votre Anneau de Cuivre
devient brûlant. Autour de vous, ces fleurs semblent trop belles... Leur pollen
inspire la terreur et vous sentez vos mains trembler. »

## La pièce

| | |
| --- | --- |
| Titre | **Les Fleurs d'Angoisse** |
| Source | composition originale, `angoisse.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | trop beau, puis la main qui tremble, puis le sol qui se dérobe |
| Mode | **mi phrygien** (mi **fa** sol la si do ré) |
| Tempo | **148** à la noire (144 auparavant) |
| Forme | intro (4) — A (8) les fleurs — B (8) le tremblement — A' (4) |
| Durée | 24 mesures à 4/4 = **39,2 s** |
| Taille | **1 773 octets** (tampon de zone : 2 304) |
| Notes | 368 de hauteur + **75 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `danger` :** le mode **phrygien** — fa contre mi,
le demi-ton posé juste au-dessus de la tonique — le **bourdon de tonique**, et
le crescendo obtenu **par la densité** et non par le volume, exactement comme
`DANGER.MB` : basse en blanches jusqu'à la mesure 12 puis en noires. La batterie
fait désormais le même chemin, et c'est le procédé de la zone appliqué à un
instrument que la zone n'avait pas.

## Ce que la révision a changé

- **un crochet qui finit par le motto** : mi - sol - do . si | **fa . mi**. Les
  trois premières notes sont douces, la quatrième mesure est le demi-ton. Mesure
  5, redit mesure 9, repris mesure 21 — et la dernière mesure de la pièce ne
  garde plus que sa fin, fa - mi, seule. Le crochet **et** le motto sont la même
  chose : c'est ce qui rend la pièce inquiétante dès la première phrase ;
- **une réponse** : mesures 8, 11 et 15, le chant tient sa ronde et l'arpège — la
  voix 3, à **droite** — répond le crochet une octave plus bas. La fleur répond
  à la fleur ;
- **un rythme harmonique varié** : onze mesures changent d'accord au milieu, et
  les deux mesures de fa n'en changent plus du tout ;
- **la surprise**, et c'est la pire qui puisse arriver à une pièce bâtie sur un
  bourdon immobile : **la pédale monte d'un demi-ton**. Mesures 17-18, le mi du
  bourdon devient **fa** — le demi-ton phrygien quitte la mélodie et passe dans
  le sol. Ce n'est plus une couleur, c'est le terrain qui se dérobe ; la batterie
  y tremble en doubles croches de tom, et le point d'HABILETÉ est perdu. Mesure
  19 le mi est revenu, et l'on n'est pas sûr d'avoir bien entendu ;
- **une cadence affirmée** : mesure 20, un **si majeur** avec son ré♯. Le
  phrygien n'a pas de sensible ; c'est justement pour cela qu'elle tranche ;
- **un arc de densité en cinq paliers** : rien, une caisse par mesure, deux, le
  charleston, le tremblement, le plein ;
- **une fin qui prépare la boucle** : après le motto, la dernière note est le
  **si** par lequel la pièce recommence.

Le tempo passe de 144 à **148**.

## La batterie

Un **cœur qui bat sourd et qui s'accélère** — c'est elle qui porte désormais le
crescendo par la densité, en cinq paliers exacts :

| mesures | motif | ce qu'on entend |
| :---: | --- | --- |
| 1-4 | — | rien |
| 5-8 | `K.......` | une grosse caisse par mesure |
| 9-12 | `K...K...` | deux |
| 13-16 | `K.H.K.H.` | le charleston entre |
| 17-18 | toms en **doubles croches** | le tremblement, sur la pédale de fa |
| 19-24 | `K.HKS.H.` puis `K.HKS.HS` | le plein |

75 coups, 225 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique fait le caractère de la pièce, et c'est lui qui monte au fa.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/22-angoisse/angoisse.mid --bpm 148`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, le crochet et son motto | G4..F♯6 | 70 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | E3..A4 | 76 | 95 % |
| 2 | **gauche** | bourdon — **mi, puis fa aux mesures 17-18** | E2..F2 | 7 | 100 % |
| 3 | **droite** | arpège, et les trois réponses | A3..C5 | 138 | 91 % |
| 4 | droite | basse — blanches, puis noires | G2..B3 | 77 | 95 % |
| 5 | **droite** | **batterie** — 34 grosse caisse, 20 charleston, 12 caisse claire, 8 toms, 1 cymbale | bruit | 75 | 9 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/22-angoisse
python3 angoisse.py
python3 ../../../midi_to_mb.py angoisse.mid DREAD.MB.BIN \
    --bpm 148 --max 2304 --wav ANGOISSE.wav
```
