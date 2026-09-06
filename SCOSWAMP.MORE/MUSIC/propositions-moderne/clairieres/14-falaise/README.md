# Clairière 14 — Sommet de la falaise

**`CLIFF.MB.BIN` — 1 447 octets, 40,3 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **183** |
| Pages | 183 |
| Case | (2,3) |
| Zone de référence | `riviere` (`RIVER.MB`) |
| Sorties | S → 066, O → 295 ; **N et E = plonger = mort** (crocodile) |

« Au lieu du morne feuillage, c'est le ciel qui s'ouvre. Vous atteignez le
sommet d'une haute falaise dominant la rivière. » En contrebas, les eaux
boueuses, les crocodiles paresseux ; plus loin à l'est, le pont, inaccessible.

## La pièce

| | |
| --- | --- |
| Titre | **Le Ciel s'Ouvre** |
| Source | composition originale, `falaise.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | l'altitude : ça monte, puis le sol s'ouvre sous les pieds |
| Mode | **si dorien** (si do♯ ré mi fa♯ **sol♯** la) |
| Tempo | **144** à la noire (140 auparavant) |
| Forme | intro (4) — A (8) — B (8) — A' (4) |
| Durée | 24 mesures à 4/4 = **40,3 s** |
| Taille | **1 447 octets** (tampon de zone : 2 304) |
| Notes | 365 de hauteur, **aucune batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `riviere` :** le mode dorien et le **bourdon sur
la quinte** — fa♯, pas si.

**Ce qui lui appartient :** l'arpège n'y tourne plus sur trois sons mais en
atteint **quatre, l'octave comprise** — une figure qui s'ouvre au lieu de
tourner. La mélodie monte jusqu'au **si aigu de la mesure 21**, le point le plus
haut du dossier.

## La batterie : il n'y en a pas, et c'est un choix

C'est la **seule des douze sans percussion**. Un seul coup de bruit coûterait la
voix 5 et ramènerait la pièce à cinq parties de hauteur ; au sommet de la
falaise, c'est la largeur qui compte, pas la frappe. Les **six** voix sont donc
gardées — mélodie, arpège à quatre sons, contre-chant, accords tenus, basse en
blanches et bourdon. Le vent n'a pas de tambour.

C'est aussi ce qui permet à cette pièce d'être la seule à garder à la fois le
bourdon **et** la voix d'accords tenus, et donc la texture la plus pleine des
douze pour la plus petite taille.

## Ce que la révision a changé

- **un crochet**, deux mesures : si - fa♯ - la - si, la quinte montée d'un trait
  puis la septième et l'octave, et la retombée sur la quinte. Mesure 5, varié
  mesure 9, et redit **à l'octave** mesure 21 où il touche le si aigu ;
- **une réponse** : mesures 8, 11 et 15, le chant tient une ronde et l'arpège —
  la voix 3, à droite — reprend le crochet une octave plus bas ;
- **un rythme harmonique varié** : sept mesures changent d'accord au milieu, et
  les mesures 15 à 18 n'en changent presque plus du tout — le ciel s'ouvre,
  l'harmonie s'arrête ;
- **la surprise**, et c'est la plus grosse que puisse subir une pièce bâtie sur
  un bourdon : **la pédale se déplace**. Mesures 15 à 18, le fa♯ descend au
  **mi** — la falaise s'ouvre sous les pieds — puis remonte mesure 19. Les
  accords de ces quatre mesures (la, la, ré, la) sont choisis pour que le mi n'y
  soit **jamais** la fondamentale : le procédé de la zone tient, même déplacé ;
- **une cadence affirmée** : mesure 20, un **fa♯ majeur** avec son la♯, la seule
  sensible du morceau. C'est aussi le seul instant où le bourdon est la
  fondamentale de l'accord — la dominante, et elle seule, a le droit de poser le
  pied ;
- **un arc de densité** : intro en blanches d'arpège, A en croches, B qui
  s'ouvre en rondes sur la pédale déplacée, A' à l'octave supérieure ;
- **une fin qui prépare la boucle** : la dernière mesure retombe de si à fa♯, la
  quinte par laquelle la pièce va repartir.

Le tempo passe de 140 à **144** : la pièce respire mieux et gagne 1,3 s de
marge sous la limite de 50 s.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/14-falaise/falaise.mid --bpm 144`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie | A4..B6 | 56 | 96 % |
| 1 | gauche | médiane (contre-chant) | G♯3..D5 | 55 | 96 % |
| 2 | **gauche** | basse, deux blanches ouvertes | A2..B3 | 59 | 96 % |
| 3 | **droite** | arpège à quatre sons, et les trois réponses | A3..E5 | 91 | 94 % |
| 4 | droite | médiane (accords tenus) | E3..B4 | 97 | 94 % |
| 5 | **droite** | bourdon de fa♯ — **et de mi, mesures 15 à 18** | E2..F♯2 | 7 | 100 % |

`OK — 6 voix employées, stéréo 50/50, aucune note abandonnée.` C'est la stéréo la
mieux équilibrée des douze : sans batterie, les six parties de hauteur se
répartissent trois et trois.

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/14-falaise
python3 falaise.py
python3 ../../../midi_to_mb.py falaise.mid CLIFF.MB.BIN \
    --bpm 144 --max 2304 --wav FALAISE.wav
```
