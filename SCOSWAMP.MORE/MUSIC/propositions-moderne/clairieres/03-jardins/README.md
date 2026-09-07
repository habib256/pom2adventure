# Clairière 3 — Le Maître des Jardins (`hub` 084, case 3,0)

**`GARDENS.MB.BIN` — 2 042 octets, 43,3 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 305 | Le Maître des Jardins | le sentier taillé, l'Amulette d'Argent en forme de fleur, l'Anneau reste froid |
| 238 | Clairière du Maître des Jardins | elle est belle et complètement déserte |
| 084 | Le Maître des Jardins | il est un ami ; un seul chemin y mène |
| 117 | L'Amulette du Jardin | la Pierre d'Amitié, la paralysie, l'avertissement |
| 251 | Maître des Jardins | vous l'avez tué : −3 CHANCE, l'Amulette FLEUR |
| 283 | Le Maître des Jardins | l'Anthérique promis, une Pierre bénéfique |
| 396 | Le buisson d'Anthérique | « prenez la direction de l'ouest, puis revenez vers l'est » |

Sept pages : la clairière la plus bavarde du Marais nord.

## La pièce

| | |
| --- | --- |
| Titre | **L'Amulette de Fleur** |
| Source | composition originale, `jardins.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | le seul endroit amical du Marais nord. « Trop belle pour être entièrement naturelle, trop naturelle pour être vraiment un jardin » |
| Mode | **ré dorien** (ré mi fa sol la **si** do) |
| Tempo | **144** à la noire (auparavant 138) |
| Forme | intro (2) — A (8) — B (8) — A' (8) |
| Durée | 26 mesures à 4/4 = **43,3 s** |
| Taille | **2 042 octets** (marge 262 sur le tampon de zone) |
| Notes | 414 de hauteur + **59 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures qui pose la fleur au sommet : `ré fa la **si**
  la / sol la fa`. Énoncé trois fois ;
- **une réponse** aux mesures 10, 18 et 26 : le chant tient une ronde et le
  sécateur — voix 3, à droite — taille à sa place ;
- **la surprise** : mesure 14, un **si bémol**. Le mode bascule du dorien à
  l'éolien pour quatre mesures, la fleur se referme, et l'ostinato se referme
  avec elle — c'est la seule fois du morceau où sa troisième note change. Le sol
  majeur ne revient qu'à la mesure 18, juste avant **deux temps de silence
  général** d'où tout repart ensemble ;
- **le rythme harmonique varie** : grille à la demi-mesure ; les mesures de repos
  tiennent un accord, celles de mouvement en ont deux ;
- **le tempo monte de 138 à 144**.

## La batterie

**La plus discrète des douze avec celle de l'Aigle.** Rien dans l'allée, deux
charlestons par mesure au A, un tom sourd et une seule cymbale au B, une grosse
caisse très légère au A' : cinquante-neuf coups en quarante-trois secondes, 4 %
d'occupation. Une clairière paisible n'a pas besoin d'être battue, elle a besoin
d'être mesurée. Le bourdon de ré a cédé la place.

## Ce qui la relie à `nord`, et ce qui l'en sépare

Même famille mineure, même ostinato fixe de quatre croches. **Une seule note
change de la zone à la clairière** : la sixte. Le `nord` est en éolien, la sixte
y est mineure et c'est elle qui mord ; ici le mode est **dorien**, la sixte est
majeure — le si bécarre — et c'est elle la fleur. L'ostinato la touche à chaque
tour, **la - fa - si - sol**, et l'harmonie pose un **sol majeur** que le mode
éolien de la zone ne peut pas produire. L'ostinato est joué détaché, à la
manière du sécateur ; la basse tient au lieu de marcher, parce qu'ici on ne fuit
pas.

## Les six voix, mesurées

`python3 ../../verifier.py jardins.mid --bpm 144`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | D5..A6 | 77 |
| 1 | gauche | le contre-chant, détaché | A3..G4 | 49 |
| 2 | **gauche** | la basse, posée et lâchée | E2..G3 | 67 |
| 3 | **droite** | **le sécateur**, détaché, et les réponses | D4..D5 | 186 |
| 4 | droite | les accords tenus | F3..E4 | 35 |
| 5 | **droite** | **LA BATTERIE** — charleston fermé 40, tom 10, grosse caisse 8, cymbale 1 | bruit | 59 |

Stéréo mesurée **58/42**, aucune note abandonnée, `verifier.py` conclut `OK`.

La séparation est nette : chaque partie écrite tombe dans une voix et une
seule, et la batterie n'occupe que 4 % du temps — c'est la clairière où l'on
entend le plus de silence.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/03-jardins
python3 jardins.py
python3 ../../../midi_to_mb.py jardins.mid GARDENS.MB.BIN \
    --bpm 144 --max 2304 --wav JARDINS.wav
```
