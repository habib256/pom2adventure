# Clairière 18 — Le pique-nique suspect

**`PICNIC.MB.BIN` — 1 865 octets, 41,2 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **179** |
| Pages | 066 (le pique-nique), 192 (retour chez le Voleur), 179 (le carrefour) |
| Case | (2,4) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | N → 183 (falaise), S → 010, E → 118 (scorpions) |
| Contenu | VOLEUR (10/9 en 267) ; **Cape Rouge** (`386 G CAPE`) |

« Un petit homme à l'air joyeux est assis par terre, le dos appuyé contre le
tronc d'un arbre. Il mange du fromage, un panier à pique-nique ouvert à côté de
lui. » Puis : « L'Anneau de Cuivre diffuse une chaleur autour de votre doigt qui
vous avertit : ne vous fiez pas. Bientôt, vous comprenez qu'il s'agit d'un
VOLEUR. »

## La pièce

| | |
| --- | --- |
| Titre | **Le Repas du Voleur** |
| Source | composition originale, `piquenique.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | une valse aimable qui trébuche — la seule pièce à trois temps |
| Mode | **fa dorien** (fa sol la♭ si♭ do **ré** mi♭) |
| Tempo | **176** à la noire |
| Forme | intro (4) — A (12) le repas — B (12) l'Anneau chauffe — A' (12) la reprise empoisonnée |
| Durée | 40 mesures à **3/4** = **41,2 s** |
| Taille | **1 865 octets** (tampon de zone : 2 304) |
| Notes | 370 de hauteur + **120 coups de batterie** — le plus gros compte des douze — **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le **bourdon de tonique immobile** (fa)
et la marche modale large. **Ce qui lui appartient :** le **3/4**, seule des
trente-cinq clairières à ne pas être à quatre temps, et le **sol bémol majeur**
qui trahit le Voleur — le demi-ton phrygien de la zone `danger`, cité à
découvert dans une valse.

## Ce que la révision a changé

- **un crochet**, la première phrase de la valse : fa - la♭ - do | si♭ tenu, la♭.
  Mesure 5, repris mesure 11 sur si bémol, redit tel quel mesure 29, et sa tête
  revient encore mesure 39, juste avant la boucle. **Quatre énoncés** ;
- **une réponse** : mesures 8, 20 et 32, le chant tient une blanche pointée et
  l'arpège — la voix 3, à **droite** — répond `fa la♭ do`, le crochet une octave
  plus bas. C'est le petit homme qui reprend la chanson la bouche pleine ;
- **un rythme harmonique varié** : treize mesures changent d'accord au
  **troisième temps** — deux temps pour le premier accord, un pour le second —
  ce qui donne à la valse le boitement qu'on entend dans les vraies ;
- **la surprise, et c'est une hémiole** : mesures 25-26, la valse trébuche. Le
  chant, l'arpège, la basse **et** la batterie passent tous en groupes de
  **deux** temps sur six — trois pas au lieu de deux mesures — et c'est
  exactement là que le **sol bémol** arrive. Deux mesures à 3/4 qui sonnent comme
  trois à 2/4 : la seule mesure impaire du dossier, obtenue sans changer de
  chiffrage et sans toucher au module ;
- **une cadence affirmée, deux fois** : mesures 28 et 38, un **do majeur** avec
  son mi naturel, étranger au mode, aux deux jointures qui comptent ;
- **un arc de densité** : intro à deux sons par mesure et sans batterie, A la
  valse, B qui se serre à la caisse claire, l'hémiole, A' pleine avec le
  charleston doublé ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **do** du
  début.

## La batterie

Celle d'une **valse** : grosse caisse au premier temps, charleston aux deux
autres (`K.H.H.`) ; caisse claire au troisième temps dès que l'Anneau chauffe
(`K.H.S.`) ; charleston doublé en A' (`K.HSH.`).

Et puis l'**hémiole** : mesures 25-26, elle abandonne le motif et frappe sur les
temps **1, 3 et 5** des six — grosse caisse, caisse claire, grosse caisse — en
faisant trébucher tout le monde avec elle. C'est le seul endroit des douze
pièces où la batterie ne suit pas la mesure : elle la contredit.

120 coups, 360 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique est le procédé de la zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/18-piquenique/piquenique.mid --bpm 176`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, la valse | A♯4..F6 | 94 | 95 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | F♯3..F4 | 96 | 95 % |
| 2 | **gauche** | bourdon de fa (la tonique) | F2 | 5 | 100 % |
| 3 | **droite** | arpège, un son d'accord par temps, et les trois réponses | A♯3..D♯5 | 96 | 95 % |
| 4 | droite | basse, fondamentale de blanche et quinte de noire | G2..A♯3 | 79 | 96 % |
| 5 | **droite** | **batterie** — 58 charleston, 36 grosse caisse, 24 caisse claire, 1 tom, 1 cymbale | bruit | 120 | 11 % |

`OK — 6 voix employées, stéréo 59/41, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/18-piquenique
python3 piquenique.py
python3 ../../../midi_to_mb.py piquenique.mid PICNIC.MB.BIN \
    --bpm 176 --max 2304 --wav PIQUENIQUE.wav
```
