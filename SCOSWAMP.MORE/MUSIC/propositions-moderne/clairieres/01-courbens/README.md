# Clairière 1 — Route de Courbensaule (`hub` 078, case 0,0)

**`BENTBEAKS.MB.BIN` — 2 276 octets, 38,2 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 280 | Route de Courbensaule | le Marais s'ouvre, les gardes forestiers, les trois auberges |
| 355 | Retour à Courbensaule | la rumeur des exploits, les deux coupeurs de bourses |
| 078 | La Lance Tordue | l'auberge, +2 ENDURANCE, le sorcier voisin |
| 150 | Le marchand de potions | Alphonse Machefer, négociant en magie |
| 408 | Échange chez Alphonse | jusqu'à trois objets contre des Pierres neutres |

C'est la seule clairière **hors Marais** des trente-cinq : une ville marchande,
pas une trouée dans la fange. La zone de référence est donc `village`.

## La pièce

| | |
| --- | --- |
| Titre | **La Route des Trois Auberges** |
| Source | composition originale, `courbens.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on arrive. Le seul morceau des douze qui n'ait rien à craindre : tierces majeures, septième mineure, un tambourin de marche |
| Mode | **ré mixolydien** (ré mi fa♯ sol la si do) |
| Tempo | **176** à la noire (auparavant 172) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **38,2 s** |
| Taille | **2 276 octets** (marge 28 sur le tampon de zone) |
| Notes | 457 de hauteur + **101 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures — `ré fa♯ la ré' do' / la sol fa♯`, la montée
  d'arpège puis la retombée par degrés. Il est énoncé **quatre fois**, et il
  ouvre la pièce dès la première mesure au lieu d'une intro qui prépare ;
- **une réponse** aux mesures 8, 12, 20 et 28 : le chant tient une ronde et
  c'est le tambourin — voix 3, à droite — qui répond par une figure écrite. La
  question est à gauche, la réponse est à droite, littéralement ;
- **le rythme harmonique varie** : la grille est écrite à la demi-mesure. Les
  mesures d'exposition tiennent un accord, celles de marche en ont deux ;
- **la surprise** : la troisième auberge, le Cheval Volant (mesures 17-18), est
  en **fa majeur** — le fa bécarre n'appartient pas au mode. C'est la seule fois
  du morceau où la route ment. Et mesure 20, tout s'arrête : **un demi-temps de
  silence général**, la batterie seule, puis le A' repart sur un tutti ;
- **l'arc de densité** : la basse pose un appui par demi-mesure jusqu'au B, puis
  reprend son balancement croche pointée - croche ; le tambourin tourne en
  noires dans l'intro et en croches ensuite ; la batterie entre au A ;
- **le tempo monte de 172 à 176**.

## La batterie

Un **tambourin de marche**, et c'est la pièce la mieux battue des douze : rien
sur la route, grosse caisse et caisse claire dès le A, charleston ouvert dans le
B, cellule complète au A'. Le bourdon de ré a cédé la place — la grosse caisse
en tient lieu, ce qui est un gain : un bourdon de ville n'existait pas.

## Ce qui la relie à `village`, et ce qui l'en sépare

De la zone elle garde les trois marques : le **mode majeur à septième mineure**,
l'**arpège de croches** qui tient lieu de tambourin, et la **basse balancée en
croche pointée - croche**, le pas de danse. Elle en change tout le reste : le
mode descend de sol à **ré**, une quinte plus bas ; le tempo monte de 166 à
**176** ; et le B enchaîne trois phrases de deux mesures, une par auberge, avant
la cadence du marchand de potions.

## Les six voix, mesurées

`python3 ../../verifier.py courbens.mid --bpm 176`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule, du début à la fin | D5..A6 | 90 |
| 1 | gauche | le contre-chant, et les notes basses du tambourin | B3..C5 | 88 |
| 2 | **gauche** | la basse de danse, détachée | A2..G3 | 87 |
| 3 | **droite** | **le tambourin**, et les quatre réponses | A3..E5 | 110 |
| 4 | droite | les accords tenus | F♯3..G4 | 82 |
| 5 | **droite** | **LA BATTERIE** — charleston fermé 36, caisse claire 30, grosse caisse 24, charleston ouvert 8, tom 2, cymbale 1 | bruit | 101 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

Mélodie et basse à gauche, tambourin et batterie à droite : la même image
stéréo que `VILLAGE.MB`, ce qui est voulu — les deux pièces se succèdent dans la
partie, page 009 puis page 280.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/01-courbens
python3 courbens.py
python3 ../../../midi_to_mb.py courbens.mid BENTBEAKS.MB.BIN \
    --bpm 176 --max 2304 --wav COURBENS.wav
```
