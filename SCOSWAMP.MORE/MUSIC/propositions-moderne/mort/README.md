# Zone `mort` — surcouche, 11 pages et l'écran `game_over`

**`DEATH.MB.BIN` — 673 octets, 31,0 s, `--no-loop`.**

Surcouche : tampon de 1 280 octets, 607 de marge — la pièce la plus au large du dossier. **Sans batterie** : six voix de hauteur.

## Ce que la zone couvre

| Pages | 003, 030, 098, 260, 297, 313, 332, 361, 372, 375, 401 |
| --- | --- |

Plus l'écran `game_over` du moteur. Quatre de ces pages (297, 372, 375, 401)
sont aussi des pages de la tour de Stratagus : la surcouche prime.

La pièce se joue **une seule fois** puis laisse le silence — c'est le seul
usage de `--no-loop` avec `victoire`. Une boucle sur un écran de mort serait
une punition.

## La pièce

| | |
| --- | --- |
| Titre | **Le Marais Referme** |
| Source | composition originale, `mort.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | rien ne court. **Aucune percussion** : c'est la seule pièce du dossier où l'absence de frappe est le sujet |
| Mode | **do éolien** (do ré mi♭ fa sol la♭ si♭) |
| Tempo | **125** à la noire, écrit en blanches et en rondes — le pouls réel est à 62 |
| Forme | quatre phrases de quatre mesures ; le crochet énoncé deux fois, puis une troisième qui ne remonte plus |
| Durée | 16 mesures à 4/4 = **31,0 s** |
| Taille | **673 octets** — 174 notes, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** Une chute : sol-mi bémol, puis la bémol-sol-fa. Énoncé mesures 1-2, **repris mesures 9-10** sur la bémol au lieu de do mineur, et la troisième fois il ne remonte plus.
- **Question et réponse.** Mesures 3 et 12 : la mélodie tient une ronde, le contre-chant descend seul.
- **Surprise, deux fois.** Mesure 12, **tout se tait pendant deux temps** — le marais se referme, et il y a un trou. Puis mesure 13 tombe un accord de **ré bémol majeur**, le napolitain : c'est exactement l'accord du thème `danger`, la chose qui vous a tué, citée une fois, sans commentaire.
- **Rythme harmonique.** Huit temps par accord aux deux premières phrases, quatre ensuite : la pièce se resserre en se refermant.
- **Arc.** L'arpège descend (quinte, tierce, fondamentale) et **ralentit à la dernière mesure**, passant à la blanche.
- La cadence finale est plagale (A♭-Cm), pas dominante : elle referme au lieu de conclure.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie, blanches et rondes | D♯5..D♯6 | 31 |
| 1 | gauche | médiane (accords tenus) | G♯3..F4 | 21 |
| 2 | **gauche** | basse, deux blanches par mesure | F2..G♯3 | 31 |
| 3 | **droite** | arpège **descendant**, qui ralentit à la fin | C4..D♯5 | 58 |
| 4 | droite | contre-chant | G3..F4 | 29 |
| 5 | **droite** | bourdon de do | C2 | 4 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/mort
python3 mort.py
python3 ../../midi_to_mb.py mort.mid DEATH.MB.BIN \
    --bpm 125 --no-loop --max 1280 --wav MORT.wav
```
