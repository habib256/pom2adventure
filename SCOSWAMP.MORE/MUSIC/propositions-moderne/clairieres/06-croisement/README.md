# Clairière 6 — Le croisement (`hub` 121, case 2,1)

**`CROSSROADS.MB.BIN` — 2 177 octets, 44,8 s, boucle.**

## Les pages

| Page | Titre | Ce qui s'y passe |
| ---: | --- | --- |
| 121 | Le croisement | quatre directions ; nord 170, sud 014, est 275, ouest 218 |

Une seule page, et c'est la clairière la plus traversée du Marais nord : c'est
par elle qu'on passe pour aller du Patrouilleur au Géant, du Feu Follet au
Scorpion.

## La pièce

| | |
| --- | --- |
| Titre | **Quatre Chemins** |
| Source | composition originale, `croisement.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | l'hésitation, pas la peur. On est arrêté au milieu, et la même question se pose quatre fois |
| Mode | **mi éolien** (mi fa♯ sol la si do ré) — celui de la zone, délibérément |
| Tempo | **150** à la noire (auparavant 144) |
| Forme | intro (4) — nord (6) — sud (6) — est (6) — ouest (6) |
| Durée | 28 mesures à 4/4 = **44,8 s** |
| Taille | **2 177 octets** (marge 127 sur le tampon de zone) |
| Notes | 432 de hauteur + **88 coups de batterie**, **0 abandonnée** |
| Voix | **cinq parties de hauteur** + la batterie sur la voix 5 |

## Ce que la révision a changé

- **le crochet est la tête de panneau** : deux mesures, `mi si ré' / si la sol`,
  qui reviennent au début de **chacune des quatre routes**. La même question
  posée quatre fois, la dernière une octave plus haut ;
- **une réponse par panneau** : à la sixième mesure de chaque route le chant
  tient une ronde et la cellule — voix 3, à droite — répond. Quatre questions à
  gauche, quatre réponses à droite ;
- **la surprise** : le quatrième panneau, l'ouest, passe en **si majeur**. Le ré
  dièse n'appartient pas au mode : c'est la seule route qui ment, et la cellule
  ment avec elle, deux mesures sur six. Juste avant, **un temps et demi de
  silence général** et un roulement de tom : le passage manque ;
- **le rythme harmonique varie** : grille à la demi-mesure. L'arrêt du carrefour
  tient un accord par mesure ; dès qu'une route s'engage, les accords vont à la
  demi-mesure. Et **chaque route a sa basse** : elle marche au nord et à
  l'ouest, elle pose et lâche au sud et à l'est ;
- **le tempo monte de 144 à 150**.

## La batterie

**Une par direction**, et c'est la seule des douze qui change de batterie quatre
fois. Rien au carrefour : on est arrêté. Marche au nord, contretemps au sud,
charleston seul à l'est, pression à l'ouest — la route qui ment est aussi celle
qui pousse. Le bourdon de mi a cédé la place.

## Ce qui la relie à `nord`, et ce qui l'en sépare

C'est la variation la plus littérale des huit clairières du nord, et c'est
voulu : le croisement est le **centre** de la zone. Même mode, même basse. Ce
qui change est la **forme** : l'ostinato est fixe **à l'intérieur d'un panneau**
et change à chaque panneau.

| Panneau | Mesures | Cellule | Batterie |
| --- | :---: | --- | --- |
| nord | 5-10 | si - sol - la - mi | `K.H.S.H.` — la marche |
| sud | 11-16 | la - mi - fa♯ - ré | `K..H..S.` — le contretemps |
| est | 17-22 | ré - sol - si - sol | `..H...H.` — presque rien |
| ouest | 23-28 | mi - la - do - la, puis **ré♯ - la - si - fa♯** | `K.S.KKS.` — la pression |

## Les six voix, mesurées

`python3 ../../verifier.py croisement.mid --bpm 150`

| voix | côté | ce qui s'y trouve | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | la mélodie, seule | D5..B6 | 75 |
| 1 | gauche | le contre-chant, détaché | A3..C5 | 71 |
| 2 | **gauche** | la basse, marchée ou posée selon la route | E2..G3 | 80 |
| 3 | **droite** | **les quatre cellules**, et les quatre réponses | D4..C5 | 168 |
| 4 | droite | les accords tenus | F♯3..B4 | 38 |
| 5 | **droite** | **LA BATTERIE** — grosse caisse 30, charleston fermé 30, caisse claire 24, tom 3, cymbale 1 | bruit | 88 |

Stéréo mesurée **55/45**, aucune note abandonnée, `verifier.py` conclut `OK`.

Les quatre cellules restent dans la même voix, donc du même côté : quand
l'ostinato change, c'est la clairière qui tourne, pas la stéréo.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/06-croisement
python3 croisement.py
python3 ../../../midi_to_mb.py croisement.mid CROSSROADS.MB.BIN \
    --bpm 150 --max 2304 --wav CROISEMENT.wav
```
