# Zone `nord` — les huit clairières au nord de la rivière

**`NORTHSWAMP.MB.BIN` — 2 262 octets, 45,1 s, boucle.** Tampon de zone (2 304 o), 42 octets de marge.

## Ce que la zone couvre

| # | `hub` | Titre | (x,y) | Pages |
| ---: | ---: | --- | :---: | --- |
| 2 | 234 | Le Patrouilleur vert | (2,0) | 170, 363, 234 |
| 3 | 084 | Le Maître des Jardins | (3,0) | 305, 238, 84, 117, 251, 283, 396 |
| 4 | 232 | Les deux loups | (4,0) | 92, 232, 247, 389 |
| 5 | 218 | Feu follet à l'orée | (1,1) | 218, 249 |
| 6 | 121 | Le croisement | (2,1) | 121 |
| 7 | 161 | Le Géant | (4,1) | 275, 342, 161, 103, 244 |
| 8 | 019 | Clairière aux brigands | (0,2) | 65, 343, 19 |
| 11 | 202 | Le nid de l'Aigle | (3,2) | 350, 331, 25, 112, 202 |

La page **363** appartient à la clairière 2 et non à la 3
(`CARTOGRAPHIE.md:810-820`).

## La pièce

| | |
| --- | --- |
| Titre | **Le Bois des Guetteurs** |
| Source | composition originale, `nord.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on est suivi. Un ostinato **fixe** de quatre croches — mi, si, sol, si — qui ne change jamais pendant que les accords bougent dessous |
| Mode | **mi éolien** (mi fa♯ sol la si do ré) |
| Tempo | **150** à la noire |
| Forme | intro (4) — A, thème énoncé deux fois (8) — B (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **45,1 s** |
| Taille | **2 262 octets** — 472 notes de hauteur, 99 coups, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** L'ostinato *est* le crochet, et il ne quitte jamais la pièce. Le thème chanté est énoncé mesures 5-6 et **repris mesures 9-10**, poussé plus haut par un la mineur et un si mineur passants.
- **Question et réponse.** Mesures 7, 12 et 24 : la mélodie tient, le contre-chant répond.
- **Surprise.** Mesures 17-18, l'accord passe en **mi majeur** et le sol de l'ostinato devient **sol dièse**. Le motif n'a pas bougé d'un pouce et il a changé de nature — les guetteurs se montrent. La batterie s'arrête pendant ces deux mesures, ce qui rend le glissement plus net encore.
- **Rythme harmonique.** Huit temps sur mi mineur à l'intro, quatre en A, deux à la mesure 11, huit sur le mi majeur, huit sur la cadence.
- **Arc.** L'ostinato se révèle : deux mesures à la noire avant de passer aux croches. La basse marche en noires mais **retient son pas pendant tout le B** (blanches), et repart en A'.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..B6 | 68 |
| 1 | **gauche** | **l'ostinato des guetteurs** | D4..B4 | 171 |
| 2 | **gauche** | basse, marche de noires | E2..G3 | 96 |
| 3 | **droite** | **contre-chant — la voix qui répond** | E4..C5 | 110 |
| 4 | droite | accords tenus | F♯3..E4 | 27 |
| 5 | **droite** | **batterie** — charleston 44, grosse caisse 30, caisse claire 22, cymbale 2 | bruit | 98 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/nord
python3 nord.py
python3 ../../midi_to_mb.py nord.mid NORTHSWAMP.MB.BIN \
    --bpm 150 --max 2304 --wav MARAISNO.wav
```
