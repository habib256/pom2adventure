# Clairière 17 — La brume fétide

**`MIST.MB.BIN` — 1 399 octets, 41,5 s, boucle.**

## La clairière

| | |
| --- | --- |
| `hub` | **094** |
| Pages | 094 |
| Case | (1,4) |
| Zone de référence | `sud` (`SOUTHSWAMP.MB`) |
| Sorties | N → 295 (la Rivière Croupie), S → 320 (la Licorne) |
| Effet | `E ENDURANCE -2` — on la traverse toujours, on la paie toujours |

« Le sentier descend et des tourbillons de brume vous entourent. Une odeur
infecte emplit l'air et vous retenez votre souffle. Mais bientôt, force vous est
de respirer de nouveau. »

## La pièce

| | |
| --- | --- |
| Titre | **La Brume Fétide** |
| Source | composition originale, `brume.py` |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | la plus lourde des douze, et la plus lente autorisée |
| Mode | **do éolien** (do ré mi♭ fa sol la♭ si♭) |
| Tempo | **128** à la noire — inchangé, on ne court pas dans une odeur pareille |
| Forme | intro (4) — A (6) la descente — B (6) l'odeur — A' (6) la brume se referme |
| Durée | 22 mesures à 4/4 = **41,5 s** |
| Taille | **1 399 octets** — la plus petite des douze (tampon de zone : 2 304) |
| Notes | 312 de hauteur + **36 coups de batterie**, **0 abandonnée** |

**Ce qu'elle garde de la zone `sud` :** le mode éolien et le **bourdon de
tonique immobile**, ici sur do et pris tout en bas du clavier.

**Ce qui lui appartient :** la **descente**. La page commence par « le sentier
descend », et la pièce descend en effet, du do aigu jusqu'au do grave.

## Ce que la révision a changé

- **un crochet qui *est* la descente** : do - si♭ - la♭ . sol | fa . do. Quatre
  notes qui tombent, deux qui se posent. Mesure 5, mesure 9 avec une autre
  chute, redit tel quel mesure 18 ;
- **une réponse** : mesures 7, 12 et 14, le chant tient une ronde et l'arpège —
  la voix 3, à **droite** — laisse retomber la même descente une octave plus
  bas. C'est la brume qui répond au marcheur ;
- **un rythme harmonique varié** : sept mesures changent d'accord au milieu, les
  deux mesures de ré bémol n'en changent plus du tout ;
- **la surprise**, et c'est la seule chose qui arrive dans cette clairière :
  mesures 15-16, un **ré bémol majeur**, le second degré abaissé — le demi-ton
  phrygien de la zone `danger`, cité ici à découvert. Il frotte le **do du
  bourdon** d'un demi-ton entier, deux mesures durant, pendant que le chant fait
  battre ré♭ contre do. C'est l'odeur, et c'est le point d'ENDURANCE. **La
  batterie s'y tait** ;
- **une cadence affirmée** : mesure 17, un **sol majeur** avec son si naturel, la
  seule sensible du morceau ;
- **un arc de densité** : intro sans batterie, A un cœur lent, B qui se serre,
  deux mesures muettes, A' pleine ;
- **une fin qui prépare la boucle** : la dernière mesure retombe sur le **do** du
  début, et le sentier redescend.

## La batterie

Un **cœur qui bat sourd**, jamais une marche — 36 coups en tout, la batterie la
plus économe des onze qui en ont une (108 octets). Grosse caisse au premier
temps ; un tom au troisième une mesure sur deux en A ; toutes les mesures en B ;
**rien** sur le ré bémol ; caisse claire et grosse caisse sur la croche finale
en A', avec une cymbale à la reprise.

Elle prend la **voix 5, à droite** : cinq parties de hauteur, et c'est la voix
d'accords tenus qui a cédé la place — le bourdon de tonique est le procédé de la
zone `sud`.

## Les six voix, mesurées

`python3 ../../verifier.py clairieres/17-brume/brume.mid --bpm 128`

| voix | côté | rôle | registre | notes | occupation |
| ---: | :---: | --- | --- | ---: | ---: |
| 0 | **gauche** | mélodie, la descente | G♯4..C6 | 56 | 96 % |
| 1 | gauche | médiane : le contre-chant, et l'arpège quand il passe sous lui | F3..G♯4 | 93 | 93 % |
| 2 | **gauche** | bourdon de do (la tonique) | C2 | 6 | 100 % |
| 3 | **droite** | arpège, les tourbillons, et les trois réponses | G♯3..C5 | 98 | 93 % |
| 4 | droite | basse, deux blanches | G2..A♯3 | 59 | 96 % |
| 5 | **droite** | **batterie** — 22 grosse caisse, 7 toms, 6 caisse claire, 1 cymbale | bruit | 36 | 5 % |

`OK — 6 voix employées, stéréo 60/40, aucune note abandonnée.`

## Refabriquer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/17-brume
python3 brume.py
python3 ../../../midi_to_mb.py brume.mid MIST.MB.BIN \
    --bpm 128 --max 2304 --wav BRUME.wav
```
