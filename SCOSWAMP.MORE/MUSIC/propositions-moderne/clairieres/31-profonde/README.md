# Clairière 31 — La rivière profonde (`hub` 044)

**`DEEPWATER.MB.BIN` — 1 894 octets, 49,7 s, boucle, avec batterie.**

## Ce que la clairière raconte

| Page | Ce qu'on y lit |
| ---: | --- |
| 090 | « celui qui se trouve devant vous est beaucoup plus profond. La rivière tourbillonne en remous : qui sait quelles créatures se cachent dans son lit ? » |
| 044 | la traversée à pied : sur l'autre rive, de grosses sangsues, un dé d'ENDURANCE perdu |
| 254 | la Pierre de Flétrissure : l'arbre s'abat, fait pont, puis se décompose dans le courant |
| 370 | la Pierre de Glace : un pont solide se forme à la surface |

Zone de référence : **`riviere`** (`RIVER.MB`, *Le Pont sur la Croupie*).

## La pièce

| | |
| --- | --- |
| Titre | **L'Eau Noire** |
| Source | composition originale, `profonde.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | on ne touche pas le fond : la plus longue boucle des onze, et la seule qui ne se pose jamais |
| Mode | **sol dorien** (sol la si♭ do ré **mi** fa) |
| Tempo | **136** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (8) — A' (8) |
| Durée | 28 mesures à 4/4 = **49,7 s** |
| Taille | **1 894 octets** (tampon de zone : 2 304) |
| Notes | 456 hauteurs + **14 coups de batterie**, **0 abandonnée** |

Les deux marques de `riviere` sont gardées, et la révision les a rendues plus
strictes : l'arpège de croches **ne s'arrête jamais** — pas une mesure, pas une
réponse ne l'interrompt — et le bourdon reste posé sur la **quinte** (un ré sous
un sol dorien). Le dessin du remous n'a pas bougé non plus : `0-2-1-2-0-1-2-1`.

**Ce que la révision change.**

* **La batterie de cette pièce est de l'eau, et rien d'autre.** Neuf nappes de
  bruit longues — 0,6 à 1,2 seconde chacune, la cymbale tenue trente à soixante
  ticks — et quelques clapotis de charleston ouvert. **Pas un seul coup sec, pas
  un temps marqué.** Sur un AY, le canal de bruit *est* le sifflement de l'eau ;
  c'est la seule des onze où il ne bat rien du tout. Deux grosses caisses
  sourdes, une seule fois, sont ce qui touche le fond.
* **Le crochet** : `ré · sol | si♭ · la`, quarte montante pointée puis retombée.
  Énoncé quatre fois (mesures 5, 9 sur ré mineur, 21 à l'octave, et en croches
  par l'arpège).
* **La réponse sans rupture** : mesures 8, 12 et 16, le chant tient une ronde et
  l'arpège lui répond — mais en croches continues, le remous se contentant de
  prendre la forme d'une phrase. Le courant ne s'arrête pas pour parler.
* **Une vraie partie B** (mesures 13-20) : le do majeur du mode dorien — le mi
  bécarre sous une armure à si♭ — prend le dessus. C'est la surface, vue d'en
  dessous, et c'est la seule clarté du morceau.
* **La surprise** : mesures 26-27, **le bourdon descend enfin sur le sol**. Tout
  le morceau flotte sur la quinte ; deux mesures durant, on touche le fond —
  puis la pédale remonte sur le ré et la boucle repart en suspension.
* **L'arc** : la basse passe de la ronde à la noire pointée, le contre-chant du
  souffle tenu à la blanche, les nappes de bruit de une à quatre par phrase.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie | D5..B♭6 | 73 |
| 1 | gauche | contre-chant | D3..A4 | 103 |
| 2 | **gauche** | bourdon sur la **quinte**, puis sur le sol (mes. 26-27) | D2..G2 | 3 |
| 3 | **droite** | le remous : croches ininterrompues, réponses comprises | A3..E5 | 179 |
| 4 | droite | basse | E2..G3 | 98 |
| 5 | **droite** | **BATTERIE** — nappes : cymbale 6, charleston ouvert 6, grosse caisse 2 | bruit | 14 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 59/41.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/31-profonde
python3 profonde.py
python3 ../../../midi_to_mb.py profonde.mid DEEPWATER.MB.BIN \
    --bpm 136 --max 2304 --wav PROFONDE.wav
```
