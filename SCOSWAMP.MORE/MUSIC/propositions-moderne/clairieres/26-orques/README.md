# Clairière 26 — Orques des Marais (`hub` 309)

**`ORCS.MB.BIN` — 1 918 octets, 40,8 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 290 | l'embuscade : « une flèche vous frôle la tête en sifflant » — trois orques à la peau rongée par la gale, arcs en main |
| 323 | le retour : s'ils vivent encore, ils gardent l'ENDURANCE qu'ils avaient |
| 352 | la remontée vers le nord, épée en main, au cas où |
| 309 | les trois chemins qui quittent la clairière |

Zone de référence : **`danger`** (`DANGER.MB`, *Ce qui Attend Sous l'Eau*).

## La pièce

| | |
| --- | --- |
| Titre | **Trois Arcs dans la Brume** |
| Source | composition originale, `orques.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | martial : une troupe qui avance, trois arcs, une flèche qui frôle la tête |
| Mode | **ré phrygien** (ré **mi♭** fa sol la si♭ do) |
| Tempo | **166** à la noire (158 auparavant : la troupe avance) |
| Forme | intro (4) — A (8) — B (8) — A' à l'octave (8) |
| Durée | 28 mesures à 4/4 = **40,8 s** |
| Taille | **1 918 octets** (tampon de zone : 2 304) |
| Notes | 383 hauteurs + **105 coups de batterie**, **0 abandonnée** |

Le procédé de `danger` est intact : demi-ton phrygien mi♭–ré, bourdon de ré.

**Ce que la révision change.**

* **C'est devenu une vraie marche.** La grosse caisse tient le pas, si bien que
  le bourdon n'a plus besoin d'être refrappé toutes les deux mesures : il tient,
  et la piece y gagne trente notes. Le tempo monte à 166.
* **Le crochet.** L'appel pointé `la la | ré do` — deux fois la même note, puis
  la quarte — est énoncé quatre fois : mesures 5, 9 (une quarte plus haut),
  21 (à l'octave) et 25 (sur mi♭). Trois arcs, la même flèche.
* **Une vraie partie B** (mesures 13-20) : si♭ et fa, les deux seuls accords
  majeurs du morceau, et le chant qui monte au sol 6.
* **La réponse** : mesures 8, 12, 16 et 28, le chant tient une ronde et l'arpège
  lui rend l'appel une octave plus bas, à droite.
* **La surprise** : mesure 20, le **grand silence**. Tout se fige sur un ré tenu,
  la batterie s'arrête net ; deux coups de caisse claire au dernier temps
  relancent la troupe. C'est la flèche qui passe.
* **L'arc** : un tambour lointain aux mesures 3-4, la marche en A, le charleston
  en B, la marche doublée en A'.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..B♭6 | 72 |
| 1 | gauche | contre-chant | G3..B♭4 | 84 |
| 2 | **gauche** | bourdon de ré, une seule note tenue | D2 | 1 |
| 3 | **droite** | l'arpège pointé, et les quatre appels de réponse | B♭3..D5 | 111 |
| 4 | droite | basse | F2..G3 | 115 |
| 5 | **droite** | **BATTERIE** — grosse caisse 50, caisse claire 32, charleston fermé 21, cymbale 2 | bruit | 105 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 59/41.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/26-orques
python3 orques.py
python3 ../../../midi_to_mb.py orques.mid ORCS.MB.BIN \
    --bpm 166 --max 2304 --wav ORQUES.wav
```
