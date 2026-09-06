# Zone `accueil` — l'écran de titre

**`WELCOME.MB.BIN` — 2 233 octets, 49,7 s, boucle.** Tampon de zone (2 304 o), 71 octets de marge.

## Ce que la zone couvre

| Page | Titre | Rôle |
| --- | --- | --- |
| 000 | écran d'accueil | la seule page où le moteur entre sans qu'un choix y mène |

Aucune clairière. La page 000 est le portage, pas le livre
(`SCOSWAMP/DOCS/CARTOGRAPHIE.md` § 6.2). Elle remplace `COMEAGAIN.MB`,
aujourd'hui sur le disque.

## La pièce

| | |
| --- | --- |
| Titre | **L'Appel du Marais** |
| Source | composition originale, `accueil.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt — aucune œuvre tierce |
| Caractère | ouverture de film : six voix frappent ensemble, un appel de cor monte à la quinte et revient une octave plus haut |
| Mode | **ré dorien** (ré mi fa sol la **si** do) — le si bécarre est la lueur qui manque à tout le reste du jeu |
| Tempo | **136** à la noire |
| Forme | intro (4) — A « le seuil », crochet énoncé deux fois (8) — B « l'appel » (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **49,7 s** |
| Taille | **2 233 octets** — 466 notes de hauteur, 105 coups, 0 abandonnée |

## Ce que la révision a apporté

- **Crochet.** Le motif ré-fa-sol-la / ré-do-la est énoncé mesures 5-6, **repris tel quel mesures 9-10** sur une autre harmonie (F-G au lieu de F-Am), et repris une octave au-dessus mesure 21.
- **Question et réponse.** Mesures 7, 12 et 24 la mélodie tient une ronde et le contre-chant répond en croches : voix 0 à gauche, voix 3 à droite, l'échange traverse la stéréo.
- **Partie B contrastée.** La mélodie redescend d'une octave et l'harmonie emprunte le **si bémol** du ré éolien, étranger au dorien.
- **Surprise.** Mesure 20, un **la majeur** : le do dièse est la seule sensible du morceau. Puis **deux temps de silence complet**, batterie comprise, avant que A' reparte à l'octave.
- **Rythme harmonique.** Douze temps sur ré mineur à l'intro, quatre en A, deux à la mesure 11, huit sur la cadence finale.
- **Arc.** L'arpège va en noires à l'intro, en croches en A, retombe à la noire dans la première moitié du B, repart ; la batterie passe de 2 à 5 frappes par mesure.

## Les voix

Mesuré par `../verifier.py` — c'est l'attribution réelle de
`midi_to_mb.py`, pas une intention. Voir `../INDEX.md` § 3.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..A6 | 71 |
| 1 | gauche | médiane (arpège / accords tenus) | A3..A4 | 78 |
| 2 | **gauche** | basse, fondamentale et quinte grave | E2..G3 | 115 |
| 3 | **droite** | **contre-chant — la voix qui répond** | D4..C5 | 78 |
| 4 | droite | médiane (arpège) | F3..G4 | 124 |
| 5 | **droite** | **batterie** — charleston 47, grosse caisse 32, caisse claire 23, cymbale 3 | bruit | 105 |

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/accueil
python3 accueil.py
python3 ../../midi_to_mb.py accueil.mid WELCOME.MB.BIN \
    --bpm 136 --max 2304 --wav ACCUEIL.wav
python3 ../verifier.py accueil.mid --bpm 136
```

Le `.wav` n'est pas suivi par git (`.gitignore:76`) : c'est un rendu, et il est
*exactement* ce que la carte jouera — six ondes carrées, deux puces, rien d'autre.
