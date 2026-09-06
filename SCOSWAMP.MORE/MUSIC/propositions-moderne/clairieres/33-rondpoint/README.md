# Clairière 33 — Le large rond-point, la clairière de départ (`hub` 058)

**`ROUNDABOUT.MB.BIN` — 2 219 octets, 48,9 s, boucle, avec batterie.**

## Ce que la clairière raconte

C'est **la première clairière du Marais** : le joueur y arrive page 195, et tout
le reste de l'aventure part d'ici.

| Page | Ce qu'on y lit |
| ---: | --- |
| **195** | « il ne s'agit que d'un large rond-point d'où partent trois sentiers. Le sol est instable et détrempé, de grosses nuées d'insectes volètent au-dessus des mares stagnantes. Le brouillard humide monte en volutes. Les arbres rabougris semblent tordus, comme marqués par la corruption du marais. » |
| 024 | le Feu Follet qui danse devant vous, le trou rempli de vase, la tromperie |
| 058 | le passage prudent : une racine, une pierre, −1 ENDURANCE — puis ouest, est ou retour au sud |
| 404 | l'autre côté atteint sain et sauf, trois directions vers l'inconnu |
| 405 | la chute dans la vase, −1 HABILETÉ, et les mêmes trois directions |

La page 208 (retour vers le sud, sortie du Marais) porte la musique de
`village`, pas celle-ci.

Zone de référence : **`sud`** (`SOUTHSWAMP.MB`, *Sentiers Verts*).

## La pièce

| | |
| --- | --- |
| Titre | **Le Cœur du Marais** |
| Source | composition originale, `rondpoint.py` (ce dossier) |
| Licence | GPL v3, comme le reste du dépôt |
| Caractère | le thème du Marais lui-même : large, sans hâte — c'est la première chose que le joueur entend en entrant, et la dernière avant de ressortir |
| Mode | **ré éolien** (ré mi fa sol la **si♭** do) — la tonalité exacte de la zone |
| Tempo | **158** à la noire (inchangé) |
| Forme | intro (4) — A (8) — B (8) — A' à l'octave (8) — coda (4) |
| Durée | 32 mesures à 4/4 = **48,9 s** |
| Taille | **2 219 octets** (tampon de zone : 2 304) |
| Notes | 472 hauteurs + **101 coups de batterie**, **0 abandonnée** |

C'est la plus longue des onze, et la seule à porter une **coda** en plus des
quatre sections : elle est le thème du lieu, pas celui d'un incident. Elle prend
de `sud` la tonique **et** le procédé — la marche i-VI-III-VII posée sur un
bourdon de ré qui ne bouge **jamais**, pas même sous l'accord majeur de la fin.

**Ce que la révision change.**

* **La montée de trois notes est devenue le crochet de toute la pièce**, plus
  seulement de la partie B. `ré · mi · fa` ouvre A (mesure 5), la relance
  (mesure 9), monte sur sol puis sur si♭ dans le B (mesures 14 et 18 — les trois
  sentiers de la page 195), revient à l'octave en A' (mesure 21), et c'est elle
  que l'arpège renvoie en réponse. **Sept énoncés, jamais deux fois au même
  degré.**
* **La réponse est le thème.** Mesures 8, 12 et 16, le chant tient une ronde et
  le sentier d'en face lui rend la montée, à droite. C'est la seule des onze où
  la réponse est littéralement le thème.
* **La batterie est le pas du voyageur.** Rien pendant six mesures : on écoute
  d'abord. Puis la grosse caisse au premier temps et la caisse claire au
  troisième — une marche régulière, jamais une danse. Elle s'épaissit en B et en
  A', et la **dernière mesure ne contient plus que deux pas**, seuls, pour que la
  boucle reparte sur eux.
* **Une vraie partie B** (mesures 13-20) : le registre monte d'une octave et
  l'harmonie s'installe sur si♭ et fa avant de redescendre par la mineur.
* **Le rythme harmonique varie** : un accord tenu quatre mesures à l'intro, deux
  par mesure dès la mesure 6, un seul de nouveau dans la coda.
* **La surprise** : mesure 31, **ré majeur**. Un fa♯, un seul, le seul de toute
  la pièce — la trouée de ciel au-dessus du rond-point. La mesure suivante le
  reprend : le Marais se referme et la boucle repart en mineur.
* **L'arc** : deux notes d'arpège par mesure à l'intro, huit en B et en A', deux
  de nouveau à la dernière. La pièce s'ouvre et se referme sur le même vide.

## Les six voix (mesurées par `verifier.py`)

Avec une batterie, la voix 5 devient le canal de bruit : il ne reste que **cinq**
voix de hauteur, et le bourdon a migré de la voix 5 (droite) à la voix 2
(gauche). C'est le lit d'accords tenus qui a cédé sa place.

| voix | côté | rôle | registre | notes |
| ---: | :---: | --- | --- | ---: |
| 0 | **gauche** | mélodie — la montée ré-mi-fa | D5..A6 | 80 |
| 1 | gauche | contre-chant | A3..A4 | 94 |
| 2 | **gauche** | bourdon de ré, une seule note tenue, jamais déplacée | D2 | 1 |
| 3 | **droite** | l'arpège, et les trois montées de réponse | A3..D5 | 149 |
| 4 | droite | basse | E2..G3 | 148 |
| 5 | **droite** | **BATTERIE** — le pas : charleston fermé 40, grosse caisse 34, caisse claire 24, cymbale 3 | bruit | 101 |

Les registres se recouvrent d'une voix à l'autre : c'est le lecteur qui attribue,
et à chaque articulation la basse et le contre-chant peuvent s'échanger un instant
leur puce. `verifier.py` conclut `OK` — aucune note abandonnée, six voix employées,
stéréo 60/40.

## Régénérer

```sh
cd SCOSWAMP.MORE/MUSIC/propositions-moderne/clairieres/33-rondpoint
python3 rondpoint.py
python3 ../../../midi_to_mb.py rondpoint.mid ROUNDABOUT.MB.BIN \
    --bpm 158 --max 2304 --wav RONDPOINT.wav
```
