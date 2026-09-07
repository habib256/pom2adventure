# Clairière 21 — Bassin de cristal

**`CRYSTAL.MB.BIN` — 2 056 octets, 40,3 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **031** |
| Pages | 031 (le bassin), 077 (boire, `E ENDURANCE +3`), 394 (observer, le Lézard) |
| Case | (5,4) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | O → 047 — **cul-de-sac** |
| Arbitrage | 394 rattaché à cette clairière, comme dans `../propositions/` (`CARTOGRAPHIE.md:810-820`) |

« Au centre, un bassin luit d'une eau pure comme du cristal. Une petite plage de
sable fin borde l'un des côtés du bassin. Aucun autre chemin ne permet de
sortir. » Page 394 : « Un gros Lézard vient boire à l'eau du bassin, puis s'en
retourne d'une démarche chaloupée. »

## La pièce

| | |
| --- | --- |
| Titre | **Le Bassin de Cristal** |
| Source | composition originale, `cristal.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | limpide : la seule eau propre du Marais, et deux mesures où le jour y tombe |
| Mode | **do dorien** (do ré mi♭ fa sol **la** si♭) |
| Tempo | **156** à la noire (152 auparavant) |
| Forme | intro (4) — A (8) l'eau pure — B (8) le Lézard — A' (6) l'éclat |
| Durée | 26 mesures à 4/4 = **40,3 s** |
| Taille | **2 056 octets** (tampon de zone : 2 304, marge 248) |
| Notes | 438 de hauteur + **65 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le **bourdon de tonique immobile** et la
marche modale large. **Ce qui lui appartient :** la **sixte majeure** — le la
naturel, porté par l'accord de fa, qui revient à chaque phrase — et l'**éclat**,
l'arpège qui passe seul en doubles croches à la reprise pendant que tout le
reste garde ses valeurs.

## Ce que la révision a changé

- **un crochet bâti sur la sixte** : do - sol - **la** . sol | fa . mi♭.
  Fondamentale, quinte, la sixte majeure effleurée, la chute. Mesure 5, redit
  **une octave plus haut** mesure 9, repris mesure 21 avec sa tête portée au **mi
  naturel** — trois fois, chaque fois plus haut ;
- **une réponse** : mesures 8, 11 et 16, le chant tient sa ronde et l'arpège — la
  voix 3, à **droite** — répond le même dessin, sixte comprise, une octave plus
  bas. C'est le reflet qui répond à la chose ;
- **un rythme harmonique varié** : dix mesures changent d'accord au milieu, les
  deux mesures de l'éclat n'en changent plus du tout ;
- **la surprise, et elle est la raison d'être de la pièce** : mesures 21-22, le
  mode **bascule en majeur**. Le mi bémol devient **mi naturel**, l'accord de do
  majeur s'installe deux mesures pleines, et l'arpège passe seul en doubles
  croches. Ce n'est plus une variation de couleur, c'est le jour qui tombe dans
  l'eau. Deux mesures, pas une de plus : mesure 23 le mi bémol est revenu, et le
  bassin redevient ce qu'il était ;
- **une cadence affirmée** : mesure 20, un **sol majeur** avec son si naturel, la
  seule sensible du morceau, qui **prépare** l'éclat au lieu de le subir ;
- **un arc de densité** : intro sans batterie, A un charleston seul toutes les
  deux croches, B la démarche du Lézard, A' l'éclat plein et le charleston
  ouvert ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **sol**,
  la quinte, d'où le do du début repart naturellement.

Le tempo passe de 152 à **156**, et la pièce gagne 1,2 s.

## La batterie

Une **eau**, pas une marche. Trois états, un par section :

- **A** : un charleston seul, deux fois par mesure (`..H...H.`). Rien d'autre.
  C'est l'entrée de batterie la plus discrète des douze ;
- **B, le Lézard** : sa **démarche chaloupée**, page 394 — grosse caisse sur le
  temps **et sur la croche d'après**, caisse claire au quatrième (`K..K..S.`).
  Le boitement est dans la batterie, pas dans la mélodie, qui reste en blanches ;
- **A', l'éclat** : charleston **ouvert** au troisième temps (`K.H.O.H.`), qui
  laisse traîner le bruit sous les doubles croches de l'arpège.

65 coups, 195 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique est le procédé de la zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/21-cristal/cristal.mid --bpm 156`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, le crochet sur la sixte | A♯4..A6 | 63 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | G3..A4 | 143 | 92 % |
| 2 | **gauche** | bourdon de do (la tonique) | C2 | 7 | 100 % |
| 3 | **droite** | arpège — doubles croches à partir de la mesure 21 — et les trois réponses | A♯3..D♯5 | 137 | 92 % |
| 4 | droite | basse brève-longue | G2..A♯3 | 88 | 95 % |
| 5 | **droite** | **batterie** — 28 charleston, 22 grosse caisse, 8 caisse claire, 6 charleston ouvert, 1 cymbale | bruit | 65 | 7 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/21-cristal
python3 cristal.py
python3 ../../../midi_to_mb.py cristal.mid CRYSTAL.MB.BIN \
    --bpm 156 --max 2304 --wav CRISTAL.wav
```
