# Zone `combat` — surcouche, 32 pages

**`BATTLE.MB.BIN` — 1 228 octets, 24,3 s, boucle.**

Surcouche : le flux doit tenir dans le **tampon de surcouche de 1 280 octets**, la moitié de celui des thèmes de zone. Il reste 52 octets.

## Ce que la zone couvre

Ce n'est pas une zone de la carte : c'est une **surcouche**. Les 32 pages qui
portent une ligne `M` (combat) prennent ce thème le temps du combat, puis la
musique de la clairière revient toute seule.

| Pages | 012, 026, 028, 064, 079, 082, 120, **124**, 134, 146, 171, 176, 200, 211, 215, 221, 222, 224, 225, 235, 261, 267, 281, 284, 301, 312, 341, 355, 378, 379, 392, 402 |
| --- | --- |

Cinq d'entre elles appartiennent aussi à une clairière (082 → clairière 35,
355 → clairière 1) ou à la tour (124, 222, 225, 402) : la surcouche prime pour
la page, la mémoire de zone n'est pas effacée.

## La pièce

| | |
| --- | --- |
| Titre | **Le Fer et la Pince** |
| Source | composition originale, `combat.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | c'est la **batterie** qui court — grosse caisse, caisse claire, charleston en croches — et les quintes à vide n'ont plus qu'à frapper les temps |
| Mode | **si éolien** (si do♯ ré mi fa♯ sol la) |
| Tempo | **200** à la noire — **15 ticks par temps**, la valeur la plus rapide qui tombe juste sur l'horloge de 50 Hz |
| Forme | garde (4) — A, crochet énoncé deux fois (8) — B (8) |
| Durée | 20 mesures à 4/4 = **24,3 s** — la durée d'une mêlée |
| Taille | **1 228 octets** — 242 notes de hauteur, 82 coups, 0 abandonnée |

## Ce que la révision a apporté

- **La batterie prend le travail.** Avant la révision, cinq voix de hauteur essayaient de faire un rythme : l'arpège martelait en croches et la basse frappait le contretemps. Maintenant le bruit s'en charge et les quintes ne jouent plus que les temps — le morceau y gagne en clarté autant qu'en octets.
- **Crochet.** Si-ré-mi-fa♯ qui monte, sol-fa♯-ré qui retombe, mesures 5-6, **repris mesures 9-10** avec une issue différente (la-fa♯ mineur au lieu de ré-la).
- **Question et réponse.** Mesures 7 et 12 : la mélodie tient une ronde en haut du registre, le contre-chant répond.
- **Surprise.** Mesure 16, **deux temps de rien**, batterie comprise, en pleine mêlée. Puis les huit dernières mesures ne lâchent plus.
- **Arc.** Garde : deux frappes par mesure, quintes à la noire, basse aux blanches. A : quatre frappes. B : cinq frappes, et la basse passe au contretemps.
- Le bourdon de fa♯ a cédé sa voix à la batterie ; c'est la grosse caisse qui tient la dominante, et rien ne se résout tant que le combat dure.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie, en valeurs longues | F♯5..B6 | 54 |
| 1 | gauche | accords tenus | A3..B4 | 29 |
| 2 | **gauche** | basse | D2..F♯3 | 47 |
| 3 | **droite** | **contre-chant — la voix qui répond** | D4..C♯5 | 46 |
| 4 | droite | **quintes à vide**, sur les temps | F♯3..F♯4 | 66 |
| 5 | **droite** | **batterie** — charleston 39, grosse caisse 24, caisse claire 15, cymbale 2 | bruit | 80 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/combat
python3 combat.py
python3 ../../midi_to_mb.py combat.mid BATTLE.MB.BIN \
    --bpm 200 --max 1280 --wav COMBAT.wav
```
