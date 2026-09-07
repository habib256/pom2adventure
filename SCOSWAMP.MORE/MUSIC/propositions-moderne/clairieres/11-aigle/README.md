# Clairière 11 — Le nid de l'Aigle (`hub` 202, case 3,2)

**`EAGLE.MB.BIN` — 1 682 octets, 43,1 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 350 | Le nid de l'Aigle | l'arbre immense dans un sol dur et nu, le nid gigantesque, l'AIGLE qui vous observe |
| 331 | Le nid de l'Aigle | de retour : rien que le vieil arbre et le nid |
| 025 | L'aigle s'envole | il crie, tourne en cercle, et s'éloigne |
| 112 | Le grand nid | grimper pour l'examiner, ou repartir |
| 202 | Trois directions | sud, est, ouest |

## La pièce

| | |
| --- | --- |
| Titre | **Le Grand Nid** |
| Source | composition originale, `aigle.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | de la hauteur. Pas une menace : une surveillance, très haut, qui tourne sans se presser |
| Mode | **fa♯ mineur éolien** (fa♯ sol♯ la si do♯ ré mi) |
| Tempo | **156** à la noire (auparavant 152) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **43,1 s** |
| Taille | **1 682 octets** (marge 622 sur le tampon de zone) |
| Notes | 380 de hauteur + **34 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **un crochet** qui chante le rythme du vol : `fa♯ la do♯' si / la fa♯ mi`,
  noire - croche - blanche - croche, exactement la cellule mais mélodique.
  Énoncé trois fois : le chant et l'ostinato battent alors de la même aile ;
- **une réponse** aux mesures 8, 20 et 28 : le chant tient une ronde et l'aile —
  voix 3, à droite — répond. C'est la seule façon d'entendre l'oiseau quand on
  ne le regarde pas ;
- **la surprise** : au B, mesures 17 à 20, **la cellule se retourne** — do♯, la,
  fa♯, la : il ne monte plus, il plonge. Et l'harmonie prend un **ré dièse** sur
  un accord de si majeur, la sixte majeure que l'éolien n'a pas. Puis mesure 20,
  **un temps et demi de silence général** : on perd l'oiseau de vue ;
- **le rythme harmonique varie** : grille à la demi-mesure ; l'arbre tient un
  accord par mesure, le nid en prend deux, et la basse double pendant le
  plongeon ;
- **le tempo monte de 152 à 156**.

## La batterie

**La plus aérée des douze**, trente-quatre coups en quarante-trois secondes.
**Aucune caisse claire, aucun charleston fermé** : une cymbale à chaque entrée,
un charleston ouvert tous les deux temps pour le vol plané, et trois grosses
caisses seulement, celles du plongeon. Le bourdon de do♯ a cédé la place :
entre la cellule très haute et la basse très grave, il ne manque rien.

## Ce qui la relie à `nord`, et ce qui l'en sépare

L'ostinato de la zone bat des croches égales ; celui-ci a un **rythme**, et
c'est tout le sujet : **noire - croche - blanche - croche**, fa♯ - la - do♯ - la.
Un coup d'aile, un second, puis le vol plané sur la note du haut pendant deux
temps, et l'on retombe. La cellule ne bat que quatre fois par mesure au lieu de
huit, et c'est ce qui fait la différence entre courir et planer. Elle est posée
très haut, jusqu'au do♯5, et la mélodie chante au-dessus d'elle.

## Les six voix, mesurées

`python3 ../../verifier.py aigle.mid --bpm 156`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | E5..A6 | 77 |
| 1 | gauche | le contre-chant, détaché | G♯3..B4 | 53 |
| 2 | **gauche** | la basse, tenue puis doublée au plongeon | F♯2..A3 | 102 |
| 3 | **droite** | **l'aile**, et les réponses | E4..C♯5 | 108 |
| 4 | droite | les accords tenus | E3..D♯4 | 40 |
| 5 | **droite** | **LA BATTERIE** — charleston ouvert 28, cymbale 3, grosse caisse 3 | bruit | 34 |

Stéréo mesurée **56/44**, aucune note abandonnée, `verifier.py` conclut `OK`.

Sept pour cent d'occupation à la voix 5 : c'est le minimum des douze avec les
Jardins. Un oiseau qui plane ne fait pas de bruit ; il en fait trois, et on les
compte.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/11-aigle
python3 aigle.py
python3 ../../../midi_to_mb.py aigle.mid EAGLE.MB.BIN \
    --bpm 156 --max 2304 --wav AIGLE.wav
```
