# Zone `sud` — les douze clairières au sud de la rivière

**`SOUTHSWAMP.MB.BIN` — 2 277 octets, 45,1 s, boucle.** Tampon de zone (2 304 o), 27 octets de marge.

## Ce que la zone couvre

La plus grande zone du jeu : douze clairières, dont celle du départ.

| # | `hub` | Titre | (x,y) | Pages |
| ---: | ---: | --- | :---: | --- |
| 16 | 304 | Le Perroquet / Maîtresse des Oiseaux | (0,4) | 304, 149, 217 |
| 17 | 094 | La brume fétide | (1,4) | 94 |
| 18 | 179 | Le pique-nique suspect | (2,4) | 66, 192, 179 |
| 20 | 047 | Trois chemins herbeux | (4,4) | 47 |
| 21 | 031 | Bassin de cristal | (5,4) | 31, 77, 394 |
| 23 | 348 | La Licorne | (1,5) | 320, 265, 348 |
| 24 | 227 | La clairière des combats | (2,5) | 10, 142, 227 |
| 30 | 230 | Clairière des grenouilles | (4,6) | 53, 329, 230 |
| 32 | 314 | Clairière du Maître des Loups | (1,8) | 398, 239, 314 |
| **33** | **058** | **Le large rond-point (départ)** | (2,8) | **195**, 24, 208, 58, 404, 405 |
| 34 | 390 | Pierres et tronc | (3,8) | 105, 330, 390 |
| 35 | 082 | Bête du bassin | (4,8) | 209, 82, 308, 397 |

Les pages **394** et **330** appartiennent aux clairières 21 et 34, non aux 20
et 25 (`CARTOGRAPHIE.md:810-820`). La page 208 porte en plus la musique de
`village` (sortie du Marais).

## La pièce

| | |
| --- | --- |
| Titre | **Sentiers Verts** |
| Source | composition originale, `sud.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | marcher longtemps sans savoir où : la zone la plus vaste a la musique la moins pressée de conclure |
| Mode | **ré éolien** (ré mi fa sol la **si♭** do) |
| Tempo | **150** à la noire |
| Forme | intro (4) — A, crochet énoncé deux fois (8) — B (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **45,1 s** |
| Taille | **2 277 octets** — 469 notes de hauteur, 113 coups, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** La montée ré-fa-la et la descente si bémol-la-fa, mesures 5-6, **reprises mesures 9-10** ; la seconde fois elle débouche sur un **la majeur** (mesure 11), seule sensible du morceau, et la cadence sur ré en devient franche.
- **Question et réponse.** Mesures 7, 12 et 24.
- **Surprise.** Mesures 17-18, tout passe en demi-mesure : la batterie ne frappe plus que les temps 1 et 3, l'arpège retombe à la noire, la basse aux blanches, l'harmonie tient huit temps sur si bémol. Le sentier débouche sur une trouée, on ralentit, puis la marche reprend sur un coup de cymbale.
- **Rythme harmonique.** Huit temps sur ré mineur à l'intro, quatre en marche, deux aux mesures 11 et 23, huit dans la trouée et sur la cadence.
- Le si bémol sépare cette pièce du ré dorien de l'accueil : **même tonique, autre monde.** Le joueur qui ressort du Marais (page 208) réentend le si bécarre du village ; c'est le seul repère tonal du jeu, et il est gratuit.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..A6 | 69 |
| 1 | gauche | médiane (accords tenus) | A3..A4 | 78 |
| 2 | **gauche** | basse, marche de noires | E2..G3 | 108 |
| 3 | **droite** | **contre-chant — la voix qui répond** | D4..C5 | 75 |
| 4 | droite | arpège fondamentale-quinte | F3..G4 | 139 |
| 5 | **droite** | **batterie** — charleston 54, grosse caisse 32, caisse claire 24, cymbale 2 | bruit | 112 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/sud
python3 sud.py
python3 ../../midi_to_mb.py sud.mid SOUTHSWAMP.MB.BIN \
    --bpm 150 --max 2304 --wav MARAISUD.wav
```
