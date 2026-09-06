# Clairière 20 — Trois chemins herbeux

**`GRASSLAND.MB.BIN` — 1 493 octets, 35,5 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **047** |
| Pages | 047 |
| Case | (4,4) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | S → 290 (orques), E → 031 (bassin de cristal), O → 118 (scorpions) |
| Contenu | rien — mais six pages y mènent (`CARTOGRAPHIE.md` § 2.3) |

« Rien d'intéressant n'y apparaît à première vue ; l'air est lourd et calme.
Trois sentiers permettent de quitter cette clairière : sud, est et ouest. Le
sentier du sud semble plus humide ; l'est offre une lueur d'horizon ; l'ouest
est étroit et bordé d'arbres serrés. »

## La pièce

| | |
| --- | --- |
| Titre | **Trois Chemins Herbeux** |
| Source | composition originale, `herbeux.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | une clairière où il n'arrive rien : la zone, en plus clair et plus vide |
| Mode | **ré dorien** (ré mi fa sol la **si** do) |
| Tempo | **150** à la noire (145 auparavant) |
| Forme | intro (4) + **trois phrases de six mesures**, une par sentier |
| Durée | 22 mesures à 4/4 = **35,5 s** |
| Taille | **1 493 octets** (tampon de zone : 2 304) |
| Notes | 326 de hauteur + **48 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le **bourdon de tonique immobile** sur
le **même ré** que `SOUTHSWAMP.MB`, et la même marche modale. C'est la plus proche
de la zone des douze — voulu : c'est la clairière la plus neutre du jeu.

**Ce qui lui appartient :** le mode dorien, si naturel au lieu de si bémol, et
la forme en trois phrases, une par sentier, trois cadences, aucun choix imposé.

## Ce que la révision a changé

Les trois phrases sont devenues **trois variations d'un même crochet**, et
chaque sentier a désormais sa propre basse **et** sa propre batterie :

| sentier | mesures | le crochet | la basse | la batterie |
| --- | :---: | --- | --- | --- |
| **sud**, « plus humide » | 5-10 | tel quel, sur ré mineur | deux blanches | grosse caisse seule au premier temps |
| **est**, « une lueur d'horizon » | 11-16 | **transposé sur sol majeur**, le seul endroit clair | brève-longue | complète : `K.H.S.H.` |
| **ouest**, « étroit et bordé d'arbres serrés » | 17-22 | redit **tel quel** | quatre noires | **rien**, puis tout |

- **une réponse** : mesures 10, 16 et 20, à chaque cadence, le chant tient sa
  ronde et l'arpège — la voix 3, à **droite** — répond le crochet une octave
  plus bas. Trois questions à gauche, trois réponses à droite : les trois
  sentiers se répondent, et aucun ne s'impose ;
- **un rythme harmonique varié** : neuf mesures changent d'accord au milieu, et
  la basse y marche en deux pas quelle que soit la phrase ;
- **la surprise** : mesure 18, un **si bémol majeur**. Le si **naturel** est
  précisément ce qui fait le dorien de cette pièce et sa différence d'avec la
  zone ; l'abaisser d'un demi-ton ferme le troisième sentier d'un coup. La
  batterie s'y tait deux mesures ;
- **une cadence affirmée** : mesure 21, un **la majeur** avec son do♯, la seule
  sensible du morceau, qui ramène au ré mineur ;
- **un arc de densité** qui suit les trois sentiers : rien, puis la caisse seule,
  puis la batterie complète, puis le silence, puis le plein ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **la** du
  début.

Le tempo passe de 145 à **150**, celui de la zone : la clairière la plus neutre
du jeu sonne maintenant exactement au pas de `SOUTHSWAMP.MB`.

## La batterie

Une **marche légère**, presque un pas dans l'herbe. Sa particularité est qu'elle
**change à chaque sentier** et disparaît au troisième : c'est elle qui rend les
trois phrases distinctes à l'oreille, là où l'harmonie seule ne suffisait pas.
48 coups, 144 octets.

Elle prend la **voix 5, à droite** : cinq parties de hauteur, et c'est la voix
d'accords tenus qui a cédé la place — le bourdon de tonique est le procédé de la
zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/20-herbeux/herbeux.mid --bpm 150`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, le crochet trois fois | G4..E6 | 56 | 97 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | D3..A4 | 100 | 94 % |
| 2 | **gauche** | bourdon de ré (la tonique) | D2 | 6 | 100 % |
| 3 | **droite** | arpège en sauts de quinte, et les trois réponses | G3..C5 | 96 | 95 % |
| 4 | droite | basse — une par sentier | G2..A♯3 | 68 | 96 % |
| 5 | **droite** | **batterie** — 18 grosse caisse, 18 charleston, 9 caisse claire, 2 toms, 1 cymbale | bruit | 48 | 6 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/20-herbeux
python3 herbeux.py
python3 ../../../midi_to_mb.py herbeux.mid GRASSLAND.MB.BIN \
    --bpm 150 --max 2304 --wav HERBEUX.wav
```
