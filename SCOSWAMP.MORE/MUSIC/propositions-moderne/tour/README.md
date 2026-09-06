# Zone `tour` — la tour de Stratagus

**`TOWER.MB.BIN` — 1 045 octets, 46,4 s, boucle.** Tampon de zone (2 304 o), 1 259 octets de marge — la pièce la plus légère du dossier.

## Ce que la zone couvre

Aucune clairière : quatorze pages hors carte, plus la victoire amère.

| Ensemble | Pages |
| --- | --- |
| Tour de Stratagus | 226, 225, 402, **124**, 222, 297, 298, 327, 349, 372, 373, 375, 401 |
| Victoire amère de Stratagus | 358 |

Les pages **124**, **222**, **225**, **402** portent aussi une ligne de combat,
et **297**, **372**, **375**, **401** sont aussi des pages de mort : la
surcouche `MU +BATTLE.MB` ou `MU +DEATH.MB` remplace le thème pour une page sans
effacer la mémoire de la zone, qui revient à la page suivante.

## La pièce

| | |
| --- | --- |
| Titre | **La Tour de Stratagus** |
| Source | composition originale, `tour.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | marche lente et haute. Presque pas de batterie : une grosse caisse toutes les deux mesures, un pas dans un escalier de pierre, pas un rythme |
| Mode | **sol mineur harmonique** (sol la si♭ do ré mi♭ **fa♯**) |
| Tempo | **125** à la noire, écrit en blanches et en noires — le pouls réel est à 62 |
| Forme | intro (4) — A, crochet énoncé deux fois (8) — B (8) — coda (4) |
| Durée | 24 mesures à 4/4 = **46,4 s** |
| Taille | **1 045 octets** — 253 notes de hauteur, 18 coups, 0 abandonnée |

## Ce que la révision a apporté

- **Surprise — la pédale monte d'un demi-ton.** Bourdon sur **ré** (la dominante, la tour n'est jamais posée) pendant tout le A, sur **mi bémol** aux mesures 13 à 20 sous une harmonie qui ne bouge pas, puis retour sur ré mesure 21 pour que la coda puisse cadencer. Rien n'a changé et tout a changé.
- **Crochet.** La quinte montante sol-ré et la descente mi bémol-ré-do, mesures 5-6, **reprises mesures 9-10** sur mi bémol au lieu de do mineur.
- **Question et réponse.** Mesures 7, 12 et 23.
- **Batterie.** Douze coups de grosse caisse en 24 mesures, une cymbale à chaque départ de partie, et **trois toms qui montent** à la mesure 20 avant la coda. Rien d'autre.
- **Ce qui a cédé sa voix.** La voix d'accords tenus ; le bourdon reste, parce que c'est lui qui fait le morceau.
- La seconde augmentée mi♭-fa♯ du mineur harmonique est la seule sensible du dossier : **c'est la magie, et elle est écrite, pas suggérée.**

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie, en valeurs longues | D5..A6 | 54 |
| 1 | gauche | arpège à la noire | D3..G4 | 83 |
| 2 | **gauche** | **bourdon — ré, puis mi bémol, puis ré** | D2..D♯2 | 6 |
| 3 | **droite** | **contre-chant — la voix qui répond** | A♯3..C5 | 62 |
| 4 | droite | basse, deux blanches par mesure | F2..G3 | 48 |
| 5 | **droite** | **batterie** — grosse caisse 12, cymbale 3, tom 3 | bruit | 18 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/tour
python3 tour.py
python3 ../../midi_to_mb.py tour.mid TOWER.MB.BIN \
    --bpm 125 --max 2304 --wav TOUR.wav
```
