# Zone `riviere` — la rivière Croupie et son pont

**`RIVER.MB.BIN` — 1 964 octets, 54,0 s, boucle.** Tampon de zone (2 304 o), 340 octets de marge. **Sans batterie** : six voix de hauteur.

## Ce que la zone couvre

| # | `hub` | Titre | (x,y) | Pages |
| ---: | ---: | --- | :---: | --- |
| 13 | 295 | La Rivière Croupie | (1,3) | 295 |
| 14 | 183 | Sommet de la falaise | (2,3) | 183 |
| **15** | **045** | **Le pont sur la rivière Croupie** | (3,3) | 138, 45, 101 |
| 31 | 044 | La rivière profonde | (1,7) | 90, 44, 254, 370 |

Quatre clairières seulement, mais le pont est **le seul passage** entre les
douze clairières du nord et les vingt-trois du sud (`CARTOGRAPHIE.md` § 1). Une
zone de quatre pages qui porte le seuil du jeu mérite sa musique.

## La pièce

| | |
| --- | --- |
| Titre | **Le Pont sur la Croupie** |
| Source | composition originale, `riviere.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | l'eau ne frappe pas : aucune percussion, un arpège de croches qui ne s'arrête jamais, une mélodie en blanches au-dessus |
| Mode | **la dorien** (la si do ré mi **fa♯** sol) |
| Tempo | **125** à la noire |
| Forme | intro (4) — A, crochet énoncé deux fois (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **54,0 s** — la plus longue boucle du dossier |
| Taille | **1 964 octets** — 487 notes, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** La montée la-do-mi et la descente ré-si-sol, mesures 5-6, **reprises mesures 9-10** sur do majeur : la même montée, éclairée.
- **Question et réponse.** Mesures 7, 12 et 24 : la mélodie tient une ronde en haut, le contre-chant répond en croches.
- **Surprise — la pédale bouge.** Le bourdon est sur **mi** (la quinte) pendant tout le A ; il descend sur **ré** aux mesures 13 à 20 et l'harmonie entière bascule d'un cran, puis remonte sur mi mesure 21 comme si de rien n'était. C'est le seul endroit du dossier où la pédale change de note, et c'est la traversée du pont.
- **Rythme harmonique.** Huit temps sur la mineur à l'intro, quatre en A, deux à la mesure 11, huit sur le la mineur qui referme le B.
- **Arc.** L'arpège passe en **doubles croches** aux mesures 15-16, au plus fort du courant, puis revient aux croches.
- Le ré majeur du mode dorien (mesures 8, 12, 24) reste la seule lumière franche.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie, en valeurs longues | D5..A6 | 66 |
| 1 | gauche | médiane (accords tenus) | C4..D5 | 79 |
| 2 | **gauche** | basse, blanche puis deux noires | G2..B3 | 82 |
| 3 | **droite** | **contre-chant — la voix qui répond** | D4..D5 | 96 |
| 4 | droite | arpège, le courant | F♯3..G4 | 157 |
| 5 | **droite** | **bourdon — mi, puis ré, puis mi** | D2..E2 | 7 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/riviere
python3 riviere.py
python3 ../../midi_to_mb.py riviere.mid RIVER.MB.BIN \
    --bpm 125 --max 2304 --wav RIVIERE.wav
```
