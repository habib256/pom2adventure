# Clairière 16 — Le Perroquet et la Maîtresse des Oiseaux

**`BIRDS.MB.BIN` — 2 002 octets, 40,3 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **304** |
| Pages | 304 (le Perroquet), 149 (la clairière aux oiseaux), 217 (retour forcé) |
| Case | (0,4) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | aucune orientée — cul-de-sac tropical, on ressort par 217 → 250 |

« Le Marais change d'aspect. Il devient moins lugubre et ressemble de plus en
plus à une jungle tropicale. Des oiseaux aux couleurs éclatantes volent parmi
les arbres. » Un gros Perroquet rouge et jaune parle. Page 149 : la Maîtresse
n'est pas là, il ne reste que des plumes éparses et « un silence léger ».

## La pièce

| | |
| --- | --- |
| Titre | **La Maîtresse des Oiseaux** |
| Source | composition originale, `oiseaux.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | la poche tropicale : la seule clairière claire du Marais sud |
| Mode | **mi dorien** (mi fa♯ sol la si **do♯** ré) |
| Tempo | **168** à la noire |
| Forme | intro (4) — A (8) les oiseaux — B (8) le silence léger — A' (8) |
| Durée | 28 mesures à 4/4 = **40,3 s** |
| Taille | **2 002 octets** (tampon de zone : 2 304) |
| Notes | 430 de hauteur + **73 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le **bourdon de tonique immobile** — mi,
d'un bout à l'autre — et la marche modale large. **Ce qui lui appartient :** le
mode dorien au lieu de l'éolien, et l'**arpège en sauts de quinte** : au lieu de
monter son accord degré par degré, il bondit de la fondamentale à la quinte et
retombe — des oiseaux, pas de l'eau.

## Ce que la révision a changé

- **un crochet**, et c'est le cri du Perroquet : deux croches accolées, un saut,
  une note tenue — `mi sol si . la | fa♯ la ré . si`. Mesure 5, redit **tel
  quel** mesure 9, repris mesure 21, transposé mesure 26. **Quatre énoncés** :
  c'est le babil qu'on emporte ;
- **une réponse, et c'est littéralement un second oiseau** : mesures 8, 11 et
  15, le chant tient sa note et l'arpège — la voix 3, à **droite** — répond le
  même cri, plus bas. Le premier appelle à gauche, le second répond à droite ;
- **un rythme harmonique varié** : dix mesures changent d'accord au milieu, et
  les mesures 17-18 n'en changent plus du tout ;
- **la surprise** : mesures 17-18, un **do majeur** — le do **naturel**, alors
  que tout le mode repose sur le do♯. C'est la page 149 : la clairière où la
  Maîtresse n'est pas, les plumes éparses au sol. La couleur tourne au gris en
  une seconde, et la batterie s'y réduit à un seul charleston ouvert ;
- **une cadence affirmée** : mesure 20, un **si majeur** avec son ré♯, la seule
  sensible du morceau ;
- **un arc de densité** : intro sans batterie, A le babil, B en blanches presque
  nu, A' plein et doublé de charleston ;
- **une fin qui prépare la boucle** : la dernière mesure redescend sur le **si**
  du début.

## La batterie

Un **tambourin**, pas une marche — cette clairière est un morceau de jungle, pas
un chemin. Charleston et grosse caisse légers en A (`K.H...H.`) ; en B, **un
seul charleston ouvert toutes les deux mesures**, ce qui donne les quatre
mesures les plus vides des douze pièces ; un petit roulement de toms et de
caisse mesure 20 ; puis la frappe pleine en A', charleston doublé sur la
dernière croche (`K.H.S.HH`).

73 coups, 219 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique est le procédé de la zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/16-oiseaux/oiseaux.mid --bpm 168`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, le cri du Perroquet | A4..G6 | 77 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | D3..A4 | 112 | 94 % |
| 2 | **gauche** | bourdon de mi (la tonique) | E2 | 7 | 100 % |
| 3 | **droite** | arpège en sauts de quinte, et les trois réponses | G3..F♯5 | 147 | 92 % |
| 4 | droite | basse | G2..B3 | 87 | 95 % |
| 5 | **droite** | **batterie** — 40 charleston, 16 grosse caisse, 10 caisse claire, 4 charleston ouvert, 2 toms, 1 cymbale | bruit | 73 | 7 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/16-oiseaux
python3 oiseaux.py
python3 ../../../midi_to_mb.py oiseaux.mid BIRDS.MB.BIN \
    --bpm 168 --max 2304 --wav OISEAUX.wav
```
