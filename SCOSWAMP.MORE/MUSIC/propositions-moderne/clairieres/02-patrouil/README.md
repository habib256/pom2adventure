# Clairière 2 — Le Patrouilleur vert (`hub` 234, case 2,0)

**`PATROLLER.MB.BIN` — 2 185 octets, 41,5 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 170 | Le Patrouilleur vert | la brume se lève, l'homme en vert sur son rocher, la question |
| 363 | Retour au Patrouilleur | ami, mort, ou fui ? |
| 234 | Deux sentiers | l'est ou le sud |

La page **363** appartient à cette clairière et non à la 3
(`CARTOGRAPHIE.md:810-820`), comme dans les deux dossiers de propositions.

## La pièce

| | |
| --- | --- |
| Titre | **La Question du Patrouilleur** |
| Source | composition originale, `patrouil.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on est interrogé, pas suivi. « Es-tu au service du Bien ou du Mal ? » — une figure d'appel qui revient toujours, et jamais au même endroit de la mesure |
| Mode | **la mineur éolien** (la si do ré mi fa sol) |
| Tempo | **162** à la noire (auparavant 156) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **41,5 s** |
| Taille | **2 185 octets** (marge 119 sur le tampon de zone) |
| Notes | 417 de hauteur + **94 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures qui cite la ronde elle-même : `la mi do' si /
  la mi sol`. Énoncé quatre fois, deux au A, deux au A' ;
- **une réponse** aux mesures 8, 12, 20 et 28 : le chant tient, la ronde — voix
  3, à droite — répond à sa place. C'est la question du patrouilleur et la
  réponse qu'on lui donne ;
- **la ronde change de vitesse** : elle tourne en **noires** dans l'intro et
  dans tout le B — trois noires contre quatre temps, l'hémiole s'entend — et en
  **croches** au A et au A'. C'est l'arc de densité du morceau, et la raison
  pour laquelle le B respire au lieu d'ajouter ;
- **la surprise** : mesure 19, l'accord de **mi majeur**, un sol dièse qui
  n'existe pas dans le mode. La pique se lève. Puis mesure 20, **un temps de
  silence général**, la caisse claire seule, et l'on repart ensemble ;
- **le rythme harmonique varie** : grille à la demi-mesure, un accord par mesure
  dans la brume, deux dès que la ronde s'engage ;
- **le tempo monte de 156 à 162**.

## La batterie

Une **marche de patrouille**, et elle est écrite de travers exprès : grosse
caisse et caisse claire d'aplomb sur les temps, mais le **charleston bat toutes
les trois croches**, sur la même grille que la ronde. Les deux décalages ne
retombent ensemble qu'une mesure sur trois. Rien dans la brume, rien pendant les
noires du B sauf la grosse caisse, tout au A'. Le bourdon de mi a cédé la place.

## Ce qui la relie à `nord`, et ce qui l'en sépare

Le procédé de la zone est l'**ostinato fixe** : quelques notes qui ne changent
jamais pendant que les accords bougent dessous. Celui-ci ne change jamais de
notes non plus — **la - mi - do**, une quarte descendante puis une sixte — mais
sa cellule fait **trois pas** dans une mesure à quatre temps. Elle retombe donc
chaque fois sur un temps différent, et ne revient à sa place qu'une mesure sur
trois. L'homme en vert est toujours là, jamais au même endroit du chemin.

## Les six voix, mesurées

`python3 ../../verifier.py patrouil.mid --bpm 162`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | E5..A6 | 80 |
| 1 | gauche | le contre-chant, détaché | E3..C5 | 58 |
| 2 | **gauche** | la basse, sèche, jamais tenue | G2..A3 | 84 |
| 3 | **droite** | **la ronde**, en entier, et les réponses | E4..E5 | 151 |
| 4 | droite | les accords tenus | E3..C5 | 44 |
| 5 | **droite** | **LA BATTERIE** — charleston fermé 44, caisse claire 26, grosse caisse 23, cymbale 1 | bruit | 94 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

151 des 417 notes de hauteur sont dans une seule voix, à droite : la ronde
occupe toute une puce. C'est ce qui rend la clairière reconnaissable en deux
secondes, exactement comme l'ostinato de la zone.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/02-patrouil
python3 patrouil.py
python3 ../../../midi_to_mb.py patrouil.mid PATROLLER.MB.BIN \
    --bpm 162 --max 2304 --wav PATROUIL.wav
```
