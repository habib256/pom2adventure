# Clairière 28 — La clairière des Arbres-Épées (`hub` 022)

**`SWORDTREES.MB.BIN` — 2 198 octets, 40,4 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 157 | l'entrée : des arbres petits, vert foncé, aux branches qui ressemblent à des bras — « chaque bras tient une épée à son extrémité » |
| 279 | le retour : « les branches des terribles Arbres-Épées ont déjà repoussé » |
| 022 | les pousses rapides, les graines en poche, et trois directions à choisir sans tarder |

Zone de référence : **`danger`** (`DANGER.MB`, *Ce qui Attend Sous l'Eau*).

## La pièce

| | |
| --- | --- |
| Titre | **Les Bras qui Repoussent** |
| Source | composition originale, `arbresepees.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on coupe le motif, il repousse ailleurs — et une lame finit par couper un temps entier |
| Mode | **fa phrygien** (fa **sol♭** la♭ si♭ do ré♭ mi♭) |
| Tempo | **166** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (8) — mesure courte (1) — A' (7) |
| Durée | 28 mesures à 4/4 **moins un temps** = **40,4 s** |
| Taille | **2 198 octets** (tampon de zone : 2 304) |
| Notes | 465 hauteurs + **98 coups de batterie**, **0 abandonnée** |

Le procédé de `danger` est intact : demi-ton phrygien sol♭–fa, bourdon de fa
immobile. Celui de la clairière aussi : le **canon** court. La cellule
`fa – sol♭ – fa` que le chant lance repousse au contre-chant, une octave plus
bas, la mesure suivante — mesures 6, 19, 21 et 23.

**Ce que la révision change.**

* **Le crochet est la cellule elle-même** : trois notes, deux secondes mineures.
  Le chant l'énonce mesures 5 et 22 (à l'octave) et dans la mesure courte ; le
  contre-chant quatre fois. Rien d'autre dans la pièce ne ressemble à ça.
* **La batterie, ce sont les lames.** Caisse claire sèche sur les temps faibles,
  grosse caisse sur le premier, charleston seulement en A'. Rien à l'intro.
* **Une vraie partie B** (mesures 13-20) : ré♭ et la♭, les deux seuls accords
  majeurs, et le chant qui monte au si♭ 6 — la seule clarté du morceau.
* **La réponse** : mesures 8, 12 et 16, le chant tient une ronde et c'est
  l'arpège, à droite, qui repousse la cellule à sa place.
* **La surprise** : la **mesure 21 n'a que trois temps**. La lame coupe un temps
  à la pièce ; trois coups de caisse claire nus la remplissent, et la reprise
  part décalée. C'est la seule mesure amputée des trente-cinq clairières.
* **L'arc** : deux notes d'arpège par mesure à l'intro et pas de batterie ; huit
  notes et le charleston en A'.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | F5..B♭6 | 70 |
| 1 | gauche | contre-chant — c'est lui qui fait repousser la cellule | E♭3..B♭4 | 79 |
| 2 | **gauche** | bourdon de fa, une seule note tenue | F2 | 1 |
| 3 | **droite** | l'arpège, et les trois repousses de réponse | B♭3..E♭5 | 171 |
| 4 | droite | basse — les lames, jamais arrêtées | F2..A♭3 | 144 |
| 5 | **droite** | **BATTERIE** — caisse claire 48, grosse caisse 37, charleston fermé 12, cymbale 1 | bruit | 98 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/28-arbresepees
python3 arbresepees.py
python3 ../../../midi_to_mb.py arbresepees.mid SWORDTREES.MB.BIN \
    --bpm 166 --max 2304 --wav ARBRESEPEES.wav
```
