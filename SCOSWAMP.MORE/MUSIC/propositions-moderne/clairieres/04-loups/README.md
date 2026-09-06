# Clairière 4 — Les deux loups (`hub` 232, case 4,0)

**`WOLVES.MB.BIN` — 2 253 octets, 38,4 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 092 | Les deux loups | la forêt profonde, le silence, puis deux énormes loups qui vous fixent |
| 247 | Buisson violet | feuilles vert foncé, fleurs blanches, la grosse baie |
| 232 | La baie rangée | vous la cueillez et la rangez |
| 389 | Buisson d'Anthérique trouvé | la moitié de la mission est accomplie |

## La pièce

| | |
| --- | --- |
| Titre | **Deux Paires d'Yeux** |
| Source | composition originale, `loups.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | l'affût. « Vous tendez l'oreille, mais rien d'anormal ne trouble le silence. Puis, soudain, deux énormes loups… » |
| Mode | **si mineur éolien** (si do♯ ré mi fa♯ sol la) |
| Tempo | **172** à la noire (auparavant 168) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures dont **une à 2/4**, 110 temps = **38,4 s** |
| Taille | **2 253 octets** (marge 51 sur le tampon de zone) |
| Notes | 459 de hauteur + **69 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures, `si ré fa♯ ré si / do♯ si fa♯` : la montée
  d'un trait puis la retombée par le demi-ton. Énoncé trois fois ;
- **une réponse** aux mesures 8, 18 et 28 : le chant tient, la bête de droite —
  voix 3 — répond. Les deux paires d'yeux ne regardent jamais ensemble ;
- **la surprise, et c'est la seule des douze clairières** : **la mesure 12 n'a
  que deux temps**. Tout le morceau est à 4/4 sauf elle. On recule d'un pas, la
  phrase boite, et le B tombe une demi-mesure trop tôt. Second coup mesure 20,
  **fa dièse majeur**, un la dièse hors du mode — les crocs — puis **un temps et
  demi de silence général** avant le A' ;
- **le rythme harmonique varie** : grille à la demi-mesure, un accord par mesure
  à l'affût, deux dès que la bête bouge ;
- **le tempo monte de 168 à 172** et la pièce raccourcit de 40,0 à 38,4 s, la
  mesure boiteuse comprise.

## La batterie

**Le cœur qui bat.** Deux toms sourds par deux mesures dans l'intro, une grosse
caisse à l'affût au A, un galop au B, la marche du recul au A' — et un seul coup
de grosse caisse et de caisse claire dans la mesure boiteuse, qui la fait
entendre comme un trébuchement. Le bourdon de fa♯ a cédé la place, et c'est
mieux ainsi : un affût ne bourdonne pas, il bat.

## Ce qui la relie à `nord`, et ce qui l'en sépare

Le procédé de la zone est l'ostinato fixe. Ici il est fixe et il y en a
**deux** : une cellule haute — si - fa♯ - la - fa♯ — et une cellule basse —
mi - si - ré - si — qui se relaient de mesure en mesure. Ni l'une ni l'autre ne
bouge d'une note de tout le morceau, y compris quand l'harmonie passe sous
elles ; ce sont deux bêtes qui se répondent d'un bord à l'autre de la clairière.
Les deux cellules sont détachées : un pas dans les feuilles, pas un
bourdonnement.

## Les six voix, mesurées

`python3 ../../verifier.py loups.mid --bpm 172`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | F♯5..A6 | 82 |
| 1 | gauche | le contre-chant, détaché | F♯3..A4 | 75 |
| 2 | **gauche** | la basse qui rôde, sèche | A2..B3 | 98 |
| 3 | **droite** | **les deux cellules**, et les réponses | B3..D5 | 168 |
| 4 | droite | les accords tenus | F♯3..D4 | 36 |
| 5 | **droite** | **LA BATTERIE** — grosse caisse 32, tom 20, caisse claire 16, cymbale 1 | bruit | 69 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

⚠ **2 253 octets, marge 51.** C'est la deuxième plus grosse des douze après
`COURBENS`. Toute retouche de `loups.py` doit être reconvertie avant d'être
crue.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/04-loups
python3 loups.py
python3 ../../../midi_to_mb.py loups.mid WOLVES.MB.BIN \
    --bpm 172 --max 2304 --wav LOUPS.wav
```
