# Clairière 7 — Le Géant (`hub` 161, case 4,1)

**`GIANT.MB.BIN` — 1 624 octets, 41,7 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 275 | Le Géant | l'empreinte de cinquante centimètres, la massue à pointes, « IL EST INTERDIT DE PASSER ! » |
| 342 | Retour au Géant | l'avez-vous tué ? |
| 161 | Carrefour après le Géant | trois directions |
| 103 | Le Géant | les renseignements : Courbensaule est loin à l'ouest |
| 244 | Le conseil du Géant | le buisson au nord, « prenez garde aux Loups ! » |

## La pièce

| | |
| --- | --- |
| Titre | **Il Est Interdit de Passer** |
| Source | composition originale, `geant.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | énorme, furieux, mais pas maléfique — l'Anneau de Cuivre reste froid. On n'a pas peur de lui, on ne passe pas |
| Mode | **do mineur éolien** (do ré mi♭ fa sol la♭ si♭) |
| Tempo | **138** à la noire (auparavant 132) |
| Forme | intro (4) — A (8) — B (6) — A' (6) |
| Durée | 24 mesures à 4/4 = **41,7 s** |
| Taille | **1 624 octets** (marge 680 sur le tampon de zone) |
| Notes | 317 de hauteur + **77 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures, `do mi♭ sol la♭ sol / sol mi♭ do` : la montée
  du géant, le la♭ qui bute contre le sol, la retombée. Énoncé trois fois ;
- **une réponse** aux mesures 8, 12 et 24 : le chant tient et l'empreinte — voix
  3, à droite — répond. Une question à hauteur d'homme, une réponse à hauteur de
  géant ;
- **la surprise** : mesure 16, l'accord de **ré bémol majeur**, le napolitain.
  Un demi-ton au-dessus de la tonique, en majeur, là où tout le morceau est
  mineur — et l'ostinato le suit, ré♭ - la♭ - fa - la♭, la seule mesure où il
  bouge. Puis mesure 18, **un temps et demi de silence général** : il s'arrête ;
- **le rythme harmonique varie** : grille à la demi-mesure. Le géant tient un
  accord par mesure, la massue en prend deux ;
- **le tempo monte de 132 à 138** : ce n'était plus une marche, c'en est une.

## La batterie

**Le pas.** Grosse caisse au premier temps, tom au troisième, un souffle de
charleston par mesure, et rien d'autre — jusqu'au B, où la massue tourne en
croches et la caisse claire s'ajoute. Les deux dernières mesures reprennent la
cellule du B : le dernier pas est le plus lourd. Le bourdon de do a cédé la
place, et la grosse caisse en tient lieu, ce qui est exactement son emploi ici.

## Ce qui la relie à `nord`, et ce qui l'en sépare

L'ostinato de la zone court en croches. Celui-ci marche en **noires** : quatre
pas par mesure, **do - sol - mi♭ - sol**, l'empreinte de cinquante centimètres
de la page 275. Il occupe deux fois moins d'espace que celui de la zone — et
c'est exactement ce qui fait la taille d'un géant : un pas qui prend le temps
d'un pas. Il ne double en croches que dans le B, quand la massue tourne, et il
retombe en noires pour le A'. C'est tout le crescendo, et il ne coûte rien : le
lecteur MB1 n'a pas de volume par note, on ne peut serrer que la densité.

## Les six voix, mesurées

`python3 ../../verifier.py geant.mid --bpm 138`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | A♯4..A♯6 | 68 |
| 1 | gauche | le contre-chant, détaché | G3..G4 | 54 |
| 2 | **gauche** | la basse pesante, posée et lâchée | F2..G♯3 | 58 |
| 3 | **droite** | **l'empreinte**, et les réponses | C4..A♯4 | 83 |
| 4 | droite | les accords tenus | G3..G♯4 | 54 |
| 5 | **droite** | **LA BATTERIE** — grosse caisse 30, tom 27, caisse claire 11, charleston fermé 8, cymbale 1 | bruit | 77 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

**1 624 octets, la plus petite des douze, marge 680.** Un géant tient dans peu
de notes : trois cent dix-sept, dont quatre-vingt-trois pour l'empreinte.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/07-geant
python3 geant.py
python3 ../../../midi_to_mb.py geant.mid GIANT.MB.BIN \
    --bpm 138 --max 2304 --wav GEANT.wav
```
