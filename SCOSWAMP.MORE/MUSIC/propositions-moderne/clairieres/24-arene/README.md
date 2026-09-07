# Clairière 24 — La clairière des combats

**`ARENA.MB.BIN` — 2 128 octets, 41,3 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **227** |
| Pages | 010 (la clairière des combats), 142 (silence après la bataille), 227 (le choix des chemins) |
| Case | (2,5) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | N → 066 (pique-nique), E → 388, O → 320 (la Licorne) |
| Contenu | traces d'un combat, cadavre → **Aimant d'Or** (`059 G AI`, maudit : `063 GX AI`) |

« L'endroit porte les marques récentes d'un combat : le sol est foulé, l'herbe
humide tachée de sang, et deux flèches sont encore plantées dans un arbre un
peu plus loin. Vous pouvez fouiller la clairière pour découvrir indices ou
butin, mais rester risque d'attirer l'attention d'ennemis cachés. » Page 227 :
« Le silence pèse, seulement rompu par le bourdonnement des mouches. »

## La pièce

| | |
| --- | --- |
| Titre | **Ce qui Reste du Combat** |
| Source | composition originale, `arene.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | martial, mais après coup : on ne se bat pas, on relève des traces |
| Mode | **mi éolien** (mi fa♯ sol la si do ré) |
| Tempo | **164** à la noire (160 auparavant) |
| Forme | intro (4) — A (8) les traces — B (8) la fouille — A' (8) |
| Durée | 28 mesures à 4/4 = **41,3 s** |
| Taille | **2 128 octets** — la plus grosse des douze (tampon de zone : 2 304, marge 176) |
| Notes | 437 de hauteur + **99 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le **bourdon de tonique immobile** et la
marche i-VI-III-VII (Em-C-G-D), celle de `SOUTHSWAMP.MB`.

**Ce qui lui appartient :** le **rythme pointé**. Le long-bref du premier temps
revient à chaque mesure de A et de A', et c'est tout ce qui sépare cette pièce
d'un thème de voyage.

## Ce que la révision a changé

- **un crochet entièrement pointé** : mi . sol - si | do . si - sol. C'est le
  rythme de la clairière devenu une phrase. Mesure 5, redit mesure 9, repris
  mesures 21 et 24, porté **à l'octave** mesure 26 — **cinq énoncés**, le plus
  grand nombre des douze. C'est un champ de bataille : on y repasse ;
- **une réponse** : mesures 8, 11 et 17, le chant tient et l'arpège — la voix 3,
  à **droite** — répond le crochet, pointé lui aussi, une octave plus bas. Deux
  voix qui se cherchent dans une clairière vide : c'est exactement ce que le
  texte promet à qui s'attarde ;
- **un rythme harmonique varié** : **quinze** mesures sur vingt-huit changent
  d'accord au milieu — le plus haut taux des douze — et les deux mesures de si
  mineur n'en changent plus du tout : la fouille s'arrête sur place ;
- **la surprise, en deux temps**. Mesures 18-19, **la batterie se tait
  complètement** et la basse tient une **ronde** : c'est le moment où l'on entend
  quelque chose. Puis mesure 19 un **fa majeur** — le second degré abaissé, le
  demi-ton phrygien de la zone `danger`, posé entier sur le bourdon de mi qu'il
  frotte. Les ennemis cachés ne sont plus une promesse ;
- **une cadence affirmée** : mesure 20, un **si majeur** avec son ré♯, la seule
  sensible du morceau ; elle revient mesure 27 ;
- **un arc de densité** : grosse caisse seule mesure 3, marche pointée en A,
  charleston en B, deux mesures de rien, roulement de toms, puis A' plein sur
  huit mesures ;
- **une fin qui prépare la boucle** : la dernière mesure redescend sur le **si**
  du début, et l'on repasse.

Le tempo passe de 160 à **164**.

## La batterie

Une **marche martiale calée sur le pointé du chant** : grosse caisse au premier
temps **et sur la croche pointée qui suit** (`K..KS...`), exactement là où la
mélodie place son long-bref. En B le charleston entre (`K.HKS.H.`). Puis
**deux mesures de rien** — la seule chose qui puisse rendre audible « le silence
pèse » — un roulement de trois toms et une caisse claire, et A' repart sur huit
mesures pleines avec cymbale.

99 coups, 297 octets. Elle prend la **voix 5, à droite** : cinq parties de
hauteur, et c'est la voix d'accords tenus qui a cédé la place — le bourdon de
tonique est le procédé de la zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/24-arene/arene.mid --bpm 164`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, le crochet pointé | B4..B6 | 72 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | E3..A4 | 109 | 94 % |
| 2 | **gauche** | bourdon de mi (la tonique) | E2 | 7 | 100 % |
| 3 | **droite** | arpège de la marche, et les trois réponses | A3..F♯5 | 143 | 92 % |
| 4 | droite | basse, quatre noires martelées | G2..B3 | 106 | 94 % |
| 5 | **droite** | **batterie** — 47 grosse caisse, 26 charleston, 22 caisse claire, 3 toms, 1 cymbale | bruit | 99 | 11 % |

`OK — 6 voix employées, stéréo 59/41, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/24-arene
python3 arene.py
python3 ../../../midi_to_mb.py arene.mid ARENA.MB.BIN \
    --bpm 164 --max 2304 --wav ARENE.wav
```
