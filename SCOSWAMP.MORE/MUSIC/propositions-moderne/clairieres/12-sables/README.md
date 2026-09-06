# Clairière 12 — Sables mouvants (`hub` 270, case 4,2)

**`QUICKSAND.MB.BIN` — 1 920 octets, 43,3 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 041 | Sables mouvants | les troncs couverts de lierre, le sol qui cède, le test de Chance |
| 382 | Retour aux Sables Mouvants | la Pierre de Glace, la Pierre de Croissance |
| 270 | Deux sentiers | le nord ou l'ouest, « avec prudence » |

## La pièce

| | |
| --- | --- |
| Titre | **Le Sol qui Cède** |
| Source | composition originale, `sables.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on tombe, et on n'arrive pas en bas. « Aucun autre chemin ne semble présent : vous êtes pris au centre » |
| Mode | **fa mineur phrygien** (fa **sol♭** la♭ si♭ do ré♭ mi♭) |
| Tempo | **144** à la noire (auparavant 138) |
| Forme | intro (4) — A (8) — B (8) — A' (6) |
| Durée | 26 mesures à 4/4 = **43,3 s** |
| Taille | **1 920 octets** (marge 384 sur le tampon de zone) |
| Notes | 387 de hauteur + **97 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures qui ne fait que tomber : `fa' ré♭' do' la♭ /
  sol♭ fa ré♭`. Quatre chutes puis une cinquième, plus grave. Énoncé trois
  fois ;
- **une réponse** aux mesures 12, 20 et 26 : le chant tient et la chute — voix
  3, à droite — répond, toujours vers le bas ;
- **la surprise** : mesure 18, **l'arpège remonte**. Une seule mesure du
  morceau : fondamentale, tierce, quinte, octave, et l'on croit s'en sortir. La
  mesure 19 retombe **deux fois plus vite**, en doubles croches. Puis mesure 20,
  **un temps et demi de silence général** — le sol cède pour de bon — un tom qui
  tombe seul, et tout repart ensemble ;
- **le sol cède toujours à la mesure 9** : l'arpège passe de la noire à la
  croche et la basse double, exactement comme le `danger` de la zone se resserre
  à sa neuvième mesure ;
- **le tempo monte de 138 à 144**.

## La batterie

**Un tom lent qui accélère avec le terrain.** Deux frappes par mesure tant que
le sol tient, quatre dès qu'il cède, une grosse caisse en dessous, et le tom
seul dans le silence de la mesure 20 — trois coups qui ralentissent en tombant.
**Pas un charleston** : rien ne claque dans du sable. Soixante toms sur
quatre-vingt-dix-sept coups, c'est le kit le plus sourd des douze.

## Ce qui la relie à `danger`, et ce qui l'en sépare

Demi-ton phrygien, bourdon immobile, crescendo par la densité : les trois
marques de la zone sont là. Ce qui appartient à cette clairière-là, c'est le
**sens**. Tout descend — l'arpège parcourt l'accord à l'envers, quinte, tierce,
fondamentale, puis la quinte une octave plus bas, et recommence en haut à chaque
changement d'accord, si bien qu'on n'arrête pas de retomber sans jamais arriver
en bas. Chaque phrase du chant part de sa note la plus aiguë et finit sur sa
plus grave.

**La voix des accords a cédé la place, pas le bourdon** — la règle du `danger`.
Le bourdon de **do**, la quinte à vide de fa, est la seule chose qui ne bouge
pas : on s'enfonce, mais le Marais, lui, ne s'enfonce pas.

## Les six voix, mesurées

`python3 ../../verifier.py sables.mid --bpm 144`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | C♯5..G♯6 | 75 |
| 1 | gauche | le contre-chant, qui porte l'harmonie | C3..D♯4 | 54 |
| 2 | **gauche** | **le bourdon de do**, immobile | C2 | 7 |
| 3 | **droite** | **la chute**, et les réponses | F3..G♯5 | 170 |
| 4 | droite | la basse, tenue puis doublée | F2..G♯3 | 81 |
| 5 | **droite** | **LA BATTERIE** — tom 60, grosse caisse 36, cymbale 1 | bruit | 97 |

Stéréo mesurée **60/40**, aucune note abandonnée, `verifier.py` conclut `OK`.

La voix 3 traverse deux octaves et demie, de fa3 à sol♯5 : c'est l'escalier de
sable, qui recommence en haut chaque fois qu'il est arrivé en bas.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/12-sables
python3 sables.py
python3 ../../../midi_to_mb.py sables.mid QUICKSAND.MB.BIN \
    --bpm 144 --max 2304 --wav SABLES.wav
```
