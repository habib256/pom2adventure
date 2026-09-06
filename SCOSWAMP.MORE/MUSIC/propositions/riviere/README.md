# Zone `riviere` — la rivière Croupie, la falaise et le pont

**Fichier proposé : `RIVER.MB` (`RIVER.MB.BIN`, 719 octets, 37,8 s de boucle)**

La ligne `y = 3` de la grille coupe la carte en deux, et le pont en est l'unique
passage (`carte.json:784`, `CARTOGRAPHIE.md:377-379`). C'est la zone la plus
courte du jeu — trois clairières sur la rivière Croupie, une quatrième sur
l'autre cours d'eau — et la seule qu'on est obligé de traverser.

## Clairières couvertes (4)

| `hub` | `id` | Titre | Case | Pages |
| --- | --- | --- | --- | --- |
| **295** | 33 | La Rivière Croupie | (1,3) | 295 |
| **183** | 20 | Sommet de la falaise | (2,3) | 183 |
| **045** | 35 | **Le pont sur la rivière Croupie** | (3,3) | 138, 045, 101 |
| **044** | 34 | La rivière profonde | (1,7) | 90, 044, 254, 370 |

Ambiances :

- 295 : *« le cours d'eau est infesté de crocodiles »* (`TEXTFR/N250/N295.TXT:5`) ;
- 183 : *« c'est le ciel qui s'ouvre »*, *« Des crocodiles paresseux flottent au
  soleil »* (`TEXTFR/N150/N183.TXT:4,7-8`) ;
- 138 : *« Un pont l'enjambe, apparemment désert. »* (`TEXTFR/N100/N138.TXT:6`) ;
- 090 : *« La rivière tourbillonne en remous et n'inspire guère confiance »*
  (`TEXTFR/N050/N090.TXT:6`).

## La pièce

| | |
| --- | --- |
| Œuvre | **The Silver Swan** |
| Auteur | **Orlando Gibbons** (1583-1625), *First Set of Madrigals and Mottets*, **1612** |
| Source | Mutopia Project, [piece-info.cgi?id=302](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=302) |
| Fichiers | `https://www.mutopiaproject.org/ftp/GibbonsO/SilverSwan/SilverSwan.{ly,mid}` |
| Licence | **domaine public** |
| Effectif d'origine | cinq voix (SAATB) |
| Tempo retenu | **136** à la noire |
| Durée de boucle | 37,8 s |
| Taille | 719 octets |

## Pourquoi elle convient

Le sujet, d'abord : *« The silver swan, who living had no note… »* — un oiseau
d'eau, un courant, une fin. C'est le seul madrigal du répertoire libre qui parle
littéralement de la surface d'une rivière, et il le fait en descendant : chaque
phrase part haut et retombe, comme le fil de l'eau. Le pont, la falaise et les
crocodiles paresseux tiennent dans cette courbe.

Musicalement c'est aussi la pièce **la plus lisse** du lot — pas d'accents, pas
de danse, des entrées décalées qui se recouvrent — donc celle qui supporte le
mieux d'être coupée n'importe où par un changement de page.

**Tempo.** 136 la noire : plus vif que les 100-120 reprochés, sans faire courir
un madrigal qui doit couler. La boucle de 37,8 s couvre confortablement les
trois pages du pont.

## Régénérer

```sh
python3 SCOSWAMP.MORE/MUSIC/midi_to_mb.py \
    SCOSWAMP.MORE/MUSIC/propositions/riviere/SilverSwan.mid \
    SCOSWAMP.MORE/MUSIC/propositions/riviere/RIVER.MB.BIN \
    --bpm 136 --vol 13,9,11 \
    --wav SCOSWAMP.MORE/MUSIC/propositions/riviere/RIVIERE.wav
```
