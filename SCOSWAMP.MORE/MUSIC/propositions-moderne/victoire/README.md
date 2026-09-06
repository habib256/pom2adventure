# Zone `victoire` — les deux fins gagnantes

**`VICTORY.MB.BIN` — 1 265 octets, 25,9 s, `--no-loop`.**

Surcouche : tampon de 1 280 octets, 15 de marge. Toute retouche doit être reconvertie avant d'être crue.

## Ce que la zone couvre

| Pages | Titre |
| --- | --- |
| 158 | victoire |
| 175 | victoire |

La victoire amère de Stratagus (page **358**) garde le thème de la `tour` :
elle n'en est pas une.

Comme `mort`, la pièce se joue **une seule fois** (`--no-loop`) et laisse le
silence.

## La pièce

| | |
| --- | --- |
| Titre | **Par la Trouée de Ciel** |
| Source | composition originale, `victoire.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | large, pas militaire. La seule batterie de fanfare du dossier : caisse claire sur les temps faibles, cymbale à chaque départ de phrase, **charleston ouvert sur la dernière mesure** |
| Mode | **ré mixolydien** (ré mi fa♯ sol la si **do**) — la seule pièce en majeur du dossier |
| Tempo | **150** à la noire |
| Forme | quatre phrases de quatre mesures ; le crochet monte trois fois, chaque fois d'un cran |
| Durée | 16 mesures à 4/4 = **25,9 s** |
| Taille | **1 265 octets** — 255 notes de hauteur, 65 coups, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** Ré-fa♯-la puis le ré à l'octave, mesure 1 ; **repris mesure 5** une quarte plus haut sur sol ; une troisième fois mesure 13 tout en haut. La pièce monte trois fois et ne redescend qu'à la cadence.
- **Question et réponse.** Mesures 4 et 12 : la mélodie tient, le contre-chant répond en croches montantes.
- **Surprise.** Mesure 9, un **si mineur** là où l'oreille attend un sol. La victoire est amère trois secondes — on sort du Marais, on n'en revient pas indemne — puis do majeur la relève.
- **Arc.** Arpège en noires aux quatre premières mesures, en croches ensuite ; batterie de 2 à 5 frappes par mesure, le charleston ouvert n'arrivant qu'au tout dernier temps.
- Le do bécarre du mixolydien supprime la sensible : la cadence finale est **do-ré, pas la-ré**. C'est ce qui empêche la victoire de sonner comme un générique et ce qui la rattache au monde modal du reste du jeu.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..A6 | 41 |
| 1 | gauche | médiane (accords tenus) | B3..A4 | 45 |
| 2 | **gauche** | basse | F♯2..G3 | 48 |
| 3 | **droite** | **contre-chant — la voix qui répond** | D4..C5 | 51 |
| 4 | droite | arpège | F♯3..G4 | 70 |
| 5 | **droite** | **batterie** — charleston 24, grosse caisse 16, caisse claire 16, charleston ouvert 4, cymbale 3 | bruit | 63 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/victoire
python3 victoire.py
python3 ../../midi_to_mb.py victoire.mid VICTORY.MB.BIN \
    --bpm 150 --no-loop --max 1280 --wav VICTOIRE.wav
```
