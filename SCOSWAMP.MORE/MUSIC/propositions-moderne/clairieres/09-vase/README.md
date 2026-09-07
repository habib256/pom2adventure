# Clairière 9 — Le bassin de Vase (`hub` 153, case 1,2)

**`MUD.MB.BIN` — 1 594 octets, 45,2 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 336 | Le bassin de Vase | le bruit de succion, le bassin, la Vase qui se soulève et barre le passage |
| 137 | Retour face à la Vase | ses blessures sont complètement guéries |
| 153 | Fuite de la clairière | le nord ou l'ouest, le sol semble plus sec |

## La pièce

| | |
| --- | --- |
| Titre | **Ce qui Sort du Bassin** |
| Source | composition originale, `vase.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | lent, épais, et qui se resserre. Deux mètres de fange qui rampent ne changent pas d'avis |
| Mode | **ré phrygien** (ré **mi♭** fa sol la si♭ do) |
| Tempo | **138** à la noire (auparavant 132) |
| Forme | intro (4) — A (8) — B (8) — A' (6) |
| Durée | 26 mesures à 4/4 = **45,2 s** — la plus longue des douze |
| Taille | **1 594 octets** (marge 710 sur le tampon de zone) |
| Notes | 319 de hauteur + **83 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** de deux mesures, `la si♭ la fa ré' / mi♭' ré'` : le demi-ton
  phrygien pris à l'endroit puis à l'envers. C'est la cellule de la fange,
  chantée. Énoncé trois fois ;
- **une réponse** aux mesures 12, 20 et 26 : le chant tient et la fange — voix
  3, à droite — répond à sa place ;
- **la surprise, et c'est le bourdon lui-même** : il ne bouge pas du morceau
  sauf pendant le B, où il **monte d'un demi-ton, de ré à mi♭**, et y reste huit
  mesures. Le sol s'est déplacé. Il redescend à la mesure 21 sans qu'on
  l'entende arriver. Juste avant le B, mesure 12, **un temps et demi de silence
  général** : le bassin retient son souffle ;
- **le crescendo par la densité s'étend à la basse** : elle tient une blanche
  par demi-mesure au A, deux noires au B, et retient de nouveau au A'. La fange
  et la basse se resserrent ensemble ;
- **le tempo monte de 132 à 138**.

## La batterie

**Un cœur qui bat sourd.** Deux grosses caisses par mesure et rien d'autre
pendant tout le A ; une cymbale à l'instant où la fange se soulève ; trois
grosses caisses et deux toms par mesure au B ; le battement seul pour finir.
**Aucun charleston** : rien ne brille dans deux mètres de vase, et c'est la
seule des douze dont le kit ne compte que trois instruments.

## Ce qui la relie à `danger`, et ce qui l'en sépare

Les deux marques de la zone sont le **demi-ton phrygien** posé un cran au-dessus
de la tonique et le **crescendo par la densité**. Ici les deux ne font qu'une
seule chose : la cellule **ré - mi♭ - ré - fa** ne change pas une note du
morceau et se resserre trois fois — blanches, puis noires, puis croches.

**La voix des accords a cédé la place, pas le bourdon.** C'est la règle de
`INDEX.md § 3.2` pour le `danger` : le bourdon fait le caractère de la pièce, on
ne le retire pas. Il reste donc cinq parties de hauteur — chant, fange,
contre-chant, basse, bourdon — l'harmonie est portée par la basse et le
contre-chant, la basse passe à droite sous la fange, et le bourdon garde le fond
à gauche.

## Les six voix, mesurées

`python3 ../../verifier.py vase.mid --bpm 138`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | F5..A♯6 | 73 |
| 1 | gauche | le contre-chant, qui porte l'harmonie | F3..F4 | 51 |
| 2 | **gauche** | **le bourdon**, ré puis mi♭ puis ré | D2..D♯2 | 7 |
| 3 | **droite** | **la fange**, et les réponses | D4..F4 | 120 |
| 4 | droite | la basse, tenue puis resserrée | A♯2..G3 | 68 |
| 5 | **droite** | **LA BATTERIE** — grosse caisse 66, tom 16, cymbale 1 | bruit | 83 |

Stéréo mesurée **60/40**, aucune note abandonnée, `verifier.py` conclut `OK`.

La voix 2 ne contient que **sept notes** et sonne 100 % du temps : c'est le
bourdon, et les deux seules hauteurs qu'on y trouve sont le ré et le mi♭ du
déplacement. Tout le morceau tient sur ce demi-ton, y compris le sol.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/09-vase
python3 vase.py
python3 ../../../midi_to_mb.py vase.mid MUD.MB.BIN \
    --bpm 138 --max 2304 --wav VASE.wav
```
