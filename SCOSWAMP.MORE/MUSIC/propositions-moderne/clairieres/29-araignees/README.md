# Clairière 29 — Tente aux araignées, le Maître des Araignées (`hub` 165)

**`SPIDERS.MB.BIN` — 1 900 octets, 45,1 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 144 | « des milliers de fils forment des guirlandes entre les arbres » — au centre, une tente somptueuse, un homme à la barbe blanche, l'Amulette d'Argent en forme d'araignée ; l'Anneau de Cuivre se réchauffe |
| 345 | le retour : la clairière est en feu, un immense brasier, −1 ENDURANCE |
| 354 | l'Amulette arrachée au cadavre : une étincelle, et tout s'embrase |
| 165 | la petite clairière à deux chemins, à peine protégée des vents |

Zone de référence : **`danger`** (`DANGER.MB`, *Ce qui Attend Sous l'Eau*).

## La pièce

| | |
| --- | --- |
| Titre | **Le Fil d'Argent** |
| Source | composition originale, `araignees.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | des fils qui ne retombent jamais au même endroit — puis la clairière prend feu |
| Mode | **do♯ phrygien** (do♯ **ré** mi fa♯ sol♯ la si) |
| Tempo | **150** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (4) — l'incendie (4) — A' (8) |
| Durée | 28 mesures à 4/4 = **45,1 s** |
| Taille | **1 900 octets** (tampon de zone : 2 304) |
| Notes | 367 hauteurs + **113 coups de batterie**, **0 abandonnée** |

Les deux procédés sont intacts. Celui de `danger` : demi-ton phrygien ré–do♯,
bourdon immobile, crescendo par la **densité** et non par le volume, puisque le
lecteur n'a pas de volume par note. Celui de la clairière : la **toile**, une
cellule de **trois** sons dans des mesures de **quatre** temps.

**Ce que la révision change.**

* **La toile ne se réinitialise plus.** Auparavant l'arpège repartait à chaque
  appel ; il roule maintenant d'un bout à l'autre du morceau, et son compteur
  avance même sous les mesures de réponse — si bien qu'il retombe de l'autre
  côté du cycle. Les fils se croisent et ne se superposent jamais.
* **Le crochet** : `do♯ · ré · do♯`, le demi-ton, puis la chute de quarte sur
  sol♯. Énoncé quatre fois (mesures 5, 9, 21 à l'octave, 26).
* **La batterie EST le feu, et rien d'autre.** Deux charlestons isolés mesure 14
  — l'araignée pose un pied — puis plus rien jusqu'à la mesure 17, où le
  charleston se met à crépiter, les toms montent, et cela ne s'arrête plus. La
  batterie ne marque aucun temps avant l'incendie : elle est l'incendie.
* **Une vraie partie B** (mesures 13-16) : la majeur et mi majeur, registre haut,
  la tente somptueuse — la seule douceur du morceau.
* **La réponse** : mesures 8, 12 et 16, la toile répond au chant en reprenant le
  crochet.
* **La surprise** : mesures 19 et 27, **sol♯ majeur**. Une sensible et une tierce
  majeure, deux notes étrangères au mode : le feu éclaire ce que le phrygien
  tenait dans l'ombre.
* **L'arc** : la toile passe de la noire à la croche, la basse de la blanche à
  la noire, la batterie de rien à tout — en une mesure, la 17.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | F♯5..A6 | 75 |
| 1 | gauche | contre-chant | E♭3..A4 | 66 |
| 2 | **gauche** | bourdon de do♯, une seule note tenue | C♯2 | 1 |
| 3 | **droite** | la toile : trois sons qui roulent sans jamais se recaler | A3..E5 | 147 |
| 4 | droite | basse — blanche avant l'incendie, noire après | E2..G♯3 | 78 |
| 5 | **droite** | **BATTERIE** — charleston fermé 73, grosse caisse 19, caisse claire 12, tom 8, cymbale 1 | bruit | 113 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/29-araignees
python3 araignees.py
python3 ../../../midi_to_mb.py araignees.mid SPIDERS.MB.BIN \
    --bpm 150 --max 2304 --wav ARAIGNEES.wav
```
